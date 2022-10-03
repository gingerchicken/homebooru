from django.test import TestCase
from django.contrib.auth.models import User

from booru.models.profile import Profile
from booru.models.comments import Comment
from booru.models.posts import Post
import booru.tests.testutils as testutils

class CommentStrTest(TestCase):
    """Tests the __str__ method of the Comment model"""

    def test_str(self):
        """Returns expected string"""

        # Create a comment
        comment = Comment(content="Test comment")

        # Check the string
        self.assertEqual(str(comment), "Test comment")

class CommentIsAnonymous(TestCase):
    """Tests the is_anonymous property of the Comment model"""

    def setUp(self):
        # Create a user
        self.user = User(username="TestUser", password="TestPassword")
        self.user.save()

        # Create a post
        self.post = Post.create_from_file(testutils.GATO_PATH)
        self.post.save()

    def test_is_anonymous(self):
        """Returns True if the comment is anonymous"""

        # Create an anonymous comment
        comment = Comment(post=self.post)

        # Check the property
        self.assertTrue(comment.is_anonymous)

    def test_is_not_anonymous(self):
        """Returns False if the comment is not anonymous"""

        # Create a comment
        comment = Comment(user=self.user, post=self.post)

        # Check the property
        self.assertFalse(comment.is_anonymous)
    
    def test_is_anonymous_deleted_user(self):
        """Returns True if the user is deleted"""

        # Create a comment
        comment = Comment(user=self.user, post=self.post)
        comment.save()

        # Delete the user
        self.user.delete()

        # See if the comment exists
        comment = Comment.objects.filter(id=comment.id).first()

        # Make sure that it is none
        self.assertIsNone(comment)

class CommentProfileTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User(username="TestUser", password="TestPassword")
        self.user.save()

        # Create a post
        self.post = Post.create_from_file(testutils.GATO_PATH)
        self.post.save()

        # Create comment
        self.comment = Comment(post=self.post, content="Test comment")
        self.comment.save()
    
    def test_when_anonymous(self):
        """Returns None if the comment is anonymous"""

        # Create an anonymous comment
        comment = Comment(post=self.post)

        # Check the property
        self.assertIsNone(comment.profile)
    
    def test_when_not_anonymous(self):
        """Returns the profile of the user who created the comment"""

        # Create a comment
        comment = Comment(user=self.user, post=self.post)
        comment.save()

        # Check the property
        self.assertEqual(comment.profile.owner, self.user)
    
    def test_gets_profile(self):
        """Gets the profile if it exists"""

        # Create a profile
        profile = Profile(owner=self.user)
        profile.save()

        # Set the bio property
        profile.bio = "Test bio"
        profile.save()

        # Create a comment
        comment = Comment(user=self.user, post=self.post)
        comment.save()

        # Check the property
        self.assertEqual(comment.profile.bio, "Test bio")