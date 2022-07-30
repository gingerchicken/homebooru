from django.test import TestCase

from scanner.models import Booru, Scanner
import booru.tests.testutils as booru_testutils
import scanner.tests.testutils as scanner_testutils

import homebooru.settings

class BoorusTest(TestCase):
    def setUp(self):
        # Create a scanner
        self.scanner = Scanner(name='test_scanner', path=booru_testutils.CONTENT_PATH)
        self.scanner.save()

        # Create some boorus
        self.boorus = []
        for booru_url in scanner_testutils.VALID_BOORUS:
            booru = Booru(url=booru_url, name='imagebooru ' + str(len(self.boorus)))
            booru.save()

            self.boorus.append(booru)


    def test_expected_boorus(self):
        """Returns expected boorus"""

        # Add a booru to the scanner
        self.scanner.search_boorus.add(self.boorus[0])
        self.scanner.save()

        # Get the expected boorus
        expected_boorus = [self.boorus[0]]

        # Get the actual boorus
        actual_boorus = self.scanner.boorus.all()
    
    def test_empty_boorus(self):
        """Returns all boorus if none are specified"""
        # Get the expected boorus
        expected_boorus = self.boorus

        # Get the actual boorus
        actual_boorus = self.scanner.boorus

        # Make sure the same amount of boorus are returned
        self.assertEqual(len(expected_boorus), len(actual_boorus))

        # Make sure all boorus are returned
        for booru in expected_boorus:
            self.assertTrue(booru in actual_boorus)

class ScannerStrTest(TestCase):
    def setUp(self):
        self.scanner = Scanner(name='test_scanner', path=booru_testutils.CONTENT_PATH)
        self.scanner.save()

    def test_str(self):
        """Returns the name of the scanner"""
        self.assertEqual(str(self.scanner), 'test_scanner')

class DefaultTagsTest(TestCase):
    def setUp(self):
        self.og_setting = homebooru.settings.SCANNER_USE_DEFAULT_TAGS
        homebooru.settings.SCANNER_USE_DEFAULT_TAGS = True

        self.og_tags = homebooru.settings.SCANNER_DEFAULT_TAGS
        homebooru.settings.SCANNER_DEFAULT_TAGS = ['test_tag', 'test_tag2']

        self.scanner = Scanner(name='test_scanner', path=booru_testutils.CONTENT_PATH)
        self.scanner.save()
    
    def tearDown(self):
        homebooru.settings.SCANNER_USE_DEFAULT_TAGS = self.og_setting
        homebooru.settings.SCANNER_DEFAULT_TAGS = self.og_tags

    def test_default_tags(self):
        """Returns the default tags"""

        # Get the raw tags
        raw_tags = homebooru.settings.SCANNER_DEFAULT_TAGS

        # Get the actual tags
        actual_tags = self.scanner.default_tags

        for tag in actual_tags:
            raw_tag = tag.tag
            self.assertTrue(raw_tag in raw_tags, 'Tag ' + raw_tag + ' not in ' + str(raw_tags))

            # Remove the tag from the raw tags (i.e. only appear once)
            raw_tags.remove(raw_tag)
    
    def test_default_tags_not_used(self):
        """Returns no default tags if the scanner does not use them"""
        homebooru.settings.SCANNER_USE_DEFAULT_TAGS = False

        # Get the actual tags
        actual_tags = self.scanner.default_tags

        # Make sure that the actual tags are empty
        self.assertEqual(len(actual_tags), 0)

class ScannerSaveTest(TestCase):
    def test_rejects_invalid_path(self):
        """Rejects invalid paths"""

        scanner = Scanner(name='test_scanner', path='/invalid/path')
        self.assertRaises(ValueError, scanner.save)
    
    def test_rejects_non_directory(self):
        """Rejects non-directory paths"""

        scanner = Scanner(name='test_scanner', path=booru_testutils.FELIX_PATH)
        self.assertRaises(ValueError, scanner.save)
    
    def test_accepts_directory(self):
        """Accepts directory paths"""

        scanner = Scanner(name='test_scanner', path=booru_testutils.CONTENT_PATH)
        scanner.save()

        self.assertTrue(scanner.pk is not None)
