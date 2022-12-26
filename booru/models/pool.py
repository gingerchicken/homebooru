import django.db.models as models
from django.apps import apps
from django.contrib.auth.models import User

from .posts import Post

class Pool(models.Model):
    # Pool name
    name = models.CharField(max_length=255)

    # Pool description
    description = models.TextField()

    # Pool creator
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    # Pool creation date
    created_at = models.DateTimeField(auto_now_add=True)

    # Public 
    public = models.BooleanField(default=True)

    @property
    def posts(self):
        # Get the PoolPost object
        PoolPost = apps.get_model('booru', 'PoolPost')

        # Get all the posts in the pool
        posts = PoolPost.objects.filter(pool=self).order_by('added_at')

        # Return the posts
        return posts
    
    def __str__(self):
        return self.name

class PoolPost(models.Model):
    # Pool
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE)

    # Post
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    # Date added
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('pool', 'post')