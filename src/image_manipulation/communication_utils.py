from image_manipulation.image_pb2 import  NLImageRotateRequest, NLImage
from image_manipulation.image_pb2_grpc import NLImageServiceServicer
from image_manipulation.image_utils import (
    get_mean_image, 
    convert_proto_to_image, 
    convert_image_to_proto, 
    get_rotated_image
)


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
        user_image_pb = convert_proto_to_image(request)
        mean_image_matrix = get_mean_image(user_image_pb)
        return convert_image_to_proto(mean_image_matrix)

    def RotateImage(self, request: NLImageRotateRequest, context) -> NLImage:
        """Run the mean filter on the protobuf `request`.

        Args:
            request: The request containing the image and the rotation requested.
        
        Returns:
            The protobuf containing the rotated image.

        """
        user_image_pb = convert_proto_to_image(request.image)
        rotated_image_matrix = get_rotated_image(
            input_image=user_image_pb, 
            rotation_request=request.rotation * 90
        )
        return convert_image_to_proto(rotated_image_matrix)
