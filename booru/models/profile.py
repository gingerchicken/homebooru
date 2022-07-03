from django.db import models
from django.contrib.auth.models import User

from .posts import Post

class Profile(models.Model):
    # Owner of the profile (User)
    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    # Avatar saved as a post on the site
    avatar = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, related_name='avatar')

    # Background post saved as a post on the site
    background = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, related_name='background')

    # Profile bio
    bio = models.TextField(max_length=500, blank=True, default='')

    # Favourite posts
    favourites = models.ManyToManyField(Post, blank=True, related_name='favourites')

    @property
    def uploads(self):
        """Get all posts uploaded by the user"""
        return Post.objects.filter(owner=self.owner)
    
    @staticmethod
    def create_or_get(user : User):
        """Get or create a profile for a user"""

        profile = None

        if Profile.objects.filter(owner=user).exists():
            profile = Profile.objects.get(owner=user)
        else:
            profile = Profile(owner=user)
            profile.save()

        # Return the profile
        return profile