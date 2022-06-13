from django.db import models

from .tags import Tag

# Create your models here.
class Post(models.Model):
    # Unique ID for each post
    id = models.AutoField(primary_key=True)

    tags = models.ManyToManyField(Tag, related_name='posts')

    # SFW Rating (either safe, questionable, or explicit) (not null, default safe)
    rating = models.CharField(max_length=10, default='safe')

    # Score (i.e. number of upvotes minus number of downvotes), not null, default 0
    score = models.IntegerField(default=0)

    # Post md5 checksum
    md5 = models.CharField(max_length=32, unique=True)

    # Sample flag (i.e. true when there is a sample for the post - happens when the post is a large image)
    sample = models.BooleanField(default=False)

    # Post folder (which folder in the storage directory the post is stored in) (this is indicated as an integer)
    folder = models.IntegerField()

    # Owner as a user id foreign key, but for now we will just store the owner as a string
    # TODO add foreign key to user table
    owner = models.CharField(max_length=100, blank=True, null=True)

    # Makes if the post is a video type or not
    is_video = models.BooleanField(default=False)

    # Post width
    width = models.IntegerField()

    # Post height
    height = models.IntegerField()

    # Post timestamp (i.e. when the post was uploaded) (default current timestamp)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Source as a URL to the original post
    source = models.CharField(max_length=1000, blank=True, null=True)
