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

class PoolPostTest(TestCase):
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

        # Create another post
        self.post2 = Post.create_from_file(testutils.FELIX_PATH)
        self.post2.save()

        # Create a pool
        self.pool = Pool(name='Test Pool', creator=self.user)
        self.pool.save()

    def test_order_inc(self):
        # Create a pool post
        pool_post = PoolPost(pool=self.pool, post=self.post)
        pool_post.save()

        # Check the order
        self.assertEqual(pool_post.display_order, 0)

        # Create another pool post
        pool_post2 = PoolPost(pool=self.pool, post=self.post2)
        pool_post2.save()

        # Check the order
        self.assertEqual(pool_post2.display_order, 1)

    def test_order_inc_last(self):
        # Create a pool post
        pool_post = PoolPost(pool=self.pool, post=self.post, display_order=5)
        pool_post.save()

        # Check the order
        self.assertEqual(pool_post.display_order, 5)

        # Create another pool post
        pool_post2 = PoolPost(pool=self.pool, post=self.post2)
        pool_post2.save()

        # Check the order
        self.assertEqual(pool_post2.display_order, 6)
