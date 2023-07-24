from celery import shared_task

# Logger
import logging
logger = logging.getLogger(__name__)

from booru.models import Post, Pool, PoolPost

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