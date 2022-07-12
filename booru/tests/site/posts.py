from django.test import TestCase
from django.contrib.auth.models import User

from booru.models.posts import Post
import booru.boorutils as boorutils
import booru.tests.testutils as testutils

from ...views.posts import *

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