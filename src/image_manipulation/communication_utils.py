"""All the server and client API is written here."""
import sys
import time
import contextlib
import datetime
from concurrent import futures
import socket
import logging
import multiprocessing
import grpc

import numpy as np
import cv2

from image_manipulation.image_pb2 import (
    NLImageRotateRequest, 
    NLImage, 
)
from image_manipulation.image_pb2_grpc import add_NLImageServiceServicer_to_server, NLImageServiceServicer, NLImageServiceStub
from image_manipulation.image_utils import (
    get_mean_image, 
    convert_proto_to_image, 
    convert_image_to_proto, 
    get_rotated_image, 
    NullImageProto, 
    NLGRPCException
)


LOG = logging.getLogger(__name__)


class ImageService(NLImageServiceServicer):
    """An implementation of a GRPC request to either get the mean or rotation of an image. 
    """

    def MeanFilter(self, request: NLImage, context) -> NLImage:
        """Run the mean filter on the protobuf `request`.

        Args:
            request: The request containing the image that needs to be averaged.

        Returns:
            The protobuf containing the rotated image.

        """
        try:
            user_image_pb = convert_proto_to_image(request)
            mean_image_matrix = get_mean_image(user_image_pb)
            return convert_image_to_proto(mean_image_matrix)
        except:
            e = sys.exc_info()[0]
            # Handling all types of exception as we don't have an exact control over the input.
            return NullImageProto(
                msg=bytes(
                    f"Microservice code for mean-filter threw an exception: {str(e)}", 'utf-8'
                )
            )

    def RotateImage(self, request: NLImageRotateRequest, context) -> NLImage:
        """Run the mean filter on the protobuf `request`.

        Args:
            request: The request containing the image and the rotation requested.
        
        Returns:
            The protobuf containing the rotated image.

        """
        try:
            user_image_pb = convert_proto_to_image(request.image)
            rotated_image_matrix = get_rotated_image(
                input_image=user_image_pb, 
                rotation_request=request.rotation * 90
            )
            return convert_image_to_proto(rotated_image_matrix)
        except Exception as e:
            # Handling all types of exception as we don't have an exact control over the input.
            return NullImageProto(msg=format(e))


def run_one_request_on_channel(
    mean: bool, 
    rotate: int, 
    channel, 
    input_image: np.ndarray
) -> np.ndarray or None:
    """Run one request on an already opened channel
    
    Args:
        mean: Set to true if a mean filter needs to be applied on the input image.
        rotate: Anticlockwise rotation in degrees to rotate the image.
        channel: the channel on which the the server is listening to.
        input_image: The user's image that needs to be manipulated. 

    Returns:
        output_image: The output image that is requested by the user.

    Raises:
        NLGRPCException: If the data passed to the server is invalid or some error occured at the server side. 
        
    """
    ALLOWED_ROTATIONS = [0, 90, 180, 270]
    output_image = None
    input_image = input_image.astype(np.uint8)
    if mean: 
        stub = NLImageServiceStub(channel)
        response = stub.MeanFilter(convert_image_to_proto(input_image))
        # If the image was invalid or so, the server returns a Null image with exception in the message.
        if response.width == 0:
            raise NLGRPCException(response.data.decode("utf-8"))
        output_image = convert_proto_to_image(response)

    if rotate in ALLOWED_ROTATIONS[1:]: # We don't check for zero rotations.
        # We'd like to apply the rotation on the averaged image if rotation is requested.
        # Otherwise we'll read the image from the local directory.
        input_image = input_image if output_image is None else output_image
        stub = NLImageServiceStub(channel)
        response = stub.RotateImage(
            NLImageRotateRequest(
                rotation=ALLOWED_ROTATIONS.index(rotate), 
                image=convert_image_to_proto(input_image)
            )
        )

        # If the image was invalid or so, the server returns a Null image with exception in the message.
        if response.width == 0:
            raise NLGRPCException(response.data.decode("utf-8"))
        output_image = convert_proto_to_image(response)

    return output_image


def _wait_forever(server):
    """Make a process running the server wait forever until a keyboard interrupt is passed."""
    try:
        while True:
            time.sleep(datetime.timedelta(days=1).total_seconds())
    except KeyboardInterrupt:
        server.stop(None)


@contextlib.contextmanager
def _reserve_port():
    """Find and reserve a port for all subprocesses to use."""
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    if sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT) == 0:
        raise RuntimeError("Failed to set SO_REUSEPORT.")
    sock.bind(('', 0))
    try:
        yield sock.getsockname()[1]
    finally:
        sock.close()


def _run_servers_one_process(
    bind_address: str,
    max_workers_per_process: int
) -> None:
    """Start a server on one python process.  

    Args:
        bind_address: The address at which the server listens to.
        max_workers_per_process: The number of process threads running on each process.

    """
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=max_workers_per_process), 
        compression=grpc.Compression.Gzip,
        options=(
            ('grpc.max_send_message_length', 1024 * 1024 * 50),
            ('grpc.max_receive_message_length', 1024 * 1024 * 50),
        )
    )
    add_NLImageServiceServicer_to_server(ImageService(), server)
    server.add_insecure_port(bind_address)
    server.start()
    _wait_forever(server)


def spawn_server(
    port: int = 50051, 
    host: str = "localhost", 
    max_workers_per_process: int = 8, 
    number_of_cores_to_use: int = 4
) -> None:
    """Run one server request.
    
    Args:
        port: The port at which this server will run 
        host: The hostname of this server 
        max_workers_per_process: Maximum number of threads that will run on one process (one core of the processor).
        number_of_cores_use: Number of cores to be used.

    """
    # Set up some logging for debugging offline.
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[PID %(process)d] %(message)s")
    handler.setFormatter(formatter)
    LOG.addHandler(handler)
    LOG.setLevel(logging.DEBUG)
    
    bind_address = f"{host}:{port}"
    LOG.info(f"Binding to {bind_address}")
    sys.stdout.flush()
    workers = []
    for process_number in range(number_of_cores_to_use):
        worker = multiprocessing.Process(
            target=_run_servers_one_process,
            args=(bind_address, max_workers_per_process)
        )
        LOG.info(f"Started process number: {process_number}")
        worker.start()
        workers.append(worker)
    for worker in workers:
        worker.join()


