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

class ProfileCreateOrGetTest(TestCase):
    def test_creates(self):
        """Test that it creates a profile for a user"""

        # Create a user
        user = User.objects.create_user(
            username='test',
            password='test'
        )
        user.save()

        # Make sure that there are no profiles for the user
        self.assertFalse(Profile.objects.filter(owner=user).exists())

        # Get the user's profile
        profile = Profile.create_or_get(user)

        # Check that the profile was created
        self.assertTrue(Profile.objects.filter(owner=user).exists())

    def test_gets(self):
        """Test that it gets a profile for a user"""

        # Create a user
        user = User.objects.create_user(
            username='test',
            password='test'
        )
        user.save()

        # Create another user
        user2 = User.objects.create_user(
            username='test2',
            password='test2'
        )
        user2.save()

        # Create a profile for the user
        expected = Profile(owner=user, bio='testing haha')
        expected.save()

        # Get the user's profile
        profile = Profile.create_or_get(user)

        # Check that the profile was retrieved
        self.assertTrue(Profile.objects.filter(owner=user).exists())
        self.assertEqual(profile.owner, user)

        # Check that the profile was retrieved correctly
        self.assertEqual(profile, expected)

    def test_rejects_anon(self):
        """Test that it rejects anon users"""

        # Make sure that an error is raised for anon users
        with self.assertRaises(Exception):
            Profile.create_or_get(None)
        
        with self.assertRaises(Exception):
            p = Profile(owner=None)
            p.save()

class ProfileRecents(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='test',
            password='test'
        )
        self.user.save()

    def assertLimit(self, get_limit, add_post, r=False):
        """Test that it returns the correct number of posts"""

        ps = []

        for i in range(0, 10):
            ps.append(Post(
                md5=boorutils.hash_str(str(i)),
                owner=self.user,
                folder=1,
                width=420,
                height=420
            ))

            ps[i].save()
        
        # Get the user's profile
        profile = Profile.create_or_get(self.user)

        for i in range(0, len(ps)):
            j = len(ps) - i - 1 if r else i
            add_post(profile, ps[j])

        # Get the user's recent uploads
        recent = get_limit(profile)

        # Check that the correct number of posts are returned
        self.assertEqual(len(recent), 5)

        # Check that the correct posts are returned
        ps.reverse()

        for i in range(0, 5):
            self.assertEqual(recent[i], ps[i])
    
    def test_recent_uploads_5(self):
        """Test that it returns the correct number of recent uploads"""
    
        def get_limit(profile):
            return profile.recent_uploads
        
        def add_post(profile, post):
            post.owner = profile.owner
            post.save()

        self.assertLimit(get_limit, add_post)
    
    def test_recent_favourites(self):
        """Test that it returns the correct number of recent favourites"""
    
        def get_limit(profile):
            return profile.recent_favourites
        
        def add_post(profile, post):
            profile.favourites.add(post)
            profile.save()

        self.assertLimit(get_limit, add_post)
