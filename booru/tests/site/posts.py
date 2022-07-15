from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

from booru.models.posts import Post
import booru.boorutils as boorutils
import booru.tests.testutils as testutils

from ...views.posts import *

import json

class PostDeleteTest(TestCase):
    temp_storage = testutils.TempStorage()
    
    def setUp(self):
        self.temp_storage.setUp()

        # Create a user
        self.user = User.objects.create_user(username='test', password='huevo')
        self.user.save()

        # Create a post
        self.post = Post.create_from_file(
            testutils.FELIX_PATH
        )
        self.post.save()
    
    def tearDown(self):
        self.temp_storage.tearDown()

    def send_request(self, post_id):
        """Sends a request to the post delete page"""

        return self.client.delete(
            '/post/' + str(post_id)
        )

    def test_post_delete_as_owner(self):
        """Allows the owner to delete the post"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Make the user the owner
        self.post.owner = self.user

        # Save the post
        self.post.save()

        # Send the request
        resp = self.send_request(self.post.id)

        # Check the response status code
        self.assertEqual(resp.status_code, 302)

        # Check the response redirects to the home page
        self.assertEqual(resp.url, reverse('index'))

        # Check the post was deleted
        self.assertEqual(Post.objects.filter(id=self.post.id).count(), 0)

    def test_post_delete_as_admin(self):
        """Allows admins to delete posts"""

        # Create an admin
        admin = User.objects.create_user(username='admin', password='huevo', is_superuser=True)
        admin.save()

        # Login
        self.assertTrue(self.client.login(username='admin', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id)

        # Check the response status code
        self.assertEqual(resp.status_code, 302)

        # Check the response redirects to the home page
        self.assertEqual(resp.url, reverse('index'))

        # Check the post was deleted   
        self.assertEqual(Post.objects.filter(id=self.post.id).count(), 0)

    def test_post_delete_as_anonymous(self):
        """Disallows anonymous users from deleting posts"""

        # Logout
        self.client.logout()

        # Send the request
        resp = self.send_request(self.post.id)

        # Sends a 403
        self.assertEqual(resp.status_code, 403)

        # Check the post was not deleted
        self.assertEqual(Post.objects.filter(id=self.post.id).count(), 1)

    def test_post_delete_as_other_user(self):
        """Disallows users from deleting other users' posts"""

        # Create a user
        user = User.objects.create_user(username='test2', password='huevo')

        # Save the user
        user.save()

        # Login
        self.assertTrue(self.client.login(username='test2', password='huevo'))

        # Set the post owner
        self.post.owner = self.user

        # Save the post
        self.post.save()

        # Send the request
        resp = self.send_request(self.post.id)

        # Sends a 403
        self.assertEqual(resp.status_code, 403)

        # Check the post was not deleted
        self.assertEqual(Post.objects.filter(id=self.post.id).count(), 1)
    
    def test_post_rejects_invalid_id(self):
        """Rejects invalid post IDs"""

        invalid_ids = [0, -1, 4354]

        for invalid_id in invalid_ids:
            # Send the request
            resp = self.send_request(invalid_id)

            # Sends a 404
            self.assertEqual(resp.status_code, 404)

            # Check the post was not deleted
            self.assertEqual(Post.objects.filter(id=self.post.id).count(), 1)

class PostLockTest(TestCase):
    temp_storage = testutils.TempStorage()
    
    def setUp(self):
        self.temp_storage.setUp()

        # Create a user
        self.user = User.objects.create_user(username='test', password='huevo')
        self.user.save()

        # Add booru.change_post
        permission = Permission.objects.get(codename='change_post')
        self.user.user_permissions.add(permission)
        self.user.save()


        # Create a post
        self.post = Post.create_from_file(
            testutils.FELIX_PATH
        )
        self.post.save()
    
    def tearDown(self):
        self.temp_storage.tearDown()

    def send_request(self, post_id, locked=True):
        """Sends a request to the post lock page"""

        return self.client.post(
            '/post/' + str(post_id), {'locked': locked} 
        )

    def test_post_lock_as_owner(self):
        """Disallows the owner to lock the post"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Make the user the owner
        self.post.owner = self.user

        # Save the post
        self.post.save()

        # Send the request
        resp = self.send_request(self.post.id)

        # Check the response status code
        self.assertEqual(resp.status_code, 403)

        # Make sure that the response body includes the correct message
        self.assertIn('lock', resp.content.decode('utf-8'))

        # Get the post from the database
        post = Post.objects.get(id=self.post.id)

        # Check the post was not locked
        self.assertFalse(post.locked)

    def test_post_lock_as_admin(self):
        """Allows admins to lock posts"""

        # Create an admin
        admin = User.objects.create_user(username='admin', password='huevo', is_superuser=True)
        admin.save()

        # Login
        self.assertTrue(self.client.login(username='admin', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id)

        # Check the response status code
        self.assertEqual(resp.status_code, 203)

        # Get the post from the database
        post = Post.objects.get(id=self.post.id)

        # Check the post was locked
        self.assertTrue(post.locked)

    def test_post_lock_as_anonymous(self):
        """Disallows anonymous users from locking posts"""

        # Logout
        self.client.logout()

        # Send the request
        resp = self.send_request(self.post.id)

        # Sends a 403
        self.assertEqual(resp.status_code, 403)

        # Get the post from the database
        post = Post.objects.get(id=self.post.id)

        # Check the post was not locked
        self.assertFalse(post.locked)
    
    def test_allows_users_with_perm(self):
        # Give user permission to lock posts
        self.user.user_permissions.add(Permission.objects.get(codename='lock_post'))
        self.user.save()

        # Make sure they have the permission
        self.assertTrue(self.user.has_perm('booru.lock_post'))

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id)

        # Check the response status code
        self.assertEqual(resp.status_code, 203, resp.content.decode('utf-8'))

        # Get the post again
        post = Post.objects.get(id=self.post.id)

        # Check the post was locked
        self.assertTrue(post.locked)
    
    def test_disallows_without_change_perm(self):
        # Give user permission to lock posts
        self.user.user_permissions.add(Permission.objects.get(codename='lock_post'))
        self.user.save()

        # Remove the booru.change_post permission
        permission = Permission.objects.get(codename='change_post')
        self.user.user_permissions.remove(permission)
        self.user.save()

        # Make sure they have the correct permissions
        self.assertTrue(self.user.has_perm('booru.lock_post'))

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id, locked=True)

        # Check the response status code
        self.assertEqual(resp.status_code, 403, resp.content.decode('utf-8'))

        # Get the post
        post = Post.objects.get(id=self.post.id)

        # Check the post was not locked
        self.assertFalse(post.locked)