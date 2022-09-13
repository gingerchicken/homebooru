from django.test import TestCase

from scanner.models import ScannerIgnore

from scanner.tests.testutils import BOORU_MD5

class ScannerIgnoreStrTest(TestCase):
    def test_str(self):
        """The string representation is the checksum"""

        # Create a new ignore
        ignore = ScannerIgnore(md5=BOORU_MD5)

        # Check the string representation
        self.assertEqual(str(ignore), BOORU_MD5)