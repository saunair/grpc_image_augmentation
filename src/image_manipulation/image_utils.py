import numpy as np
from imutils import rotate_bound as imrotate
from image_manipulation.image_pb2 import NLImage
from numba import double, jit


class NLGRPCException(Exception):
    """A class to handle server exceptions on the client side."""
    def __init__(self, message):
        self.message = message

AVERAGING_KERNEL = np.ones((3,3), np.float32) / 9


def NullImageProto(msg:str = ""):
    """A null image to return if something goes wrong
    
    Args: 
        msg: Optional message to be used to know what exception happened on the server side

    Returns:
        A null proto buf image representation.

    """
    return NLImage(width=0, height=0, data=msg)


def get_mean_image(input_image: np.ndarray) -> np.ndarray:
    """Run an averaging filter over `input_image`.
    
    Args:
        input_image: The image provided by the user. Can be greyscale or RGB.

    Returns: 
        The blurred image.
    
    """
    #@jit(nopython=True)
    def fastfilter_2d(image, kernel):
        M, N = image.shape
        Mf, Nf = kernel.shape
        Mf2 = Mf // 2
        Nf2 = Nf // 2
        result = np.zeros_like(image, dtype=image.dtype)
        for i in range(Mf2, M - Mf2):
            for j in range(Nf2, N - Nf2):
                num = 0.0
                for ii in range(Mf):
                    for jj in range(Nf):
                        num += (kernel[Mf-1-ii, Nf-1-jj] * image[i-Mf2+ii, j-Nf2+jj])
                result[i, j] = num
        return result

    #fastfilter_2d = jit(double[:,:](double[:,:], double[:,:]))(_filter2d)
    
    # If an RGB image run the filter thrice.
    if len(input_image.shape) > 2:
        result = np.empty(input_image.shape, dtype=input_image.dtype)
        result[0, :, :] = fastfilter_2d(input_image[0], kernel=AVERAGING_KERNEL)
        result[1, :, :] = fastfilter_2d(input_image[1], kernel=AVERAGING_KERNEL)
        result[2, :, :] = fastfilter_2d(input_image[2], kernel=AVERAGING_KERNEL)
        return result

    # If grey scale run it only once and return the image.
    return fastfilter_2d(input_image, kernel=AVERAGING_KERNEL)


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

