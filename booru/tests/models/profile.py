from django.test import TestCase
from django.contrib.auth.models import User

from ...models.posts import Post, Rating
from ...models.profile import Profile
import booru.boorutils as boorutils

class ProfileUploadsTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='test',
            password='test'
        )
        self.user.save()

        # Create another user
        self.user2 = User.objects.create_user(
            username='test2',
            password='test2'
        )
        self.user2.save()

        # Create a post
        self.post = Post.objects.create(
            md5=boorutils.hash_str("test"),
            owner=self.user,
            folder=1,
            width=420,
            height=420
        )
        self.post.save()

        # Create another post
        self.post2 = Post.objects.create(
            md5=boorutils.hash_str("test2"),
            owner=self.user2,
            folder=1,
            width=420,
            height=420
        )
        self.post2.save()

        # Create another post
        self.post3 = Post.objects.create(
            md5=boorutils.hash_str("test3"),
            owner=self.user,
            folder=1,
            width=420,
            height=420
        )
        self.post3.save()

    def test_profile_uploads(self):
        """Test that it returns all user posts"""

        # Get the user's profile
        profile = Profile.create_or_get(self.user)

        # Get all posts uploaded by the user
        uploads = profile.uploads

        # Check that the correct posts are returned
        self.assertEqual(uploads.count(), 2)

        # Check that the correct post is returned, with the most recent first
        self.assertEqual(uploads.first(), self.post3)
        self.assertEqual(uploads.last(), self.post)
    
    def test_empty_case(self):
        """Test that it returns an empty list if the user has no posts"""

        # Create a fresh user
        user = User.objects.create_user(
            username='garry',
            password='garryisawesome'
        )

        # Get the user's profile
        profile = Profile.create_or_get(user)

        # Get all posts uploaded by the user
        uploads = profile.uploads

        # Check that the correct posts are returned
        self.assertEqual(uploads.count(), 0)