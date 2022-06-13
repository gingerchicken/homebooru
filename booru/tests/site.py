from django.test import TestCase

from ..models.posts import *

# Test the index page
class IndexTest(TestCase):
    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_imagecounter(self):
        response = self.client.get('/')
        self.assertContains(response, '<div id="imagecounter">')
        self.assertContains(response, '<img src="/static/layout/')

    def setUp(self):
        # Clear tables
        Post.objects.all().delete()