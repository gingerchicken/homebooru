from django.test import TestCase

from ...models.posts import *
import booru.tests.testutils as testutils

class UploadTest(TestCase):
    temp_storage = testutils.TempStorage()

    def test_page(self):
        response = self.client.get('/upload')

        self.assertEqual(response.status_code, 200)
    
    def test_form_visible(self):
        # Make sure that it has an upload form
        response = self.client.get('/upload')

        self.assertContains(response, 'form method="post" action="/upload" enctype="multipart/form-data"')
    
    def setUp(self):
        self.temp_storage.setUp()
    
    def tearDown(self):
        self.temp_storage.tearDown()