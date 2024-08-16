from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission

from booru.models.posts import Post, PostFlag
from booru.models.comments import Comment
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
    
    def test_unlock(self):
        # Give user permission to lock posts
        self.user.user_permissions.add(Permission.objects.get(codename='lock_post'))
        self.user.save()

        # Make sure they have the permission
        self.assertTrue(self.user.has_perm('booru.lock_post'))

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Lock the post
        self.post.locked = True
        self.post.save()

        # Get the post
        post = Post.objects.get(id=self.post.id)

        # Check the post was locked
        self.assertTrue(post.locked)

        # Send the request
        resp = self.send_request(self.post.id, locked=False)

        # Check the response status code
        self.assertEqual(resp.status_code, 203, resp.content.decode('utf-8'))

        # Get the post
        post = Post.objects.get(id=self.post.id)

        # Check the post was unlocked
        self.assertFalse(post.locked)

class PostFlagDeleteTest(TestCase):
    temp_storage = testutils.TempStorage()
    
    def givePermissions(self, user):
        # Give them the permission to create post flags
        permission = Permission.objects.get(codename='add_postflag')

        user.user_permissions.add(permission)
        user.save()

        # Reload the user
        user = User.objects.get(id=user.id)
        self.assertTrue(self.user.has_perm('booru.add_postflag'))

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

    def send_request(self, post_id, delete='Some reason'):
        """Sends a request to the post flag delete page"""

        return self.client.post(
            reverse('post_flag', kwargs={'post_id': post_id}), {
                'reason': str(delete)
            }
        )
    
    def test_post_flag_delete_as_anonymous(self):
        """Disallows anonymous users from flagging posts for deletion"""

        # Logout
        self.client.logout()

        # Send the request
        resp = self.send_request(self.post.id)

        # Sends a 403
        self.assertEqual(resp.status_code, 403)

        # Get the post from the database
        post = Post.objects.get(id=self.post.id)

        # Check the post was not flagged for deletion
        self.assertFalse(post.delete_flag)
    
    def test_allows_users_with_perm(self):
        # Give user permission to flag posts for deletion
        self.givePermissions(self.user)

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id)

        # Check the response status code
        self.assertEqual(resp.status_code, 201, resp.content.decode('utf-8'))

        # Get the post again
        post = Post.objects.get(id=self.post.id)

        # Check the post was flagged for deletion
        self.assertTrue(post.delete_flag)

    def test_disallows_without_change_perm(self):
        # Give user permission to flag posts for deletion
        self.givePermissions(self.user)

        # Remove the booru.add_postflag permission
        permission = Permission.objects.get(codename='add_postflag')
        self.user.user_permissions.remove(permission)
        self.user.save()

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id, delete=True)

        # Check the response status code
        self.assertEqual(resp.status_code, 403, resp.content.decode('utf-8'))

        # Get the post
        post = Post.objects.get(id=self.post.id)

        # Check the post was not flagged for deletion
        self.assertFalse(post.delete_flag)

    def test_disallows_without_flag_delete_perm(self):
        """Disallows people who aren't the owner and don't have the flag deletion permission"""

        # Create another user
        user2 = User.objects.create_user(username='test2', password='huevo')
        user2.save()

        # Login
        self.assertTrue(self.client.login(username='test2', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id, delete=True)

        # Check the response status code
        self.assertEqual(resp.status_code, 403, resp.content.decode('utf-8'))

        # Get the post
        post = Post.objects.get(id=self.post.id)

        # Check the post was not flagged for deletion
        self.assertFalse(post.delete_flag)
    
    def test_allows_custom_reason(self):
        """Allows the owner to specify a custom reason for flagging the post for deletion"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Give the user permission to flag posts for deletion
        self.givePermissions(self.user)

        # Save the post
        self.post.save()

        # Send the request
        resp = self.send_request(self.post.id, delete='Custom reason')

        # Check the response status code
        self.assertEqual(resp.status_code, 201)

        # Get the post from the database
        post = Post.objects.get(id=self.post.id)

        # Check the post was flagged for deletion
        self.assertTrue(post.delete_flag)

        # Get the flag
        flag = PostFlag.objects.get(post=self.post)

        # Check that the flag has the correct values
        self.assertEqual(flag.user, self.user)
        self.assertEqual(flag.reason, 'Custom reason')
    
    def test_disallows_two_flags_from_same_user(self):
        """Disallows users from flagging the same post twice"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Give the user permission to flag posts for deletion
        self.givePermissions(self.user)

        # Send the request
        resp = self.send_request(self.post.id, 'first reason')

        # Check the response status code
        self.assertEqual(resp.status_code, 201)

        # Send the request again
        resp = self.send_request(self.post.id, 'second reason')

        # Check the response status code
        self.assertEqual(resp.status_code, 409)

        # Get the post from the database
        post = Post.objects.get(id=self.post.id)

        # Check the post was flagged for deletion
        self.assertTrue(post.delete_flag)

        # Get the flag
        flag = PostFlag.objects.get(post=self.post)

        # Make sure there is only one flag
        self.assertEqual(PostFlag.objects.count(), 1)

        # Check that the flag has the correct values
        self.assertEqual(flag.user, self.user)
        self.assertEqual(flag.reason, 'first reason')

class PostDeleteFlagTest(TestCase):
    """Tests for the post delete flag view"""

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

        # Flag the post for deletion
        self.flag = PostFlag(post=self.post, user=self.user, reason='test')
        self.flag.save()

        # Update the post
        self.post = Post.objects.get(id=self.post.id)

        # Make sure it is flagged for deletion
        self.assertTrue(self.post.delete_flag)
    
    def tearDown(self):
        self.temp_storage.tearDown()

    def send_request(self, post_id):
        """Sends a request to the post delete flag view"""

        # Send the request
        return self.client.delete(
            reverse('post_flag', kwargs={'post_id': post_id})
        )
    
    def givePermissions(self, user):
        """Gives the user permissions to flag posts for deletion"""

        # Give the user permission to flag posts for deletion
        permission = Permission.objects.get(codename='delete_postflag')
        user.user_permissions.add(permission)
        user.save()
    
    def test_disallows_anonymous(self):
        # Send the request
        resp = self.send_request(self.post.id)

        # Sends a 403
        self.assertEqual(resp.status_code, 403)

        # Get the post from the database
        post = Post.objects.get(id=self.post.id)

        # Check the post was not flagged for deletion
        self.assertTrue(post.delete_flag)
    
    def test_disallows_users_without_perm(self):
        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id)

        # Sends a 403
        self.assertEqual(resp.status_code, 403)

        # Get the post from the database
        post = Post.objects.get(id=self.post.id)

        # Check the post was not flagged for deletion
        self.assertTrue(post.delete_flag)

    def test_disallows_users_without_flag_delete_perm(self):
        # Create another user
        user2 = User.objects.create_user(username='test2', password='huevo')
        user2.save()

        # Login
        self.assertTrue(self.client.login(username='test2', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id)

        # Sends a 403
        self.assertEqual(resp.status_code, 403)

        # Get the post from the database
        post = Post.objects.get(id=self.post.id)

        # Check the post was not flagged for deletion
        self.assertTrue(post.delete_flag)
    
    def test_allows_users_with_perm(self):
        # Give the user permission to flag posts for deletion
        self.givePermissions(self.user)

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id)

        # Sends a 201
        self.assertEqual(resp.status_code, 200)

        # Get the post from the database
        post = Post.objects.get(id=self.post.id)

        # Check the post was not flagged for deletion
        self.assertFalse(post.delete_flag)
    
    def test_no_flag(self):
        """Rejects when there is no flag to be deleted"""

        # Remove the flag
        self.flag.delete()

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Give perms
        self.givePermissions(self.user)

        # Send the request
        resp = self.send_request(self.post.id)

        # Sends a 404
        self.assertEqual(resp.status_code, 404)
    
    def test_multiple_flags(self):
        """Deletes only the user's flag"""

        # Create another user
        user2 = User.objects.create_user(username='test2', password='huevo')
        user2.save()

        # Flag the post for deletion
        flag2 = PostFlag(post=self.post, user=user2, reason='test')
        flag2.save()

        # Update the post
        self.post = Post.objects.get(id=self.post.id)

        # Make sure it is flagged for deletion
        self.assertTrue(self.post.delete_flag)

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Give perms
        self.givePermissions(self.user)

        # Send the request
        resp = self.send_request(self.post.id)

        # Sends a 200
        self.assertEqual(resp.status_code, 200)

        # Get the post from the database
        post = Post.objects.get(id=self.post.id)

        # Check that it is still flagged for deletion
        self.assertTrue(post.delete_flag)

        # Check that there is only one flag
        self.assertEqual(PostFlag.objects.count(), 1)

        # Get the last flag
        flag = PostFlag.objects.last()

        # Check that it is the correct one (i.e. the one from the second user)
        self.assertEqual(flag.user, user2)
        self.assertEqual(flag.reason, 'test')

class PostEditRatingTest(TestCase):
    fixtures = ['ratings.json']

    def setUp(self):
        self.temp_storage = testutils.TempStorage()
        self.temp_storage.setUp()

        # Create a user
        self.user = User.objects.create_user(username='test', password='huevo')
        self.user.save()

        # Create a post
        self.post = Post.create_from_file(
            testutils.FELIX_PATH
        )
        self.post.save()

        # Mark the rating as safe
        self.safe = Rating.objects.get(name='safe')
        self.post.rating = self.safe
        self.post.save()

        # Set the owner of the post
        self.post.owner = self.user
        self.post.save()
        
    def tearDown(self):
        self.temp_storage.tearDown()

    def send_request(self, post_id, rating):
        """Sends a request to the post edit rating view"""

        return self.client.post(
            '/post/' + str(post_id), {'rating': rating} 
        )
    
    def test_change_rating(self):
        """Changes the rating of a post"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        post_id = self.post.id

        default_rating = Rating.objects.get(name='safe')

        for rating in Rating.objects.all():
            # Set the post rating
            self.post.rating = default_rating
            self.post.save()

            # Send the request
            resp = self.send_request(post_id, rating.pk)

            # Check the response status code
            self.assertEqual(resp.status_code, 203)

            # Get the post from the database
            post = Post.objects.get(id=post_id)

            # Check the post rating
            self.assertEqual(post.rating, rating)

    def test_disallows_invalid_rating(self):
        """Rejects invalid rating IDs"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        invalid_ratings = ["bababooey", 0, 0.3, True, False]

        for rating in invalid_ratings:
            # Send the request
            resp = self.send_request(self.post.id, rating)

            # Check the response status code
            self.assertEqual(resp.status_code, 400, "Rating: " + str(rating))

            # Get the post from the database
            post = Post.objects.get(id=self.post.id)

            # Check the post rating
            self.assertEqual(post.rating, self.safe)

class PostPostCommentTest(TestCase):
    def setUp(self) -> None:
        self.temp_storage = testutils.TempStorage()
        self.temp_storage.setUp()

        self.user = User.objects.create_user(username='test', password='huevo')
        self.user.save()

        self.post = Post.create_from_file(testutils.FELIX_PATH)
        self.post.save()
    
    def tearDown(self):
        self.temp_storage.tearDown()

    def send_request(self, post_id, comment, as_anonymous = False):
        """Sends a request to the post comment view"""

        # Send the request
        return self.client.post(
            reverse('post_comment', kwargs={'post_id': post_id}),
            {'comment': comment, 'as_anonymous': as_anonymous}
        )
    
    def givePermissions(self, user):
        """Gives the user permissions to comment on posts"""

        # Give the user permission to comment on posts
        permission = Permission.objects.get(codename='add_comment')
        user.user_permissions.add(permission)
        user.save()
    
    def test_disallows_anonymous(self):
        # Set the setting
        homebooru.settings.BOORU_ANON_COMMENTS = False

        # Send the request
        resp = self.send_request(self.post.id, 'test')

        # Sends a 403
        self.assertEqual(resp.status_code, 403)

        # Check that there are no comments
        self.assertEqual(Comment.objects.count(), 0)
    
    def test_disallows_users_without_perm(self):
        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id, 'test')

        # Sends a 403
        self.assertEqual(resp.status_code, 403)

        # Check that there are no comments
        self.assertEqual(Comment.objects.count(), 0)
    
    def test_allows_users_with_perm(self):
        # Give the user permission to comment on posts
        self.givePermissions(self.user)

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id, 'test')

        # Sends a 201
        self.assertEqual(resp.status_code, 201)

        # Check that there is one comment
        self.assertEqual(Comment.objects.count(), 1)

        # Get the comment
        comment = Comment.objects.last()

        # Check that it is correct
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.content, 'test')
    
    def test_no_post(self):
        """Rejects when there is no post to comment on"""

        # Remove the post
        self.post.delete()

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Give perms
        self.givePermissions(self.user)

        # Send the request
        resp = self.send_request(42423, 'test')

        # Sends a 404
        self.assertEqual(resp.status_code, 404)
    
    def test_empty_comment(self):
        """Rejects when the comment is empty"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Give perms
        self.givePermissions(self.user)

        # Send the request
        resp = self.send_request(self.post.id, '')

        # Sends a 400
        self.assertEqual(resp.status_code, 400)

        # Check that there are no comments
        self.assertEqual(Comment.objects.count(), 0)
    
    def test_comment_whitespace(self):
        """Rejects when the comment is only whitespace"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Give perms
        self.givePermissions(self.user)

        # Send the request
        resp = self.send_request(self.post.id, '   ')

        # Sends a 400
        self.assertEqual(resp.status_code, 400)

        # Check that there are no comments
        self.assertEqual(Comment.objects.count(), 0)
    
    def test_strips_whitespace(self):
        """Strips whitespace from the comment"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Give perms
        self.givePermissions(self.user)

        # Send the request
        resp = self.send_request(self.post.id, ' test ')

        # Sends a 201
        self.assertEqual(resp.status_code, 201)

        # Check that there is one comment
        self.assertEqual(Comment.objects.count(), 1)

        # Get the comment
        comment = Comment.objects.last()

        # Check that it is correct
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.content, 'test')
    
    def test_allow_anonymous_setting(self):
        homebooru.settings.BOORU_ANON_COMMENTS = True

        # Send the request
        resp = self.send_request(self.post.id, 'test')

        # Sends a 201
        self.assertEqual(resp.status_code, 201)

        # Check that there is one comment
        self.assertEqual(Comment.objects.count(), 1)

        # Get the comment
        comment = Comment.objects.last()

        # Check that it is correct
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.user, None)
        self.assertEqual(comment.content, 'test')
        self.assertTrue(comment.is_anonymous)

    def test_as_anonymous(self):
        homebooru.settings.BOORU_ANON_COMMENTS = True

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Give perms
        self.givePermissions(self.user)

        # Send the request
        resp = self.send_request(self.post.id, 'test', as_anonymous = True)

        # Sends a 201
        self.assertEqual(resp.status_code, 201)

        # Make sure that the comment is anonymous
        comment = Comment.objects.last()

        self.assertTrue(comment.is_anonymous)
    
    def test_as_anonymous_no_anon(self):
        homebooru.settings.BOORU_ANON_COMMENTS = False

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Give perms
        self.givePermissions(self.user)

        # Send the request
        resp = self.send_request(self.post.id, 'test', as_anonymous = True)

        # Sends a 400
        self.assertEqual(resp.status_code, 403)

        # Make sure that no comment was created
        self.assertEqual(Comment.objects.count(), 0)

class PoolPostPoolTest(TestCase):
    def setUp(self):
        self.temp_storage = testutils.TempStorage()
        self.temp_storage.setUp()

        # Create a user
        self.user = User.objects.create_user(username='test', password='huevo')
        self.user.save()

        # Create a post
        self.post = Post.create_from_file(testutils.FELIX_PATH)
        self.post.save()

        # Create a pool
        self.pool = Pool.objects.create(name='test', creator=self.user)
        self.pool.save()
    
    def tearDown(self):
        self.temp_storage.tearDown()
    
    def givePermissions(self, user):
        """Gives the user the required permissions"""

        for perm_name in ['add_poolpost', 'change_poolpost', 'delete_poolpost']:
            # Get the permission
            perm = Permission.objects.get(codename=perm_name)

            # Give the permission
            user.user_permissions.add(perm)
            user.save()
    
    def send_request(self, post_id, pool_id):
        """Sends a request to the post comment view"""

        # Send the request
        return self.client.post(
            reverse('pool', kwargs={'pool_id': pool_id}),
            {'post': post_id}
        )

    def test_as_anonymous(self):
        """Rejects when the user is anonymous"""

        # Send the request
        resp = self.send_request(self.post.id, self.pool.pk)

        # Sends a 403
        self.assertEqual(resp.status_code, 403)
    
    def test_no_pool(self):
        """Rejects a pool that doesn't exist"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id, 42423)

        # Sends a 404
        self.assertEqual(resp.status_code, 404)
    
    def test_no_post(self):
        """Rejects a post that doesn't exist"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Give perms
        self.givePermissions(self.user)

        # Send the request
        resp = self.send_request(42423, self.pool.pk)

        # Sends a 404
        self.assertEqual(resp.status_code, 404)
    
    def test_no_perms(self):
        """Rejects when the user doesn't have perms"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id, self.pool.pk)

        # Sends a 403
        self.assertEqual(resp.status_code, 403)
    
    def test_add(self):
        """Adds a post to a pool"""

        # Skip this test for now
        self.skipTest('Unable to check worker queue')
        return

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Give perms
        self.givePermissions(self.user)

        # Send the request
        resp = self.send_request(self.post.id, self.pool.pk)

        # Sends a 201
        self.assertEqual(resp.status_code, 201)

        # Check that the post is in the pool
        self.assertTrue(len(self.pool.posts.all()) == 1)
    
    def test_already_exists(self):
        """Rejects when the post is already in the pool"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Give perms
        self.givePermissions(self.user)

        # Add the post to the pool
        PoolPost(pool=self.pool, post=self.post).save()

        # Send the request
        resp = self.send_request(self.post.id, self.pool.pk)

        # Sends a 400
        self.assertEqual(resp.status_code, 409)
    
    def send_remove_request(self, post_id, pool_id):
        """Sends a request to remove a post from a pool"""

        body = {
            'posts': [post_id]
        }

        return self.client.delete(
            reverse('pool', kwargs={'pool_id': pool_id}),
            body,
            content_type='application/json'
        )
    
    def test_remove(self):
        """Removes a post from a pool"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Give perms
        self.givePermissions(self.user)

        # Add the post to the pool
        PoolPost(pool=self.pool, post=self.post).save()

        # Send the request
        resp = self.send_remove_request(self.post.id, self.pool.pk)

        # Sends a 204
        self.assertEqual(resp.status_code, 200)

        # Check that the post is not in the pool
        self.assertTrue(len(self.pool.posts.all()) == 0)
    
    def test_remove_not_in_pool(self):
        """Rejects when the post is not in the pool"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Give perms
        self.givePermissions(self.user)

        # Send the request
        resp = self.send_remove_request(self.post.id, self.pool.pk)

        # Sends a 404
        self.assertEqual(resp.status_code, 404)
    
    def test_remove_no_perms(self):
        """Rejects when the user doesn't have perms"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Add the post to the pool
        PoolPost(pool=self.pool, post=self.post).save()

        # Send the request
        resp = self.send_remove_request(self.post.id, self.pool.pk)

        # Sends a 403
        self.assertEqual(resp.status_code, 403)
    
    def test_remove_as_anonymous(self):
        """Rejects when the user is anonymous"""

        # Add the post to the pool
        PoolPost(pool=self.pool, post=self.post).save()

        # Send the request
        resp = self.send_remove_request(self.post.id, self.pool.pk)

        # Sends a 403
        self.assertEqual(resp.status_code, 403)
    
    def test_remove_no_post(self):
        """Rejects when the post doesn't exist"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Give perms
        self.givePermissions(self.user)

        # Send the request
        resp = self.send_remove_request(42423, self.pool.pk)

        # Sends a 404
        self.assertEqual(resp.status_code, 404)
    
    def test_remove_invalid_post_id(self):
        """Rejects when the post id is invalid"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Give perms
        self.givePermissions(self.user)

        # Send the request
        resp = self.send_remove_request('huevo', self.pool.pk)

        # Sends a 404
        self.assertEqual(resp.status_code, 404)

class PostEditSource(TestCase):
    def setUp(self):
        self.temp_storage = testutils.TempStorage()
        self.temp_storage.setUp()

        # Create a user
        self.user = User.objects.create_user(username='test', password='huevo')
        self.user.save()

        # Create a post
        self.post = Post.create_from_file(testutils.FELIX_PATH)
        self.post.save()

        # Set the post owner
        self.post.owner = self.user
        self.post.save()
    
    def tearDown(self):
        self.temp_storage.tearDown()
    
    def send_request(self, post_id, source):
        """Sends a request to the post source view"""

        # Send the request
        return self.client.post(
            '/post/' + str(post_id), {'source': source} 
        )
    
    def test_updates_source(self):
        """Updates the source of a post"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id, 'https://example.com')

        # Sends a 203
        self.assertEqual(resp.status_code, 203)

        # Get the post from the database
        post = Post.objects.get(id=self.post.id)

        # Check the post source
        self.assertEqual(post.source, 'https://example.com')

        # Change the source once more
        resp = self.send_request(self.post.id, 'https://example2.com')

        # Sends a 203
        self.assertEqual(resp.status_code, 203)

        # Get the post from the database
        post = Post.objects.get(id=self.post.id)

        # Check the post source
        self.assertEqual(post.source, 'https://example2.com')
    
    def test_accepts_empty_string(self):
        """
        Accepts an empty string as the source
        """

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id, '')

        # Sends a 203
        self.assertEqual(resp.status_code, 203)

        # Get the post from the database
        post = Post.objects.get(id=self.post.id)

        # Check the post source
        self.assertEqual(post.source, '')
    
    def test_strips_string(self):
        """
        Automatically strips the source string of whitespace
        """

        whitespaces = [' ', '  ', '   ', '    ', '     ', '\t\n ', '\t\n\t\n', '\t\n\t\n\t\n']

        for whitespace in whitespaces:
            # Login
            self.assertTrue(self.client.login(username='test', password='huevo'))

            # Send the request
            resp = self.send_request(self.post.id, whitespace)

            # Sends a 203
            self.assertEqual(resp.status_code, 203)

            # Get the post from the database
            post = Post.objects.get(id=self.post.id)

            # Check the post source
            self.assertEqual(post.source, '')

class PostEditTags(TestCase):
    def setUp(self):
        self.temp_storage = testutils.TempStorage()
        self.temp_storage.setUp()

        # Create a user
        self.user = User.objects.create_user(username='test', password='huevo')
        self.user.save()

        # Create a post
        self.post = Post.create_from_file(testutils.FELIX_PATH)
        self.post.save()

        # Add a tag to the post
        self.post.tags.add(Tag.create_or_get('felix_argyle'))
        self.post.save()

        # Set the post owner
        self.post.owner = self.user
        self.post.save()
    
    def tearDown(self):
        self.temp_storage.tearDown()
    
    def send_request(self, post_id, tags):
        """Sends a request to the post tags view"""

        # Send the request
        return self.client.post(
            reverse('view', kwargs={'post_id': post_id}),
            {'tags': tags}
        )

    def test_updates_tags(self):
        """Overwrites the tags of a post"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id, 'catboy')

        # Sends a 203
        self.assertEqual(resp.status_code, 203)

        # Get the post from the database
        post = Post.objects.get(id=self.post.id)

        # Check the post tags
        self.assertEqual(post.tags.count(), 1)
        self.assertEqual(post.tags.first().tag, 'catboy')
    
    def test_allows_appending_tags(self):
        """Accepts a list of tags that contain existing post tags"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id, 'felix_argyle catboy')

        # Sends a 203
        self.assertEqual(resp.status_code, 203)

        # Get the post from the database
        post = Post.objects.get(id=self.post.id)

        # Check the post tags
        self.assertEqual(post.tags.count(), 2)
        self.assertEqual(set([tag.tag for tag in post.tags.all()]), {'felix_argyle', 'catboy'})

    def test_rejects_no_tags(self):
        """Rejects when there are no tags"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id, '')

        # Sends a 400
        self.assertEqual(resp.status_code, 400)

        # Get the post from the database
        post = Post.objects.get(id=self.post.id)

        # Check the post tags
        self.assertEqual(post.tags.count(), 1)
        self.assertEqual(post.tags.first().tag, 'felix_argyle')
    
    def test_rejects_invalid_tags(self):
        """Rejects when the tags are invalid"""

        invalid_tags = ['a' * 1000, 'md5:1234567890abcdef1234567890abcdef']
        valid_tags = ['cute', '^_^', ':3']

        # Compute every combination of invalid and valid tags
        for invalid_tag in invalid_tags:
            for valid_tag in valid_tags:
                # Login
                self.assertTrue(self.client.login(username='test', password='huevo'))

                # Send the request
                resp = self.send_request(self.post.id, f'{invalid_tag} {valid_tag}')

                # Sends a 400
                self.assertEqual(resp.status_code, 400)

                # Get the post from the database
                post = Post.objects.get(id=self.post.id)

                # Check the post tags
                self.assertEqual(post.tags.count(), 1)
                self.assertEqual(post.tags.first().tag, 'felix_argyle')
        
        # Only invalid tags
        for invalid_tag in invalid_tags:
            # Login
            self.assertTrue(self.client.login(username='test', password='huevo'))

            # Send the request
            resp = self.send_request(self.post.id, invalid_tag)

            # Sends a 400
            self.assertEqual(resp.status_code, 400)

            # Get the post from the database
            post = Post.objects.get(id=self.post.id)

            # Check the post tags
            self.assertEqual(post.tags.count(), 1)
            self.assertEqual(post.tags.first().tag, 'felix_argyle')
    
    def test_handles_duplicate_tags(self):
        """Ignores second interation of tag in list"""

        # Login
        self.assertTrue(self.client.login(username='test', password='huevo'))

        # Send the request
        resp = self.send_request(self.post.id, 'catboy felix_argyle catboy')

        # Sends a 203
        self.assertEqual(resp.status_code, 203)

        # Get the post from the database
        post = Post.objects.get(id=self.post.id)

        # Check the post tags
        self.assertEqual(post.tags.count(), 2)
        self.assertEqual(set([tag.tag for tag in post.tags.all()]), {'felix_argyle', 'catboy'})