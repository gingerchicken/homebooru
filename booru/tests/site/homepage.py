from django.test import TestCase

from ...models.posts import *

# Test the index page
class IndexTest(TestCase):
    def test_index(self):
        """Checks the main page can be accessed"""

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_imagecounter(self):
        """Checks the image counter is correct"""

        response = self.client.get('/')
        self.assertContains(response, '<div id="imagecounter">')
        self.assertContains(response, '<img src="/static/layout/')

    def setUp(self):
        # Clear tables
        Post.objects.all().delete()