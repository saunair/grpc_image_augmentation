import numpy as np
import cv2

from image_manipulation import __version__
from image_manipulation import image_utils 


def test_version():
    assert __version__ == '0.1.0'


def test_image_manipulations():
    input_image = np.array([[13, 14, 15], [11, 12, 13], [7, 8, 9]], dtype=np.uint8)
    mean_image = image_utils.get_mean_image(input_image)
    rotated_image = image_utils.get_rotated_image(input_image, 90)
    input_image_path = "testing_data/image.jpg"
    input_image = cv2.imread(input_image_path)
    mean_image = image_utils.get_mean_image(input_image)
    rotated_image = image_utils.get_rotated_image(input_image, 90)


def test_convert_image_to_pb_and_back():
    # Test for an RGB image.
    input_image_path = "testing_data/image.jpg"
    input_image = cv2.imread(input_image_path)
    image_pb = image_utils.convert_image_to_proto(input_image)
    recovered_image = image_utils.convert_proto_to_image(image_pb)
    assert np.allclose(recovered_image, input_image, atol=0.0), "Image has been changed."

    # Check if the conversions work fine with a grey scale image
    gray_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    image_pb = image_utils.convert_image_to_proto(gray_image)
    recovered_image = image_utils.convert_proto_to_image(image_pb)
    assert np.allclose(recovered_image, gray_image, atol=0.0), "Image has been changed."

