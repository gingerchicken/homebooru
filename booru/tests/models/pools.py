from django.test import TestCase
from django.contrib.auth.models import User

import booru.tests.testutils as testutils

from ...models.posts import Post, Rating
from ...models.pool import Pool, PoolPost

class PoolTestCase(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='test',
            password='test'
        )
        self.user.save()

        # Create a post
        self.post = Post.create_from_file(testutils.GATO_PATH)
        self.post.save()

    def test_pool_str(self):
        # Create a pool
        pool = Pool(name='Test Pool', creator=self.user)
        pool.save()

        # Check the string
        self.assertEqual(str(pool), 'Test Pool')
    
    def test_pool_posts(self):
        # Create a pool
        pool = Pool(name='Test Pool', creator=self.user)
        pool.save()

        # Add a post
        pool_post = PoolPost(pool=pool, post=self.post)
        pool_post.save()

        # Check the post
        self.assertEqual(pool.posts.first().post, self.post)