import os
import logging
import time
import multiprocessing

import cv2
from fire import Fire
import grpc
import numpy as np

from image_manipulation import image_pb2_grpc, image_pb2
from image_manipulation.image_utils import (
    convert_proto_to_image, 
    convert_image_to_proto,
    NLGRPCException
)
from image_manipulation.communication_utils import run_one_request_on_channel


LOG = logging.getLogger(__name__)


ALLOWED_ROTATIONS = ["none", "ninety_deg", "one_eighty_deg", "two_seventy_deg"]
SUPPORTED_IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"]


def check_and_print_if_valid_inputs(
    output: str,
    input: str, 
    mean: bool, 
    rotate: float, 
):
    """Check if the inputs provided by the user are supported

    Args:
        mean: Set to true if a mean filter needs to be applied on the input image.
        rotate: Anticlockwise rotation in degrees to rotate the image.
        input: Path to the input image
        output: Path to the output image.
    
    Returns:
        valid: True if all the inputs are valid.

    """
    if not mean and np.isclose(rotate, 0.0):
        print("No action input provided, either send mean as True or a rotation that is valid.")
        return False

    rotate = rotate.lower()
    if rotate not in ALLOWED_ROTATIONS:
        print(f"Rotation request must be in {ALLOWED_ROTATIONS}")
        return False
    
    if not os.path.exists(input):
        print(f"{input} doesn't exist. Please provide a valid image path.")
        return False

    ext = os.path.splitext(input)[-1].lower()
    if ext not in SUPPORTED_IMAGE_EXTENSIONS:
        print(f"Please provide a valid image extension within {SUPPORTED_IMAGE_EXTENSIONS} and not {ext}")
        return False
    
    if not os.path.exists(os.path.dirname(output)):
        print(f"{output} doesn't exist. Please provide a valid image path.")
        return False
    ext = os.path.splitext(output)[-1].lower()
    if ext not in [".png", ".jpg", ".jpeg"]:
        print(f"Invalid image file extension {ext} passed to the client for the output path.")
        return False

    return True


def run_client(
    mean:bool = False, 
    rotate: str = "NINETY_DEG", 
    port: str = "50051", 
    host: str = "localhost",
    # Using a python keyword "input" here. But keeping the requirements of the assignment.
    input: str = "/home/saurabh/image.jpg", 
    output: str = "/home/saurabh/WabaLabaDubDub.jpeg",
    timeit: bool = False,
) -> None:
    """
    Args:
        mean: Set to true if a mean filter needs to be applied on the input image.
        rotate: Anticlockwise rotation in degrees to rotate the image.
        port: Port of the server the client needs to communicate to. 
        host: The host-name of the server. 
        input: The directory of the input image.
        output: The directory of the output image.
        timeit: Set to true if the response time over a folder `input` of images need to be saved.

    """

    # We want an option to run both. Hence we'll do it sequentially if the user requests for it. 
    channel = grpc.insecure_channel(f"{host}:{port}", compression=grpc.Compression.Gzip, options=[
            ('grpc.max_send_message_length', 1024 * 1024 * 50),
            ('grpc.max_receive_message_length', 1024 * 1024 * 50),
        ]
    )
    if not timeit: # The original mode of the client as per the assignment.
        if not check_and_print_if_valid_inputs(
            mean=mean,
            rotate=rotate,
            input=input,
            output=output,
        ):
            return
        try:
            input_image = cv2.imread(input)
        except:
            LOG.error(f"Something went wrong while reading the input image: {input}")
            return
        if input_image is None:
            LOG.error(f"Something went wrong while reading the input image: {input}")
            return
        
        # Convert the rotation command passed to lower as it is easier for us to assess.
        rotate = rotate.lower()

        output_image = run_one_request_on_channel(
            mean=mean, 
            rotate=rotate * 90, 
            channel=channel,
            input_image=input_image,
        ) 
        # Hooray, we now write the image to the user's preferred location.  
        cv2.imwrite(img=output_image, filename=output) 
    else:
        # Run the scaling testing mode with multiple client requests to send to the server.
        rotate = rotate.lower()

        def _image_manipulation_thread(image_extension_option, filename):
            if filename.endswith(image_extension_option):
                image_file_path = os.path.join(input, filename)
                try:
                    input_image = cv2.imread(image_file_path)
                except:
                    LOG.error(f"something went wrong while reading the input image: {image_file_path}")
                    return
                if input_image is None:
                    LOG.error(f"something went wrong while reading the input image: {image_file_path}")
                    return

                output_image = run_one_request_on_channel(
                    mean=mean, 
                    rotate=ALLOWED_ROTATIONS.index(rotate) * 90, 
                    channel=channel,
                    input_image=input_image,
                )
    
                # Hooray, we now write the image to the user's preferred location.
                output_image_file_path = os.path.join(output, f"manipulated_{filename}")
                cv2.imwrite(img=output_image, filename=output_image_file_path)

        workers = []
        start_time = time.time()
        for filename in os.listdir(input):
            for image_extension_option in SUPPORTED_IMAGE_EXTENSIONS:
                worker = multiprocessing.Process(
                    target=_image_manipulation_thread, args=(image_extension_option, filename)
                )
                worker.start()
                workers.append(worker)

        for worker in workers:
            worker.join()

        print(f"Response time: {time.time() - start_time}")


def main():
    Fire(run_client)
