from django.db import models
from django.contrib.auth.models import User

from .posts import Post

class Profile(models.Model):
    # Owner of the profile (User)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)

    # Avatar saved as a post on the site
    avatar = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='avatar')

    # Background post saved as a post on the site
    background = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='background')

    # Profile bio
    bio = models.TextField(max_length=500, blank=True, default='')

    # Favourite posts
    favourites = models.ManyToManyField(Post, blank=True, related_name='favourites')

    @property
    def uploads(self):
        """Get all posts uploaded by the user"""

        # Get the user's posts
        posts = Post.objects.filter(owner=self.owner)

        # Order them with the most recent first (i.e. the highest id first)
        posts = posts.order_by('-id')

        return posts

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
    
    @property
    def recent_uploads(self):
        return self.uploads[:5]
    
    @property
    def recent_favourites(self):
        # Get the favourite posts
        posts = self.favourites.all()

        # TODO this should be ordered by the most recent added to the favourites
        # Order them with the most recent first (i.e. the highest id first)
        posts = posts.order_by('-id')

        # Limit to the first 5
        return posts[:5]