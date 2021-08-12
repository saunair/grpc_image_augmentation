from image_manipulation.image_pb2 import  NLImageRotateRequest, NLImageService
from fire import Fire
from concurrent import futures
from grpc import server


def run_service_request():
    server = server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()





def main():
    Fire(run_service_request)
