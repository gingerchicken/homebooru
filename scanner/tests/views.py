from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.urls import reverse

from scanner.models import Scanner, Booru
from booru.models import Post

import scanner.tests.testutils as scanner_testutils
import booru.tests.testutils as booru_testutils

class ScanTest(TestCase):
    temp_scan_folder = scanner_testutils.TempScanFolder()
    temp_storage_folder = booru_testutils.TempStorage()
    
    def setUp(self):
        self.temp_scan_folder.add_file(booru_testutils.BOORU_IMAGE)
        self.temp_scan_folder.setUp()
        self.temp_storage_folder.setUp()

        # Create a booru
        self.booru = Booru(name='Imageboard', url=scanner_testutils.VALID_BOORUS[0])
        self.booru.save()

        # Create a scanner
        self.scanner = Scanner(name='Scanner', path=self.temp_scan_folder.folder)
        self.scanner.save()

        self.scanner.boorus.add(self.booru)
        self.scanner.save()

        # Create a user
        self.user = User(username='testuser')
        self.user.save()

        # Give the user permission to scan
        self.user.user_permissions.add(Permission.objects.get(codename='scan'))
        self.user.save()

        # Log the user in
        self.client.force_login(self.user)

    def tearDown(self):
        self.temp_storage_folder.tearDown()
        self.temp_scan_folder.tearDown()
        self.temp_scan_folder.remove_all_files()
    
    def send_request(self, scanner_id):
        return self.client.get(reverse('scan', kwargs={'scanner_id': scanner_id}))

    def test_scan(self):
        """Scans a scanner when requested"""

        # Make sure that there are no posts
        self.assertEqual(Post.objects.count(), 0)

        # Scan the scanner
        response = self.send_request(self.scanner.id)

        # Make sure that the response is a redirect
        self.assertEqual(response.status_code, 302)

        # Make sure that there is now one post
        self.assertEqual(Post.objects.count(), 1)
    
    def test_scan_invalid_scanner(self):
        """Scans an invalid scanner"""

        # Make sure that there are no posts
        self.assertEqual(Post.objects.count(), 0)

        # Scan the scanner
        response = self.send_request(543543)

        # Make sure that the response is 404
        self.assertEqual(response.status_code, 404)

        # Make sure that there are no posts
        self.assertEqual(Post.objects.count(), 0)
    
    def test_scan_no_permission(self):
        """Scans a scanner without permission"""

        # Make sure that there are no posts
        self.assertEqual(Post.objects.count(), 0)

        # Remove the user's permission to scan
        self.user.user_permissions.remove(Permission.objects.get(codename='scan'))
        self.user.save()

        # Scan the scanner
        response = self.send_request(self.scanner.id)

        # Make sure that the response is 403
        self.assertEqual(response.status_code, 403)

        # Make sure that there are no posts
        self.assertEqual(Post.objects.count(), 0)

    def test_scan_logged_out(self):
        """Scans a scanner when logged out"""

        # Make sure that there are no posts
        self.assertEqual(Post.objects.count(), 0)

        # Log the user out
        self.client.logout()

        # Scan the scanner
        response = self.send_request(self.scanner.id)

        # Make sure that the response is 403
        self.assertEqual(response.status_code, 403)

        # Make sure that there are no posts
        self.assertEqual(Post.objects.count(), 0)

    def test_scan_active(self):
        """Rejects when scan is active"""

        # Make active
        self.scanner.set_is_active(True)

        # Scan the scanner
        response = self.send_request(self.scanner.id)

        # Make sure that the response is 400
        self.assertEqual(response.status_code, 400)

        # Make sure that there are no posts
        self.assertEqual(Post.objects.count(), 0)

        # Make inactive
        self.scanner.set_is_active(False)

        # Scan the scanner
        response = self.send_request(self.scanner.id)

        # Make sure that the response is not 400
        self.assertNotEqual(response.status_code, 400)

        # Make sure that there are posts
        self.assertEqual(Post.objects.count(), 1)