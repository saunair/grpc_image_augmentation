import numpy as np
import cv2
from mock import Mock
from copy import copy

from image_manipulation.communication_utils import ImageService
from image_manipulation import image_utils


def test_service_object():
    service_object = ImageService()
    # Test an expected case.
    input_image_path = "testing_data/image.png" 
    input_image = cv2.imread(input_image_path)
    valid_image_pb = image_utils.convert_image_to_proto(input_image)

    # Just mocking the context for now as we don't care about where it sends the output to.
    op_pb = service_object.MeanFilter(valid_image_pb, context=Mock())
    assert op_pb.width == 1080
    
    # Check if exception handling works correctly.
    invalid_pb_image = copy(valid_image_pb)
    invalid_pb_image.width = 80
    op_pb = service_object.MeanFilter(invalid_pb_image, context=Mock())
    assert op_pb.width == 0
