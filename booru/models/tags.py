from django.db import models
from django.apps import apps

class TagType(models.Model):
    # We will use the type name as the primary key
    name = models.CharField(max_length=100, primary_key=True)

    # Description of the tag type
    description = models.CharField(max_length=1000, blank=True, null=True)

class Tag(models.Model):
    # We will use the tag name as the primary key
    tag = models.CharField(max_length=100, primary_key=True)

    # Tag type as a foreign key to the TagType model
    tag_type = models.ForeignKey(TagType, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def total_posts(self):
        """Returns the total number of posts that have this tag."""
        # Get the modes model
        Post = apps.get_model('booru', 'Post')

        # Get all the posts that have this tag
        posts = Post.objects.filter(tags__tag=self.tag)

        # Return the count
        return posts.count()