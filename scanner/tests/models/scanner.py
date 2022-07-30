from django.test import TestCase

from scanner.models import Booru, Scanner
import booru.tests.testutils as booru_testutils
import scanner.tests.testutils as scanner_testutils

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