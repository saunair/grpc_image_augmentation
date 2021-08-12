from concurrent import futures

from grpc import server
from fire import Fire

from image_manipulation.image_pb2 import  NLImageRotateRequest, NLImageService
from image_manipulation.image_pb2_grpc import add_NLImageServiceServicer_to_server, NLImageServiceServicer, NLImageServiceStub, NLImageService
from image_manipulation.communication_utils import NLImageService


class NLImageService(NLImageServiceServicer):
    def MeanFilter(self, request, context):
        return 


def run_service_request():
    server = server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_NLImageServiceServicer_to_server(NLImageService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


def main():
    Fire(run_service_request)
