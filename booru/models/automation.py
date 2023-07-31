import django.db.models as models

from .posts import Post

class TagAutomationRecord(models.Model):
    """A record of a tag automation's state."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    # The hash of the automation's state
    state_hash = models.CharField(max_length=32)

    # The date the record was created
    performed = models.DateTimeField(auto_now_add=True)

    # The post must be unique
    class Meta:
        unique_together = ('post', 'state_hash')