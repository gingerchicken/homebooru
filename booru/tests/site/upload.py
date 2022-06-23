from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import serializers

from ...models.posts import *
import booru.tests.testutils as testutils

class UploadTest(TestCase):
    def test_page(self):
        """Makes sure that the page can be GET'd"""

        response = self.client.get('/upload')

        self.assertEqual(response.status_code, 200)
    
    def test_form_visible(self):
        """Makes sure that there is a form on the page"""

        # Make sure that it has an upload form
        response = self.client.get('/upload')

        self.assertContains(response, 'form method="post" action="/upload" enctype="multipart/form-data"')

class UploadPOSTTest(TestCase):
    temp_storage = testutils.TempStorage()
    test_path = testutils.FELIX_PATH

    fixtures = ['ratings.json']

    def setUp(self):
        self.temp_storage.setUp()

        super().setUp()

    def tearDown(self):
        self.temp_storage.tearDown()

        super().tearDown()
    
    def post(self, body):
        return self.client.post('/upload', body)
    
    def make_post(self, path, tags, title, source, rating):
        return self.client.post('/upload', 
            {
                'upload': SimpleUploadedFile(path, path.read_bytes()) if path is not None else None,
                'tags': tags,
                'title': title,
                'source': source,
                'rating': rating
            }
        )

    def test_post_no_file(self):
        """Rejects an empty post form"""

        response = self.client.post('/upload')

        self.assertEqual(response.status_code, 400)

        # Make sure that no post was created
        self.assertEqual(Post.objects.count(), 0)
    
    def test_rating_valid(self):
        """Accepts valid ratings"""

        ratings = ['explicit', 'safe', 'questionable']
        for rating in ratings:
            self.setUp()

            resp = self.make_post(self.test_path, 'tag1 tag2 tag3', 'a title', 'https://example.com/', rating)

            # Get the post
            post = Post.objects.first()
            self.assertEqual(post.rating.name, rating)

            self.tearDown()

    def test_rating_invalid(self):
        """Rejects invalid ratings"""

        ratings = ['x', 'y', 'z', 'zoom']

        for rating in ratings:
            resp = self.make_post(self.test_path, 'tag1 tag2 tag3', 'a title', 'https://example.com/', rating)

            self.assertEqual(resp.status_code, 400)

            # Make sure that the post wasn't created
            self.assertEqual(Post.objects.count(), 0)

    def test_file_invalid(self):
        """Rejects non-image types"""

        resp = self.make_post(testutils.NON_IMAGE_PATH, 'tag1 tag2 tag3', 'a title', 'https://example.com/', 'explicit')

        self.assertEqual(resp.status_code, 400)

        # Make sure that the post wasn't created
        self.assertEqual(Post.objects.count(), 0)

        # Make sure that the tags were not created
        self.assertEqual(Tag.objects.count(), 0)

        # Make sure that it gave an error "file type not allowed"
        # self.assertContains(resp.content, 'File type not allowed')

    def test_file_corrupted(self):
        """Rejects corrupted files"""

        resp = self.make_post(testutils.CORRUPT_IMAGE_PATH, 'tag1 tag2 tag3', 'a title', 'https://example.com/', 'explicit')

        self.assertEqual(resp.status_code, 400)

        # Make sure that the post wasn't created
        self.assertEqual(Post.objects.count(), 0)

        # Make sure that it gave an error "file type not allowed"
        # self.assertContains(resp.content, 'File type not allowed')

    # TODO test file too large

    def test_duplicate_post(self):
        """Rejects posts that have duplicate files"""

        resp = self.make_post(self.test_path, 'tag1 tag2 tag3', 'a title', 'https://example.com/', 'explicit')

        # Make sure it was accepted
        self.assertEqual(resp.status_code, 302)

        # Make sure that the post was created
        self.assertEqual(Post.objects.count(), 1)

        # Send the post again
        resp = self.make_post(self.test_path, 'tag1 tag2 tag3', 'a title', 'https://example.com/', 'explicit')

        # Make sure it was rejected
        self.assertEqual(resp.status_code, 400)

        # Make sure that the post wasn't created
        self.assertEqual(Post.objects.count(), 1)

        # Make sure that it gave an error "File already exists"
        # self.assertContains(resp.content, 'File already exists')


    def test_post_video(self):
        """Accepts video posts"""

        resp = self.make_post(testutils.VIDEO_PATH, 'tag1 tag2 tag3', 'a title', 'https://example.com/', 'explicit')

        self.assertEqual(resp.status_code, 302)

        # Check that the post was created
        self.assertEqual(Post.objects.count(), 1)

        # Check that the post has the correct tags
        post = Post.objects.first()

        self.assertEqual(post.tags.count(), 3)
        self.assertEqual(post.tags.first().tag, 'tag1')
        self.assertEqual(post.tags.last().tag, 'tag3')

        # Check that the post has the correct title
        self.assertEqual(post.title, 'a title')

        # Check that the post has the correct source
        self.assertEqual(post.source, 'https://example.com/')

        # Check that the post has the correct rating
        self.assertEqual(post.rating.name, 'explicit')

        # Make sure that the post is a video
        self.assertEqual(post.is_video, 1)

        # Check that the post has the right md5
        self.assertEqual(post.md5, boorutils.get_file_checksum(testutils.VIDEO_PATH))

    def test_tags_invalid(self):
        """Rejects invalid tag sets"""

        invalid = [
            't a g', '**** *.*', '', '     ', 'rating:safe', 'md5:520'
        ]

        for tags in invalid:
            resp = self.make_post(testutils.FELIX_PATH, tags, 'a title', 'https://example.com/', 'explicit')

            self.assertEqual(resp.status_code, 400)

            # Make sure no tags were created
            self.assertEqual(Tag.objects.count(), 0)

            # Make sure that the post wasn't created
            self.assertEqual(Post.objects.count(), 0)
        
    def test_tags_duplicate(self):
        """Processes duplicate tags correctly"""

        resp = self.make_post(testutils.FELIX_PATH, 'tag1 tag1', 'a title', 'https://example.com/', 'explicit')

        self.assertEqual(resp.status_code, 302)

        # Make sure only one tag was created
        self.assertEqual(Tag.objects.count(), 1)

        # Make sure that the post was created
        self.assertEqual(Post.objects.count(), 1)

        # Make sure it only has one tag
        post = Post.objects.first()
        self.assertEqual(post.tags.count(), 1)

    def test_post_valid(self):
        """Accepts valid posts"""

        resp = self.make_post(self.test_path, 'tag1 tag2 tag3', 'a title', 'https://example.com/', 'explicit')

        self.assertEqual(resp.status_code, 302)

        # Check that the post was created
        self.assertEqual(Post.objects.count(), 1)

        # Check that the post has the correct tags
        post = Post.objects.first()

        self.assertEqual(post.tags.count(), 3)
        self.assertEqual(post.tags.first().tag, 'tag1')
        self.assertEqual(post.tags.last().tag, 'tag3')

        # Make sure that the tags were created
        self.assertEqual(Tag.objects.count(), 3)

        # Check that the post has the correct title
        self.assertEqual(post.title, 'a title')

        # Check that the post has the correct source
        self.assertEqual(post.source, 'https://example.com/')

        # Check that the post has the correct rating
        self.assertEqual(post.rating.name, 'explicit')

        # Check that the post has the right md5
        self.assertEqual(post.md5, boorutils.get_file_checksum(self.test_path))
    
    def test_redirects_to_correct_page(self):
        """Redirects to the correct page"""

        resp = self.make_post(self.test_path, 'tag1 tag2 tag3', 'a title', 'https://example.com/', 'explicit')

        # Get the post
        post = Post.objects.first()

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], '/view?id=' + str(post.id))