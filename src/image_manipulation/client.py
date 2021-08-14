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
import time


ALLOWED_ROTATIONS = [0, 90, 180, 270]
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
    rotate: int = 0, 
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
    channel = grpc.insecure_channel(f"{host}:{port}", compression=grpc.Compression.Gzip)
    if not timeit: # The original mode of the client.
        if not check_and_print_if_valid_inputs(
            mean=mean,
            rotate=rotate,
            input=input,
            output=output,
        ):
            return
        input_image = cv2.imread(input)
        output_image = run_one_request_on_channel(
            mean=mean, 
            rotate=rotate, 
            channel=channel,
            input_image=input_image,
        )
        # Hooray, we now write the image to the user's preferred location.
        cv2.imwrite(img=output_image, filename=output)
    else:
        response_times = []
        for filename in os.listdir(input):
            for image_extension_option in SUPPORTED_IMAGE_EXTENSIONS:
                if filename.endswith(image_extension_option):
                    image_file_path = os.path.join(input, filename)
                    input_image = cv2.imread(image_file_path)
                    start_time = time.time()
                    output_image = run_one_request_on_channel(
                        mean=mean, 
                        rotate=rotate, 
                        channel=channel,
                        input_image=input_image,
                    )
                    response_times.append(time.time() - start_time)
    
                    # Hooray, we now write the image to the user's preferred location.
                    output_image_file_path = os.path.join(output, f"manipulated_{filename}")
                    print("this", filename)
                    cv2.imwrite(img=output_image, filename=output_image_file_path)
        print(response_times)


def main():
    Fire(run_client)
