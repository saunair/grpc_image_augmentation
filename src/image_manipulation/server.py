from concurrent import futures

import grpc
from fire import Fire

from image_manipulation.communication_utils import ImageService
from image_manipulation.grpc_pb.image_pb2_grpc import add_NLImageServiceServicer_to_server 


def run_service_request(port: int = 50051, host: str = "localhost", max_workers_per_process: int = 10) -> None:
    """Run one server request.
    
    Args:
        port: The port at which this server will run 
        host: The hostname of this server 
        max_workers_per_process: Maximum number of threads that will run on one process (one core of the processor).

    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers_per_process), compression=grpc.Compression.Gzip)
    add_NLImageServiceServicer_to_server(ImageService(), server)
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    server.wait_for_termination()


def main():
    Fire(run_service_request)
