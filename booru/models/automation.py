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
import homebooru.settings

def post_save_post(sender, instance, created, **kwargs):
    """Removes the post from the automation records."""

    # TODO fix circular import
    from booru.tasks.tag_automation import perform_automation as perform_tag_automation
    from booru.tasks.rating_automation import perform_rating_automation

    # Check if the post was created
    if created:
        # Run the automation task
        # This way we don't have to wait for the next scan but it should get scanned anyway.
        perform_tag_automation.delay(instance.id)
        perform_rating_automation.delay(instance.id)

# Connect the post save signal
post_save.connect(post_save_post, sender=Post)