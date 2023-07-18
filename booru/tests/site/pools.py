from django.test import TestCase
from django.contrib.auth.models import Permission

from ...models.posts import *
from booru.models import Pool, Post, PoolPost
from booru.tests import testutils
import json

class PostPoolDeleteTest(TestCase):
    temp_storage = testutils.TempStorage()
    
    def setUp(self):
        self.temp_storage.setUp()

        # Create a user
        self.user = User.objects.create_user(username='test', password='huevo')
        self.user.save()

        # Give the user permission to delete post pools
        self.user.user_permissions.add(Permission.objects.get(codename='delete_poolpost'))

        # Create a post
        self.post = Post.create_from_file(
            testutils.FELIX_PATH
        )
        self.post.save()

        # Create a pool
        self.pool = Pool(
            name='test',
            description='test',
            creator=self.user
        )

        self.pool.save()

        # Add the post to the pool
        self.pool_post = PoolPost(
            pool=self.pool,
            post=self.post
        )

        self.pool_post.save()

        self.client.login(username='test', password='huevo')
    
    def tearDown(self):
        self.temp_storage.tearDown()

        super().tearDown()

    def send_request(self, pool_id, posts = []):
        return self.client.delete(
            '/pools/{}'.format(pool_id),
            json.dumps({
                'posts': posts
            }),
            content_type='application/json'
        )

    def test_delete_post_pool(self):
        """Deletes a post pool"""

        # Send the request
        response = self.send_request(self.pool.id, [self.post.id])
        
        # Make sure that it was a 200
        self.assertEqual(response.status_code, 200, response.content)

        # Make sure that the pool post was deleted
        self.assertFalse(PoolPost.objects.filter(pool=self.pool, post=self.post).exists())

    def test_delete_multiple_post_pools(self):
        """Deletes multiple post pools"""

        # Create another post
        post2 = Post.create_from_file(
            testutils.GATO_PATH
        )
        post2.save()

        # Add the post to the pool
        pool_post2 = PoolPost(
            pool=self.pool,
            post=post2
        )

        pool_post2.save()

        # Send the request
        response = self.send_request(self.pool.id, [self.post.id, post2.id])

        # Make sure that it was a 200
        self.assertEqual(response.status_code, 200, response.content)

        # Make sure that the pool post was deleted
        self.assertFalse(PoolPost.objects.filter(pool=self.pool, post=self.post).exists())
        self.assertFalse(PoolPost.objects.filter(pool=self.pool, post=post2).exists())

    def test_delete_only_one(self):
        """Deletes only one post from a pool"""

        # Create another post
        post2 = Post.create_from_file(
            testutils.GATO_PATH
        )
        post2.save()

        # Add the post to the pool
        pool_post2 = PoolPost(
            pool=self.pool,
            post=post2
        )

        pool_post2.save()

        # Send the request
        response = self.send_request(self.pool.id, [self.post.id])

        # Make sure that it was a 200
        self.assertEqual(response.status_code, 200, response.content)

        # Make sure that the pool post was deleted
        self.assertFalse(PoolPost.objects.filter(pool=self.pool, post=self.post).exists())
        self.assertTrue(PoolPost.objects.filter(pool=self.pool, post=post2).exists())