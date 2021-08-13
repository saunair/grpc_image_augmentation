from concurrent import futures

import grpc
from fire import Fire

from image_manipulation.communication_utils import ImageService
from image_manipulation.image_pb2_grpc import add_NLImageServiceServicer_to_server 


def run_service_request(port: int = 50051, host: str = "localhost", max_workers_per_process: int = 10) -> None:
    """Run one server request"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers_per_process))
    add_NLImageServiceServicer_to_server(ImageService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


def main():
    Fire(run_service_request)
