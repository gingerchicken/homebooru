from django.test import TestCase
from django.contrib.auth.models import Permission
from django.urls import reverse

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

class EditPoolTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.user.save()

        self.user.user_permissions.add(Permission.objects.get(codename='change_pool'))

        self.pool = Pool.objects.create(
            name='Test Pool',
            description='Test Description',
            creator=self.user
        )

        self.client.login(username='testuser', password='password')

    def send_request(self, pool_id, name, description):
        return self.client.post(reverse('edit_pool', kwargs={'pool_id': pool_id}), {
            'name': name,
            'description': description
        })

    def test_successful_pool_edit(self):
        """
        Accepts valid pool data and updates the pool
        """
        response = self.send_request(self.pool.id, 'Updated Pool Name', 'Updated Description')
        self.assertEqual(response.status_code, 302)  # Redirect after successful edit
        self.pool.refresh_from_db()
        self.assertEqual(self.pool.name, 'Updated Pool Name')
        self.assertEqual(self.pool.description, 'Updated Description')

    def test_no_account(self):
        """
        Rejects anonymous users
        """
        self.client.logout()
        response = self.send_request(self.pool.id, 'Updated Pool Name', 'Updated Description')
        self.assertContains(response, 'You must be logged in to edit pools.')

    def test_no_permission(self):
        """
        Rejects users without the 'change_pool' permission
        """
        self.user.user_permissions.remove(Permission.objects.get(codename='change_pool'))
        response = self.send_request(self.pool.id, 'Updated Pool Name', 'Updated Description')
        self.assertContains(response, 'You do not have permission')

        self.pool.refresh_from_db()
        self.assertEqual(self.pool.name, 'Test Pool')

    def test_invalid_pool_data(self):
        """
        Rejects invalid pool data (e.g., name too short/long, description too long)
        """
        response = self.send_request(self.pool.id, 'ab', 'Description')
        self.assertContains(response, 'Pool name must be at least 3 characters long.')

        response = self.send_request(self.pool.id, 'a' * 256, 'Description')
        self.assertContains(response, 'Pool name cannot be longer than 255 characters.')

        response = self.send_request(self.pool.id, 'Valid Name', 'a' * 1025)
        self.assertContains(response, 'Pool description cannot be longer than 1024 characters.')

    def test_duplicate_pool_name(self):
        """
        Rejects duplicate pool names
        """
        Pool.objects.create(
            name='Another Pool',
            description='Another Description',
            creator=self.user
        )

        response = self.send_request(self.pool.id, 'Another Pool', 'Updated Description')
        self.assertContains(response, 'A pool with that name already exists.')