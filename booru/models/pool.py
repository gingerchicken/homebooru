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
        posts = PoolPost.objects.filter(pool=self).order_by('display_order')

        # Return the posts
        return posts
    
    def __str__(self):
        return self.name
    
    @staticmethod
    def search(phrase : str()):
        """Searches for all pools that include the phrase in their name or description"""

        if phrase is None or phrase == "":
            return Pool.objects.all().order_by('-created_at')
        
        # Try to convert the phrase to an integer
        potential_pk = None
        try:
            potential_pk = int(phrase)
        except ValueError:
            potential_pk = -1

        # Get the pools that include the phrase in their name or description or if the primary key is the phrase
        pools = Pool.objects.filter(
            models.Q(name__icontains=phrase)
            | models.Q(description__icontains=phrase)
            | models.Q(pk=potential_pk)
            | models.Q(creator__username__icontains=phrase)
        )

        # Order the pools by creation date
        pools = pools.order_by('-created_at')

        # Return the pools
        return pools

class PoolPost(models.Model):
    # Pool
    pool = models.ForeignKey(Pool, on_delete=models.CASCADE)

    # Post
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    # Order
    display_order = models.IntegerField(null=True, blank=True)

    def get_next_order_number(self):

        # TODO why don't you just use auto increment?

        # Get all of the pool posts in the pool
        pool_posts = PoolPost.objects.filter(pool=self.pool)

        # Get the last pool post
        last_pool_post = pool_posts.last()

        # If there is no last pool post, return 0
        if last_pool_post is None:
            return 0

        # Return the last pool post's display order + 1
        return last_pool_post.display_order + 1

    # Override the save method
    def save(self, *args, **kwargs):
        # Check if the display order is not set
        if self.display_order is None:
            # Get the next order number
            self.display_order = self.get_next_order_number()
        
        # Call the super method
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('pool', 'post')