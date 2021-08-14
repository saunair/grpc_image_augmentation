import os

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

ALLOWED_ROTATIONS = [0, 90, 180, 270]


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

    if rotate not in ALLOWED_ROTATIONS:
        print(f"Rotation request must be in {ALLOWED_ROTATIONS}")
        return False
    
    if not os.path.exists(input):
        print(os.path.exists(input), "tihs!!")
        print(f"{input} doesn't exist. Please provide a valid image path.")
        return False

    ext = os.path.splitext(input)[-1].lower()
    if ext not in [".png", ".jpg", ".jpeg"]:
        print(f"Invalid image file extension {ext} passed to the client for the input image.")
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
    rotate: int = 0, 
    port: str = "50051", 
    host: str = "localhost",
    # Using a python keyword "input" here. But keeping the requirements of the assignment.
    input: str = "/home/saurabh/image.jpg", 
    output: str = "/home/saurabh/WabaLabaDubDub.jpeg"
) -> None:
    """
    Args:
        mean: Set to true if a mean filter needs to be applied on the input image.
        rotate: Anticlockwise rotation in degrees to rotate the image.
        port: Port of the server the client needs to communicate to. 
        host: The host-name of the server. 
    """
    if not check_and_print_if_valid_inputs(
        mean=mean,
        rotate=rotate,
        input=input,
        output=output,
    ):
        return

    # We want an option to run both. Hence we'll do it sequentially if the user requests for it. 
    channel = grpc.insecure_channel(f"{host}:{port}", compression=grpc.Compression.Gzip)
    input_image = cv2.imread(input)
    output_image = run_one_request_on_channel(
        mean=mean, 
        rotate=rotate, 
        channel=channel,
        input_image=input_image,
    )
    
    # Hooray, we now write the image to the user's preferred location.
    cv2.imwrite(img=output_image, filename=output)


def main():
    Fire(run_client)
