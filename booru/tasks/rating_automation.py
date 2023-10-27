from celery import shared_task

from booru.automation.rating import perform_automation as perform_rating_automation
from booru.models import Post

from .skipper import skip_if_running

@shared_task
def perform_rating_automation(post_id : int):
    """Performs rating automation on a post."""

    # Get the post
    post = Post.objects.get(id=post_id)

    # Perform the automation
    post.rating = perform_rating_automation(post=post)
    post.save()

@shared_task(bind=True)
@skip_if_running
def perform_all_rating_automation(self):
    """Performs rating automation on all posts."""

    # Get all the posts
    posts = Post.objects.all()

    for post in posts:
        # perform_rating_automation.delay(post.id)
        perform_rating_automation(post.id)