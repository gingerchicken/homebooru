from celery import shared_task

from booru.automation.rating import perform_automation
from booru.models import Post

from .skipper import skip_if_running

@shared_task
def perform_rating_automation(post_id : int):
    """Performs rating automation on a post."""

    # TODO This can create duplicate keys as it is called on save too!
    # django.db.utils.IntegrityError: duplicate key value violates unique constraint "booru_nsfwautomationrecord_post_id_key"

    # Get the post
    post = Post.objects.get(id=post_id)

    # Perform the automation
    predicted_rating = perform_automation(post=post)
    
    # Check if the predicted rating is None
    if predicted_rating == None:
        return
    
    # Update the post rating
    post.rating = predicted_rating
    post.save()

    return str(predicted_rating)

@shared_task(bind=True)
@skip_if_running
def perform_all_rating_automation(self):
    """Performs rating automation on all posts."""

    # Get all the posts
    posts = Post.objects.all()

    for post in posts:
        # perform_rating_automation.delay(post.id)
        perform_rating_automation(post.id)