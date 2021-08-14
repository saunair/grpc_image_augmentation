from concurrent import futures
import logging
import contextlib
import sys
import multiprocessing
import socket
import time
import datetime

import grpc
from fire import Fire

from image_manipulation.communication_utils import ImageService
from image_manipulation.image_pb2_grpc import add_NLImageServiceServicer_to_server 
_ONE_DAY = datetime.timedelta(days=1)


_LOGGER = logging.getLogger(__name__)


def wait_forever(server):
    try:
        while True:
            time.sleep(_ONE_DAY.total_seconds())
    except KeyboardInterrupt:
        server.stop(None)


@contextlib.contextmanager
def reserve_port():
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


def run_servers_one_process(
    bind_address, 
    max_workers_per_process
):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers_per_process), compression=grpc.Compression.Gzip)
    add_NLImageServiceServicer_to_server(ImageService(), server)
    server.add_insecure_port(bind_address)
    server.start()
    wait_forever(server)


def spawn_server(
    port: int = 50051, 
    host: str = "localhost", 
    max_workers_per_process: int = 10, 
    number_of_cores_to_use: int = 3
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
    _LOGGER.addHandler(handler)
    _LOGGER.setLevel(logging.DEBUG)
    
    bind_address = f"{host}:{port}"
    _LOGGER.info(f"Binding to {bind_address}")
    sys.stdout.flush()
    workers = []
    for _ in range(number_of_cores_to_use):
        # NOTE: It is imperative that the worker subprocesses be forked before
        # any gRPC servers start up. See
        # https://github.com/grpc/grpc/issues/16001 for more details.
        worker = multiprocessing.Process(
            target=run_servers_one_process,
            args=(bind_address, max_workers_per_process)
        )
        worker.start()
        workers.append(worker)
    for worker in workers:
        worker.join()


def main():
    Fire(spawn_server)
