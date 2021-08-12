import numpy as np
import cv2 as cv
from imutils import rotate_bound as imrotate
from .image_pb2 import NLImage


AVERAGING_KERNEL = np.ones((3,3), np.float32) / 9


def get_mean_image(input_image: np.ndarray) -> np.ndarray:
    """Run an averaging filter over `input_image`.
    
    Args:
        input_image: The image provided by the user. Can be greyscale or RGB.

    Returns: 
        The blurred image.
    
    """
    return cv.filter2D(input_image, -1, kernel=AVERAGING_KERNEL)


def get_rotated_image(
    input_image: np.ndarray, 
    rotation_request: int  # Currently setting to an int as the possible rotations are fixed.
) -> np.ndarray:
    """Get a rotated image around the center. 
    
    Args: 
        input_image: The image that the user provided. 
        rotation_request: Anticlockwise rotation in degrees to rotate the image.
    
    Returns:
        The rotated image around the center of the original image.

    """
    return imrotate(input_image, rotation_request)


def convert_image_to_proto(image: np.ndarray) -> NLImage:
    """Convert a numpy image to a protobuf message."""
    return NLImage(
        color=len(image.shape) > 2, # If the dimensions has a 3rd value which is the channels, it is RGB.
        data=image.flatten().tobytes(),
        width=image.shape[1],
        height=image.shape[0]
    )


def convert_proto_to_image(image_pb: NLImage) -> np.ndarray:
    """Convert an NLImage protobuf message to a numpy image."""
    input_array = np.frombuffer(image_pb.data, dtype=np.uint8)
    dimensions = [image_pb.height, image_pb.width]
    if image_pb.color:
        dimensions.append(3)
    input_image = input_array.reshape(dimensions)
    return input_image

