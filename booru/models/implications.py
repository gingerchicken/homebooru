import django.db.models as models

from .tags import Tag
from .posts import Post

class Implication(models.Model):
    """An implication between two tags."""
    
    # The parent tag as a string
    parent = models.CharField(max_length=255)

    # The child tag as a string
    child = models.CharField(max_length=255)

    @property
    def is_usable(self):
        """Is this implication usable - i.e., does the parent tag exist?"""
        return Tag.objects.filter(name=self.parent).exists() 
    
    def apply(self) -> int:
        """Applies the implication to all current posts, returning the number of posts affected."""

        # Ensure that the implication is usable
        if not self.is_usable:
            return 0

        # Select all posts that have the parent tag
        posts = Post.objects.filter(tags__tag=self.parent)
        # If there are no posts, return 0
        if posts.count() == 0:
            return 0

        # Select the posts that do not have the child tag
        posts = posts.exclude(tags__tag=self.child)
        # Verify that there are posts
        if posts.count() == 0:
            return 0

        # Create the child tag
        child_tag = Tag.objects.get_or_create(name=self.child)

        # Add the child tag to all the posts
        for post in posts:
            # Add the child tag
            post.tags.add(child_tag)

            # Update the post
            post.save()

        # TODO Should we recursively apply the implication?
        return len(posts)

    def __str__(self):
        return f"{self.parent} -> {self.child}"
    
    class Meta:
        # The plural name is "Implications"
        verbose_name_plural = "Implications"