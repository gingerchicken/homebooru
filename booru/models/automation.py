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

class TagSimilarity(models.Model):
    """Bi-directional tag similarity."""

    # The first tag (string)
    tag_x = models.CharField(max_length=255)

    # The second tag (string)
    tag_y = models.CharField(max_length=255)

    # The probability of x given y
    prob_x_given_y = models.FloatField()

    # The probability of y given x
    prob_y_given_x = models.FloatField()

    # The number of times x and y have been seen together
    occurrence = models.IntegerField()

    # Was this given manually?
    manual = models.BooleanField(default=True)

    # Override the save method to ensure that the tags are always in the same order
    def save(self, *args, **kwargs):

        # Ensure that the tags are always in the same order
        [self.tag_x, self.tag_y] = sorted([self.tag_x, self.tag_y])

        # If manual is set to True, then the probabilities should be 1 or 0
        # Round them to the nearest integer
        if self.manual:
            self.prob_x_given_y = round(self.prob_x_given_y)
            self.prob_y_given_x = round(self.prob_y_given_x)

        # The probabilities should be between 0 and 1
        self.prob_x_given_y = max(0, min(1, self.prob_x_given_y))
        self.prob_y_given_x = max(0, min(1, self.prob_y_given_x))

        # Call the parent save method
        super().save(*args, **kwargs)
    
    class Meta:
        # The tag pair must be unique
        unique_together = ('tag_x', 'tag_y')

        # The plural name is "Tag Similarities"
        verbose_name_plural = "Tag Similarities"
    
    def __str__(self):
        return f"{self.tag_x} -> {self.tag_y} ({self.prob_x_given_y}) | {self.tag_y} -> {self.tag_x} ({self.prob_y_given_x})"