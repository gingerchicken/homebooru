import django.db.models as models
from django.contrib.auth.models import User

from .posts import Post
from .profile import Profile

class Comment(models.Model):
    """A comment on a post"""

    # The post the comment is on
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    # The comment text
    content = models.TextField()
    
    # The date the comment was created
    created = models.DateTimeField(auto_now_add=True)

    # The user who created the comment
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.content
    
    @property
    def is_anonymous(self):
        """Returns True if the comment is anonymous"""

        return self.user is None
    
    @property
    def profile(self):
        """Returns the profile of the user who created the comment"""

        # Make sure it isn't anonymous
        if self.is_anonymous:
            return None

        # Return the profile
        return Profile.create_or_get(self.user)