from django.test import TestCase

from ..boorutils import *

class HashStrTest(TestCase):
    def test_hash_str(self):
        self.assertEqual(hash_str("test"), "098f6bcd4621d373cade4e832627b4f6")

class GetContentDimensionsTest(TestCase):
    def test_get_content_dimensions_image(self):
        self.assertEqual(get_content_dimensions("assets/TEST_DATA/content/felix.jpg"), (500, 688))

    def test_get_content_dimensions_video(self):
        self.assertEqual(get_content_dimensions("assets/TEST_DATA/content/ana_cat.mp4"), (928, 1904))