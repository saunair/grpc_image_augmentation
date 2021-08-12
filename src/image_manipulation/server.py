from concurrent import futures

import grpc
from fire import Fire

from .image_pb2_grpc import add_NLImageServiceServicer_to_server 
from image_manipulation.communication_utils import ImageService


def run_service_request():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_NLImageServiceServicer_to_server(ImageService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


def main():
    Fire(run_service_request)
