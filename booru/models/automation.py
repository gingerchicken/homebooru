import django.db.models as models

from .posts import Post, Rating

class TagAutomationRecord(models.Model):
    """A record of a tag automation's state."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    # The hash of the automation's state
    state_hash = models.CharField(max_length=32)

    # The date the record was created
    performed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post} @ State {self.state_hash}"

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
    prob_x_impl_y = models.FloatField()

    # The probability of y given x
    prob_y_impl_x = models.FloatField()

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
            self.prob_x_impl_y = round(self.prob_x_impl_y)
            self.prob_y_impl_x = round(self.prob_y_impl_x)

        # The probabilities should be between 0 and 1
        self.prob_x_impl_y = max(0, min(1, self.prob_x_impl_y))
        self.prob_y_impl_x = max(0, min(1, self.prob_y_impl_x))

        # Call the parent save method
        super().save(*args, **kwargs)
    
    class Meta:
        # The tag pair must be unique
        unique_together = ('tag_x', 'tag_y')

        # The plural name is "Tag Similarities"
        verbose_name_plural = "Tag similarities"
    
    def __str__(self):
        return f"{self.tag_x} -> {self.tag_y} ({self.prob_x_impl_y}) | {self.tag_y} -> {self.tag_x} ({self.prob_y_impl_x})"

    @staticmethod
    def find_similar(tag : str, critical_region : float) -> list[str]:
        """Returns a list of tags similar to the given tag."""

        # Find all the tags that are above the critical region (either a or b)
        similar_tags = TagSimilarity.objects.filter(
            models.Q(tag_x=tag, prob_x_impl_y__gte=critical_region) |
            models.Q(tag_y=tag, prob_y_impl_x__gte=critical_region)
        )

        # Filter this this to get only the tags include the tag as either x or y
        similar_tags = similar_tags.filter(
            models.Q(tag_x=tag) | models.Q(tag_y=tag)
        )

        # Create the array to store the new tags
        new_tags = []

        # Iterate through the similar tags
        for similar_tag in similar_tags:
            # Check if the tag is x or y
            is_x = similar_tag.tag_x == tag
            is_y = similar_tag.tag_y == tag

            p = 0
            result_tag = None

            # Check if the tag is x or y
            if is_x:
                # Get the probability of y given x
                p = similar_tag.prob_x_impl_y

                # Set the result tag to y
                result_tag = similar_tag.tag_y
            elif is_y:
                # Get the probability of x given y
                p = similar_tag.prob_y_impl_x

                # Set the result tag to x
                result_tag = similar_tag.tag_x

            # If the probability is less than the critical region, then remove it
            if p < critical_region:
                # Skip this tag
                continue

            # Sanity check to make sure that there is a tag
            if result_tag is None:
                # Show a warning
                print(f"Warning: TagSimilarity {similar_tag} has no tag, this should never be reached!")
                
                # Skip this tag
                continue

            # Add the tag to the list
            new_tags.append(result_tag)

        # Return the new tags
        return new_tags

class RatingThreshold(models.Model):
    """A NSFW threshold for rating."""

    # There is a model that returns the probability of a piece of content being NSFW
    # We want to make a threshold such that (threshold >= probability) -> this rating

    # The rating that this threshold is for
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE)

    # The threshold
    threshold = models.FloatField()

    @staticmethod
    def get_rating(nsfw_probability : float):
        """Returns the rating for the given NSFW probability."""

        # Get all the thresholds that are less than or equal to the given probability
        rating_thresholds = RatingThreshold.objects.filter(threshold__lte=nsfw_probability)

        # Get the rating with the highest threshold
        rating_threshold = rating_thresholds.order_by('-threshold').first()

        # Check if there is a rating threshold
        if rating_threshold is None:
            # Return the safe rating
            return Rating.get_default()
        
        # Return the rating
        return rating_threshold.rating

    def __str__(self):
        return f"{self.rating} @ {self.threshold}"
    
class NSFWAutomationRecord(models.Model):
    """A record of a NSFW scan."""

    # The post that was scanned
    post = models.OneToOneField(Post, on_delete=models.CASCADE)

    # The probability of the post being NSFW
    nsfw_probability = models.FloatField()

    # The date the record was created
    performed = models.DateTimeField(auto_now_add=True)

    def get_rating(self):
        """Returns the rating for this record."""

        # Get the rating threshold
        rating_threshold = RatingThreshold.get_rating(self.nsfw_probability)

        # Return the rating
        return rating_threshold

    def __str__(self):
        return f"{self.post} @ {self.nsfw_probability}"

    class Meta:
        # The plural name is "NSFW Automation Records"
        verbose_name_plural = "NSFW automation records"

# Hook into the Post save method to re-add the post to be scanned
from django.db.models.signals import post_save

def post_save_post(sender, instance, created, **kwargs):
    """Removes the post from the automation records."""

    # TODO fix circular import
    from booru.tasks.tag_automation import perform_automation as perform_tag_automation
    from booru.tasks.rating_automation import perform_rating_automation

    # Remove the post from the automation records
    TagAutomationRecord.objects.filter(post=instance).delete()

    # Check if the post was created
    if created:
        # Run the automation task
        # This way we don't have to wait for the next scan but it should get scanned anyway.
        perform_tag_automation.delay(instance.id)
        perform_rating_automation.delay(instance.id)

# Connect the post save signal
post_save.connect(post_save_post, sender=Post)