from image_manipulation.image_pb2 import  NLImageRotateRequest
from image_manipulation.image_pb2_grpc import NLImageServiceServicer
from image_manipulation.image_utils import (
    get_mean_image, 
    convert_proto_to_image, 
    convert_image_to_proto, 
    get_rotated_image
)


class ImageService(NLImageServiceServicer):
    def MeanFilter(self, request, context):
        user_image_pb = convert_proto_to_image(request)
        mean_image_matrix = get_mean_image(user_image_pb)
        return convert_image_to_proto(mean_image_matrix)

    def RotateImage(self, request, context):
        user_image_pb = convert_proto_to_image(request.image)
        rotated_image_matrix = get_rotated_image(
            input_image=user_image_pb, 
            rotation_request=request.rotation * 90
        )
        return convert_image_to_proto(rotated_image_matrix)
