from django.test import TestCase

from ...models.posts import *
import booru.tests.testutils as testutils

class RandomTest(TestCase):
    temp_storage = testutils.TempStorage()
    
    def setUp(self) -> None:
        self.temp_storage.setUp()

        post_paths = [
            testutils.FELIX_PATH, testutils.BOORU_IMAGE, testutils.GATO_PATH
        ]

        # Create posts
        for p in post_paths:
            post = Post.create_from_file(p)
            post.save()

    def tearDown(self) -> None:
        self.temp_storage.tearDown()
    
    def send_request(self):
        return self.client.get('/random')

    def test_gets_a_post(self):
        """Gets a post"""

        # Send request
        response = self.send_request()

        # Make sure that it is a redirect
        self.assertEqual(response.status_code, 302)

        # Make sure that the redirect is to a post
        self.assertTrue(response.url.startswith('/post/'))

        # Make sure that the redirect is to a post that exists
        post_id = int(response.url.split('/')[-1])
        self.assertTrue(Post.objects.filter(id=post_id).exists())

    def test_random_post(self):
        """Gets posts at random"""

        posts = Post.objects.all()

        TRIALS = 1000

        frequencies = {}

        for i in range(TRIALS):
            response = self.send_request()
            post_id = int(response.url.split('/')[-1])
            if post_id not in frequencies:
                frequencies[post_id] = 0
            frequencies[post_id] += 1

        # Make sure that each post was selected at least once
        self.assertEqual(len(frequencies), len(posts))

        approx_avg = TRIALS / len(posts)

        allowed_delta = approx_avg * 0.1

        # Make sure that they are all approximately equally selected
        for post_id in frequencies:
            self.assertAlmostEqual(frequencies[post_id], approx_avg, delta=allowed_delta)
    
    def test_no_posts(self):
        """Redirects to index when there are no posts"""

        # Delete all posts
        Post.objects.all().delete()

        # Send request
        response = self.send_request()

        # Make sure that it is a redirect
        self.assertEqual(response.status_code, 302)

        # Make sure that the redirect is to the index
        self.assertEqual(response.url, '/')