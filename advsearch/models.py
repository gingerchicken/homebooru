from django.db import models

import blogic.evaluator

from booru.models import Post, Tag

# Create your models here.
def search_posts(phrase : str):
    """Search for posts based on a phrase"""

    # Get the truth table
    truth_table = blogic.evaluator.evaluate_all(phrase)

    # Check for all True cases
    true_only = []
    for row in truth_table:
        [inputs, output] = row

        # Check if all inputs are True
        if output:
            true_only.append(inputs)
    
    # Check if it is a tautology 
    if len(true_only) == len(truth_table):
        # Return all images
        return Post.objects.all()
    
    # Check if it is a contradiction
    if len(true_only) == 0:
        # Return no images
        return Post.objects.none()

    # Get the posts
    posts = Post.objects.none()

    tags = {}

    def get_cached_tag(tag : str):
        if tag not in tags:
            tags[tag] = Tag.objects.get(tag=tag)
        
        return tags[tag]

    for row in true_only:
        # Get the different tags
        true_tags  = [] # Positive tags
        false_tags = [] # Negative tags

        # Get the true and false tags
        for i, raw_tag in enumerate(row):
            value = row[raw_tag]

            # Append it to the correct list
            (true_tags if value else false_tags).append(raw_tag)
        
        # Get the current posts
        current_posts = Post.objects.all()

        # Filter the posts
        for tag in true_tags:
            try:
                current_posts = current_posts.filter(tags=get_cached_tag(tag))
            except Tag.DoesNotExist:
                # Clear the posts
                current_posts = Post.objects.none()
                break
        
        # Make sure that we have posts
        if current_posts.count() > 0:
            # Remove the false tags
            for tag in false_tags:
                try:
                    current_posts = current_posts.exclude(tags=get_cached_tag(tag))
                except Tag.DoesNotExist:
                    pass # Ignore, no effect
        
        # Append the newly found posts
        posts = posts | current_posts
    
    return posts