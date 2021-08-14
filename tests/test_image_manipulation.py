import numpy as np
import cv2
import os

from image_manipulation import __version__
from image_manipulation import image_utils 


dir_path = os.path.dirname(os.path.realpath(__file__))


def test_version():
    assert __version__ == '0.1.0'


def test_image_manipulations():
    input_image = np.array([[13, 14, 15], [11, 12, 13], [7, 8, 9]], dtype=np.uint8)
    mean_image = image_utils.get_mean_image(input_image)
    expected_mean = np.array(
        [[12, 13, 13],
         [10, 11, 11],
         [ 9, 10, 10]], 
        dtype=np.uint8
    )
    assert np.allclose(mean_image, expected_mean), "The mean function is broken on the mock image"
    rotated_image = image_utils.get_rotated_image(input_image, 90)
    expected_rotated_image = np.array(
        [[ 0,  7, 11],
         [ 0,  8, 12],
         [ 0,  9, 13]], dtype=np.uint8
    )
    assert np.allclose(rotated_image, expected_rotated_image)

    # Now let's try the operations on a real image.
    input_image_path = os.path.join(dir_path, "testing_data/image.png")
    input_image = cv2.imread(input_image_path)
    mean_image = image_utils.get_mean_image(input_image)
    expected_mean_image = cv2.imread(os.path.join(dir_path, "testing_data/mean_image.png"))
    assert np.allclose(mean_image, expected_mean_image, atol=3.0), "Averaging function is broken"
    rotated_image = image_utils.get_rotated_image(input_image, 90)
    expected_rotated_image = cv2.imread(os.path.join(dir_path, "testing_data/rotated_image.png"))
    assert np.allclose(rotated_image, expected_rotated_image), "Rotation function is broken"


def test_convert_image_to_pb_and_back():
    # Test for an RGB image.
    input_image_path = os.path.join(dir_path, "testing_data/image.png")
    input_image = cv2.imread(input_image_path)
    image_pb = image_utils.convert_image_to_proto(input_image)
    recovered_image = image_utils.convert_proto_to_image(image_pb)
    assert np.allclose(recovered_image, input_image, atol=0.0), "Image has been changed."

    # Check if the conversions work fine with a grey scale image
    gray_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    image_pb = image_utils.convert_image_to_proto(gray_image)
    recovered_image = image_utils.convert_proto_to_image(image_pb)
    assert np.allclose(recovered_image, gray_image, atol=0.0), "Image has been changed."
