import time
import threading

import cv2
import numpy as np
from image_manipulation.image_pb2 import NLImage
from numba import uint8, jit


class NLGRPCException(Exception):
    """A class to handle server exceptions on the client side."""
    def __init__(self, message):
        self.message = message


def NullImageProto(msg:str = ""):
    """A null image to return if something goes wrong
    
    Args: 
        msg: Optional message to be used to know what exception happened on the server side

    Returns:
        A null proto buf image representation.

    """
    return NLImage(width=0, height=0, data=msg)


AVERAGING_KERNEL = np.ones((3,3), np.float32) / 9

# This function is not working the way it should be, hence sticking to the opencv version.
def get_mean_image(input_image: np.ndarray) -> np.ndarray:
    """Run an averaging filter over `input_image`.

    Args:
        input_image: The image provided by the user. Can be greyscale or RGB.

    Returns:
        The blurred image.

    """
    input_image = input_image.astype(np.uint8)
    @jit(uint8[:,:](uint8[:,:]))
    def filter_2d(image):
        M, N = image.shape
        Mf, Nf = 3, 3
        result = np.zeros_like(image, dtype=image.dtype)
        for i in range(M):
            for j in range(N):
                num = 0.0
                count = 0
                for ii in range(Mf):
                    for jj in range(Nf):
                        row_index = i- 1 + ii
                        column_index = j - 1 + jj
                        if row_index < 0 or row_index >= M or column_index < 0 or column_index >= N:
                            continue
                        num += image[row_index, column_index]
                        count += 1
                result[i, j] = num / count
        return result

    # If an RGB image run the filter thrice.
    if len(input_image.shape) > 2:
        result = np.empty(input_image.shape, dtype=input_image.dtype)
        def set_result(input_image, depth, result):
            result[:, :, depth] = filter_2d(input_image[:, :, depth])
        threads = []

        for depth in range(3):
            current_thread = threading.Thread(target=set_result, args=(input_image, depth, result))
            current_thread.setDaemon(True)
            current_thread.start()
            threads.append(current_thread)

        for t in threads:
            t.join()
        return result

    a = filter_2d(input_image)
    return a


def get_rotated_image(
    input_image: np.ndarray,
    rotation_request: int  # Currently setting to an int as the possible rotations are fixed.
) -> np.ndarray:
    """Get a rotated image around the center.

    This API is copied from the image utils convenience functions.

    Args:
        input_image: The image that the user provided.
        rotation_request: Anticlockwise rotation in degrees to rotate the image.

    Returns:
        The rotated image around the center of the original image.

    """
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = input_image.shape[:2]
    (cX, cY) = (w / 2, h / 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -rotation_request, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(input_image, M, (nW, nH))


def convert_image_to_proto(image: np.ndarray) -> NLImage:
    """Convert a numpy `image` to a protobuf message."""
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

