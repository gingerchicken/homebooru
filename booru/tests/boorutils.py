from django.test import TestCase

import pathlib

from ..boorutils import *

class HashStrTest(TestCase):
    def test_hash_str(self):
        self.assertEqual(hash_str("test"), "098f6bcd4621d373cade4e832627b4f6")

class GetContentDimensionsTest(TestCase):
    def test_get_content_dimensions_image(self):
        self.assertEqual(get_content_dimensions("assets/TEST_DATA/content/felix.jpg"), (500, 688))

    def test_get_content_dimensions_video(self):
        self.assertEqual(get_content_dimensions("assets/TEST_DATA/content/ana_cat.mp4"), (928, 1904))

class GetFileChecksumTest(TestCase):
    def test_get_file_checksum(self):
        self.assertEqual(get_file_checksum("assets/TEST_DATA/content/felix.jpg"),   "2dcd09f6c874b36355336112d17434e1")
        self.assertEqual(get_file_checksum("assets/TEST_DATA/content/ana_cat.mp4"), "11e0a9c6b20d54593b8fc8f134a25256")

class GenerateThumbnailTest(TestCase):
    original_image = "assets/TEST_DATA/content/felix.jpg"
    output_image   = "/tmp/thumbnail_felix.png"

    def setUp(self):
        if pathlib.Path(self.output_image).exists():
            # Delete it
            pathlib.Path(self.output_image).unlink()

    def test_generates_a_file(self):
        self.assertTrue(generate_thumbnail(self.original_image, self.output_image))

        # Check that the file exists
        self.assertTrue(pathlib.Path(self.output_image).exists())
    
    def test_generates_a_file_with_the_correct_dimensions(self):
        self.assertTrue(generate_thumbnail(self.original_image, self.output_image))

        # Check that the file exists
        self.assertTrue(pathlib.Path(self.output_image).exists())

        # Check that the file has the correct dimensions
        original_dims = get_content_dimensions(self.original_image)
        output_dims = get_content_dimensions(self.output_image)
        
        r = float(150) / float(original_dims[1])
        expected_dims = (int(r * original_dims[0]), 150)

        self.assertEqual(output_dims, expected_dims)
    
    def test_generates_a_file_for_a_video(self):
        self.assertTrue(generate_thumbnail("assets/TEST_DATA/content/ana_cat.mp4", self.output_image))

        # Check that the file exists
        self.assertTrue(pathlib.Path(self.output_image).exists())
    
    def test_generates_a_file_for_a_video_with_the_correct_dimensions(self):
        self.assertTrue(generate_thumbnail("assets/TEST_DATA/content/ana_cat.mp4", self.output_image))

        # Check that the file exists
        self.assertTrue(pathlib.Path(self.output_image).exists())

        # Check that the file has the correct dimensions
        original_dims = get_content_dimensions("assets/TEST_DATA/content/ana_cat.mp4")
        output_dims = get_content_dimensions(self.output_image)

        r = float(150) / float(original_dims[1])
        expected_dims = (int(r * original_dims[0]), 150)

        self.assertEqual(output_dims, expected_dims)
    
    # TODO test for invalid/corrupt files