from celery import shared_task

# Logger
import logging
logger = logging.getLogger(__name__)

from booru.models import Post, Pool, PoolPost

# TODO you might want to make a file for each different category of tasks

# Pool tasks
@shared_task
def create_pool_posts(pool_id : int, posts_ids : list):
    """Creates the pool posts for the given pool and posts"""

    # Get the pool
    pool = Pool.objects.get(id=pool_id)

    # Get the posts
    posts = Post.objects.filter(id__in=posts_ids)

    # TODO if this is a range then we could do a bulk create

    for post in posts:
        # Check if it already exists in the pool
        if PoolPost.objects.filter(pool=pool, post=post).exists():
            continue # Skip this post

        # Create a post pool
        pool_post = PoolPost(
            pool=pool,
            post=post
        )
        pool_post.save()

@shared_task
def create_pool_posts_range(pool_id : int, start_id : int, end_id : int):
    """Creates the pool posts for the given pool and posts"""

    # Get the pool
    pool = Pool.objects.get(id=pool_id)

    # Get the posts
    posts = Post.objects.filter(id__range=(start_id, end_id))

    # Remove the posts that already exist in the pool
    posts = posts.exclude(id__in=PoolPost.objects.filter(pool=pool).values_list('post_id', flat=True))

    # Create the pool posts
    pool_posts = []

    for post in posts:
        # Create a post pool
        pool_post = PoolPost(
            pool=pool,
            post=post
        )
        pool_posts.append(pool_post)

    # Bulk create
    PoolPost.objects.bulk_create(pool_posts)

# Automation tasks
from booru.automation.tag_automation import TagAutomationRegistry

@shared_task
def perform_automation(post_id : int, force_perform = False):
    """Performs all automation on a post."""

    # Get the post
    post = Post.objects.get(id=post_id)

    # Get the registry
    registry = TagAutomationRegistry()

    # Perform the automation
    registry.perform_automation(post=post, force_perform=force_perform)

@shared_task
def perform_all_automation(force_perform = False):
    """Performs all automation on all posts."""

    # Get all the posts
    posts = Post.objects.all()

    # Perform automation on each post as a subtask
    for post in posts:
        # perform_automation.delay(post.id, force_perform=force_perform)
        perform_automation(post.id, force_perform=force_perform) # Do it without a delay to prevent spamming requests