from celery import shared_task

from booru.models import Post
from booru.automation.tag.tag_automation import TagAutomationRegistry

from .skipper import skip_if_running

@shared_task
def perform_automation(post_id : int, force_perform = False):
    """Performs all automation on a post."""

    # Get the post
    post = Post.objects.get(id=post_id)

    # Get the registry
    registry = TagAutomationRegistry()

    # Perform the automation
    return registry.perform_automation(post=post, force_perform=force_perform)

@shared_task(bind=True)
@skip_if_running
def perform_all_automation(self, force_perform = False):
    """Performs all automation on all posts."""

    # Get all the posts
    posts = Post.objects.all()

    # Perform automation on each post as a subtask
    for post in posts:
        # perform_automation.delay(post.id, force_perform=force_perform)
        perform_automation(post.id, force_perform=force_perform) # Do it without a delay to prevent spamming requests