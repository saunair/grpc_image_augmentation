import cv2
from fire import Fire
import grpc
import numpy as np

from image_manipulation import image_pb2_grpc, image_pb2
from image_manipulation.image_utils import (
    convert_proto_to_image, 
    convert_image_to_proto, 
)

ALLOWED_ROTATIONS = [0, 90, 180, 270]


def run_client(
    mean:bool = False, 
    rotate: float = 0.0, 
    port: str = "50051", 
    host: str = "localhost",
    input_dir: str = "/home/saurabh/coding/grpc_image_project/20210802-neuralink-image-service-prompt/image_manipulation/test_images/show_me_what_youve_got.jpg",
    output_dir: str = "/home/saurabh/wabalabadubdub.jpg"
) -> None:
    """
    Args:
        mean: Set to true if a mean filter needs to be applied on the input image.
        rotate: Anticlockwise rotation in degrees to rotate the image.
        port: Port of the server the client needs to communicate to. 
        host: The host-name of the server. 
    """
    if not mean and np.isclose(rotate, 0.0):
        print("No action input provided, either send mean as True or a rotation that is valid.")

    if rotate not in ALLOWED_ROTATIONS:
        raise ValueError(f"Rotation request must be in {ALLOWED_ROTATIONS}")

    # We want an option to run both. Hence we'll do it sequentially if the user requests for it. 
    output_image = None
    if mean: 
        with grpc.insecure_channel(f"{host}:{port}") as channel:
            user_image = cv2.imread(input_dir)
            stub = image_pb2_grpc.NLImageServiceStub(channel)
            response = stub.MeanFilter(convert_image_to_proto(user_image))
            output_image = convert_proto_to_image(response)

    if rotate in ALLOWED_ROTATIONS[1:]: # We don't check for zero rotations.
        with grpc.insecure_channel(f"{host}:{port}") as channel:
            # We'd like to apply the rotation on the averaged image if rotation is requested.
            # Otherwise we'll read the image from the local directory.
            user_image = cv2.imread(input_dir) if output_image is None else output_image
            stub = image_pb2_grpc.NLImageServiceStub(channel)
            response = stub.RotateImage(
                image_pb2.NLImageRotateRequest(
                    rotation=ALLOWED_ROTATIONS.index(rotate), 
                    image=convert_image_to_proto(user_image)
                )
            )
            output_image = convert_proto_to_image(response)
    
    # Hooray, we now write the image to the user's preferred location.
    cv2.imwrite(img=output_image, filename=output_dir)


def main():
    Fire(run_client)
