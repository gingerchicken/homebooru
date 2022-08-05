from django.test import TestCase

from scanner.models import Booru

import scanner.tests.testutils as scanner_testutils

class SearchBooruMD5Test(TestCase):
    valid_md5 = scanner_testutils.BOORU_MD5
    expected_tags = scanner_testutils.BOORU_TAGS

    def setUp(self):
        booru_url = scanner_testutils.VALID_BOORUS[0]

        self.booru = Booru(url=booru_url, name='imagebooru')
        self.booru.save()

    def test_search_booru_md5(self):
        """Returns expected search result"""

        result = self.booru.search_booru_md5(md5=self.valid_md5)

        # Make sure that the result was found
        self.assertTrue(result.found)

        # Make sure that the tags are correct
        for tag in self.expected_tags:
            self.assertTrue(tag in result.tags)
        
        # Make sure that the rating is correct
        self.assertEqual(result.raw_rating, 'safe')

    def test_invalid_search(self):
        """Returns a non-found search result"""

        invalid_md5 = 'invalid_md5'

        result = self.booru.search_booru_md5(md5=invalid_md5)

        # Make sure that the result was not found
        self.assertFalse(result.found)

        # Make sure that the tags are correct
        self.assertEqual(result.tags, '')

        # Make sure that the rating is correct
        self.assertEqual(result.raw_rating, '')

class TestBooruTest(TestCase):
    def test_valid(self):
        """Returns true with valid boorus"""

        # Get a valid booru
        for booru_url in scanner_testutils.VALID_BOORUS:
            # Create a new booru
            booru = Booru(url=booru_url, name='imagebooru')

            # Make sure that the booru is valid
            self.assertTrue(booru.test(), 'Failed to test booru: ' + booru_url)

    def test_invalid(self):
        """Returns false with invalid boorus"""

        # Get an invalid booru
        for booru_url in scanner_testutils.INVALID_BOORUS:
            # Create a new booru
            booru = Booru(url=booru_url, name='imagebooru')

            # Make sure that the booru is invalid
            self.assertFalse(booru.test(), 'Failed to test booru: ' + booru_url)

class BooruStrTest(TestCase):
    def test_str(self):
        """Returns the name of the booru"""

        booru_url = scanner_testutils.VALID_BOORUS[0]

        # Create a new booru
        booru = Booru(url=booru_url, name='something cool')

        # Make sure that the booru is valid
        self.assertEqual(str(booru), 'something cool')

class SaveBooruTest(TestCase):
    def test_rejects_invalid(self):
        """Rejects invalid boorus"""

        # Get an invalid booru
        for booru_url in scanner_testutils.INVALID_BOORUS:
            # Create a new booru
            booru = Booru(url=booru_url, name='imagebooru')

            # Make sure it raises an error
            with self.assertRaises(Exception):
                booru.save()

    def test_accepts_valid(self):
        """Accepts valid boorus"""

        i = 0
        # Get a valid booru
        for booru_url in scanner_testutils.VALID_BOORUS:
            # Create a new booru
            booru = Booru(url=booru_url, name='imagebooru' + str(i))

            # Make sure it doesn't raise an error
            booru.save()

            i += 1