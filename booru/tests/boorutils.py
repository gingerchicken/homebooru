from django.test import TestCase

import pathlib

from ..boorutils import *

import homebooru.settings

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
        expected_dims = (round(r * original_dims[0]), 150)

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
        expected_dims = (round(r * original_dims[0]), 150)

        self.assertEqual(output_dims, expected_dims)

    def test_raises_an_error_if_the_file_does_not_exist(self):
        with self.assertRaises(Exception):
            generate_thumbnail("assets/TEST_DATA/content/does_not_exist.jpg", self.output_image)
        
        # Make sure that there was no output file
        self.assertFalse(pathlib.Path(self.output_image).exists())

    def test_raises_an_error_if_file_corrupted(self):
        with self.assertRaises(Exception):
            generate_thumbnail("assets/TEST_DATA/content/corrupted_image.jpg", self.output_image)

        # Make sure that there was no output file
        self.assertFalse(pathlib.Path(self.output_image).exists())

class GenerateSampleTest(TestCase):
    original_image = "assets/TEST_DATA/content/sampleable_image.jpg"
    output_image   = "/tmp/sampled.png"

    def setUp(self):
        if pathlib.Path(self.output_image).exists():
            # Delete it
            pathlib.Path(self.output_image).unlink()
    
    def test_generates_a_file(self):
        self.assertTrue(generate_sample(self.original_image, self.output_image))

        # Check that the file exists
        self.assertTrue(pathlib.Path(self.output_image).exists())
    
    def test_generates_a_file_with_the_correct_dimensions(self):
        self.assertTrue(generate_sample(self.original_image, self.output_image))

        # Check that the file exists
        self.assertTrue(pathlib.Path(self.output_image).exists())

        # Check that the file has the correct dimensions
        original_dims = get_content_dimensions(self.original_image)
        output_dims = get_content_dimensions(self.output_image)
        
        r = float(850) / float(original_dims[0])
        expected_dims = (850, round(r * original_dims[1]))

        self.assertEqual(output_dims, expected_dims)
    
    def test_generates_a_file_for_a_video(self):
        self.assertTrue(generate_sample("assets/TEST_DATA/content/ana_cat.mp4", self.output_image))

        # Check that the file exists
        self.assertTrue(pathlib.Path(self.output_image).exists())
    
    def test_generates_a_file_for_a_video_with_the_correct_dimensions(self):
        self.assertTrue(generate_sample("assets/TEST_DATA/content/ana_cat.mp4", self.output_image))

        # Check that the file exists
        self.assertTrue(pathlib.Path(self.output_image).exists())

        # Check that the file has the correct dimensions
        original_dims = get_content_dimensions("assets/TEST_DATA/content/ana_cat.mp4")
        output_dims = get_content_dimensions(self.output_image)

        r = float(850) / float(original_dims[0])
        expected_dims = (850, round(r * original_dims[1]))

        self.assertEqual(output_dims, expected_dims)

    def test_raises_an_error_if_the_file_does_not_exist(self):
        with self.assertRaises(Exception):
            generate_sample("assets/TEST_DATA/content/does_not_exist.jpg", self.output_image)
        
        # Make sure that there was no output file
        self.assertFalse(pathlib.Path(self.output_image).exists())
    
    def test_raises_an_error_if_file_corrupted(self):
        with self.assertRaises(Exception):
            generate_sample("assets/TEST_DATA/content/corrupted_image.jpg", self.output_image)

        # Make sure that there was no output file
        self.assertFalse(pathlib.Path(self.output_image).exists())

    def test_returns_true_upon_applicable(self):
        self.assertTrue(generate_sample(self.original_image, self.output_image))
    
    def test_returns_false_upon_inapplicable(self):
        self.assertFalse(generate_sample("assets/TEST_DATA/content/felix.jpg", self.output_image))

    # TODO test videos

class ValidUsernameTest(TestCase):
    def test_valid_username(self):
        usernames = ["test", "H0wITsDone", "cool_man123", "games_are_fun", "gamer", "SalC1", "yay"]

        for username in usernames:
            self.assertTrue(is_valid_username(username))
    
    def test_invalid_username(self):
        usernames = ["", " ", "test@", "gamer man", "chad!!", "a" * 21, "a", "aa", None, False]

        for username in usernames:
            self.assertFalse(is_valid_username(username))

class ValidPasswordTest(TestCase):
    def test_valid_password(self):
        passwords = ["P@ssw0rd1.3!", "水泥420!", "Now this @~is ep1c!" "SomethingReallyS3cure1!", "Password123!", "IL0v3Gaming!"]

        for password in passwords:
            self.assertTrue(is_valid_password(password))
    
    def test_invalid_password(self):
        passwords = ["", " ", "test", "gaming", "password", "a", "aaaaa", "password1"]

        for password in passwords:
            self.assertFalse(is_valid_password(password))
    
    def test_disable_safety(self):
        # Disable safety
        homebooru.settings.LOGIN_ALLOW_INSECURE_PASSWORD = True

        passwords = ["something", "a", "abc", "password123"]

        for password in passwords:
            self.assertTrue(is_valid_password(password))

        # Re-enable safety
        homebooru.settings.LOGIN_ALLOW_INSECURE_PASSWORD = False

        # Make sure they would have failed
        for password in passwords:
            self.assertFalse(is_valid_password(password))


class ValidEmailTest(TestCase):
    def test_valid_emails(self):
        emails = ["test@gmail.com", "martincool2003@outlook.com", "gaming@gov.uk"]

        for email in emails:
            self.assertTrue(is_valid_email(email))

    def test_invalid_emails(self):
        emails = ["", " ", "test", "test@gmailcom", "testgmail.com", "test@", "test@gmail", "test@gmail.", "test@gmail.", "huevo.com", "example", None]

        for email in emails:
            self.assertFalse(is_valid_email(email))