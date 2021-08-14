import sys

import numpy as np

from image_manipulation.image_pb2 import  NLImageRotateRequest, NLImage
from image_manipulation.image_pb2_grpc import NLImageServiceServicer
from image_manipulation.image_utils import (
    get_mean_image, 
    convert_proto_to_image, 
    convert_image_to_proto, 
    get_rotated_image, 
    NullImageProto
)
from image_manipulation import image_pb2_grpc, image_pb2


class ImageService(NLImageServiceServicer):
    """An implementation of a GRPC request to either get the mean or rotation of an image. 
    """

    def MeanFilter(self, request: NLImage, context) -> NLImage:
        """Run the mean filter on the protobuf `request`.

        Args:
            request: The request containing the image that needs to be averaged.

        Returns:
            The protobuf containing the rotated image.

        """
        try:
            user_image_pb = convert_proto_to_image(request)
            mean_image_matrix = get_mean_image(user_image_pb)
            return convert_image_to_proto(mean_image_matrix)
        except:
            e = sys.exc_info()[0]
            # Handling all types of exception as we don't have an exact control over the input.
            return NullImageProto(msg=bytes(f"Microservice code for mean-filter threw an exception: {str(e)}", 'utf-8'))

    def RotateImage(self, request: NLImageRotateRequest, context) -> NLImage:
        """Run the mean filter on the protobuf `request`.

        Args:
            request: The request containing the image and the rotation requested.
        
        Returns:
            The protobuf containing the rotated image.

        """
        try:
            user_image_pb = convert_proto_to_image(request.image)
            rotated_image_matrix = get_rotated_image(
                input_image=user_image_pb, 
                rotation_request=request.rotation * 90
            )
            return convert_image_to_proto(rotated_image_matrix)
        except Exception as e:
            # Handling all types of exception as we don't have an exact control over the input.
            return NullImageProto(msg=format(e))


def run_one_request_on_channel(mean: bool, rotate: int, channel, input_image: np.ndarray) -> np.ndarray or None:
    """Run one request on an already opened channel
    
    Args:
        mean: Set to true if a mean filter needs to be applied on the input image.
        rotate: Anticlockwise rotation in degrees to rotate the image.
        channel: the channel on which the the server is listening to.
        input_image: The user's image that needs to be manipulated. 

    Returns:
        output_image: The output image that is requested by the user.

    Raises:
        NLGRPCException: If the data passed to the server is invalid or some error occured at the server side. 
        
    """
    ALLOWED_ROTATIONS = [0, 90, 180, 270]
    output_image = None
    if mean: 
        stub = image_pb2_grpc.NLImageServiceStub(channel)
        response = stub.MeanFilter(convert_image_to_proto(input_image))
        # If the image was invalid or so, the server returns a Null image with exception in the message.
        if response.width == 0:
            raise NLGRPCException(response.data.decode("utf-8"))

        output_image = convert_proto_to_image(response)

    if rotate in ALLOWED_ROTATIONS[1:]: # We don't check for zero rotations.
        # We'd like to apply the rotation on the averaged image if rotation is requested.
        # Otherwise we'll read the image from the local directory.
        input_image = cv2.imread(input) if output_image is None else output_image
        stub = image_pb2_grpc.NLImageServiceStub(channel)
        response = stub.RotateImage(
            image_pb2.NLImageRotateRequest(
                rotation=ALLOWED_ROTATIONS.index(rotate), 
                image=convert_image_to_proto(input_image)
            )
        )

        # If the image was invalid or so, the server returns a Null image with exception in the message.
        if response.width == 0:
            raise NLGRPCException(response.data.decode("utf-8"))

        output_image = convert_proto_to_image(response)
    return output_image


