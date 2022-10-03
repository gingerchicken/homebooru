from django.db import models
from django.contrib.auth.models import User
from django.apps import apps

from .tags import Tag, TagType
from .posts_search_criteria import *

import homebooru.settings as settings
import booru.boorutils as boorutils
from booru.pagination import Paginator

import math
import pathlib
import shutil
import re

class Rating(models.Model):
    # Name of the rating, this will be the primary key
    name = models.CharField(max_length=20, primary_key=True)

    # Description of the rating, this can be null and by default is blank
    description = models.CharField(max_length=200, blank=True, null=True)

    @staticmethod
    def get_default():
        """Gets the default rating"""
        try:
            return Rating.objects.get(name=settings.BOORU_DEFAULT_RATING_PK)
        except Rating.DoesNotExist:
            return None
    
    def __str__(self):
        return self.name

class Post(models.Model):
    """A post is a picture or video that has been uploaded to the site."""

    # Unique ID for each post
    id = models.AutoField(primary_key=True)

    tags = models.ManyToManyField(Tag, related_name='posts')

    # Rating of the post
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE, null=True)

    # Score (i.e. number of upvotes minus number of downvotes), not null, default 0
    score = models.IntegerField(default=0)

    # Post md5 checksum
    md5 = models.CharField(max_length=32, unique=True)

    # Sample flag (i.e. true when there is a sample for the post - happens when the post is a large image)
    sample = models.BooleanField(default=False)

    # Post folder (which folder in the storage directory the post is stored in) (this is indicated as an integer)
    folder = models.IntegerField()

    # Owner as a user id foreign key
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    # Makes if the post is a video type or not
    is_video = models.BooleanField(default=False)

    # Post width
    width = models.IntegerField()

    # Post height
    height = models.IntegerField()

    # Post timestamp (i.e. when the post was uploaded) (default current timestamp)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Source as a URL to the original post
    source = models.CharField(max_length=1000, blank=True, null=True)

    # File name
    filename = models.CharField(max_length=64)

    # Post title
    title = models.CharField(max_length=512, blank=True, null=True)

    # Post locked
    locked = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """Saves the post to the database."""

        # Make sure that the md5 is lower case
        self.md5 = self.md5.lower()

        # Make sure that the md5 is a valid md5
        if not re.match("^[0-9a-f]{32}$", self.md5):
            raise ValueError("Invalid md5")
        
        # Make sure that the rating is set, if not set it to the default
        if self.rating is None:
            self.rating = Rating.get_default()

        super(Post, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Deletes the post from the database."""

        # Delete the post from the storage directory
        paths = [
            self.get_sample_path(),
            self.get_thumbnail_path(),
            self.get_media_path()
        ]

        for path in paths:
            if not path.exists():
                continue

            # Delete the file
            path.unlink()
        
        # Delete the post from the database
        super(Post, self).delete(*args, **kwargs)

    @staticmethod
    def search(search_phrase, wild_card="*"):
        """Search for posts that match a user entered search phrase"""

        search_criteria = [] 

        # Split the search phrase into words
        words = search_phrase.split()

        # List of accepted parameters
        accepted_params = {
            'md5': str,
            'rating': str,
            'title': str,
            'width': int,
            'height': int,
            'user': int
        }

        # For each word, check if it is a tag
        for word in words:
            # Strip the word of spaces
            word = word.strip()

            # If the word starts with a '-', it is an exclusion
            should_exclude = word[0] == '-'

            # If it is an exclusion, strip the '-'
            if should_exclude:
                word = word[1:]
            
            # Make sure that it isn't empty
            if len(word) == 0:
                continue
            
            potential_param = word.split(':')[0]
            # Handle parameter tags
            if potential_param in accepted_params:
                expected_type = accepted_params[potential_param]

                # Get the value of the parameter
                val = word[len(potential_param) + 1:]

                # Make sure that the value is of the correct type
                try:
                    val = expected_type(val)
                except Exception:
                    if not should_exclude:
                        # They wouldn't find anything if the value is wrong
                        return Post.objects.none()
                    
                    # If it is an exclusion, just continue as this would have had no effect
                    continue

                # Handle the user case
                if potential_param == 'user':
                    # Add the user to the search criteria
                    search_criteria.append(SearchCriteriaExcludeUser(val) if should_exclude else SearchCriteriaUser(val))

                    continue
                
                # Handle the generic cases
                search_criteria.append(
                    SearchCriteriaExcludeParameter(potential_param, val) if should_exclude else SearchCriteriaParameter(potential_param, val)
                )

                continue

            # Handle wild cards
            if wild_card in word:
                r = boorutils.wildcard_to_regex(word, wild_card)

                # Get all of the tags where their names match the regex
                tags = Tag.objects.filter(tag__regex=r)

                # Add the search criteria
                search_criteria.append(SearchCriteriaExcludeWildCardTags(tags) if should_exclude else SearchCriteriaWildCardTags(tags))

                # TODO This is kinda bad because this could cause a lot of queries, maybe consider putting a limit on it or something
                continue
            
            # Handle normal tag case
            # Get the tag by name or if it doesn't exist, make it none
            tag = Tag.objects.filter(tag=word).first()

            # If the tag doesn't exist, return an empty query set
            if tag is None:
                return Post.objects.none()
            
            # Add the criteria to the list
            search_criteria.append(SearchCriteriaExcludeTag(tag) if should_exclude else SearchCriteriaTag(tag))
        
        # These will be the results of the search
        results = Post.objects.all()

        # Go over each of the criteria filter the results
        for criteria in search_criteria:
            # If everything is gone then we can stop
            if results.count() == 0:
                return results
            
            results = criteria.search(results)

        # Sort the results by their id in descending order
        results = results.order_by('-id')

        return results

    @staticmethod
    def get_search_tags(search_result = models.QuerySet(), depth = 512):
        """Get the tags from a search result"""

        # Search result should be a query set of posts

        # Get all of the tags from the posts, each post will have many tags
        # tags = search_result.values_list('tags', flat=True)

        # You see you'd like to think that the top solution would work but it doesn't

        # Create a new empty query set
        tags = {}

        for post in search_result[:depth]:
            for tag in post.tags.all():
                tags[tag.tag] = tag

        # Convert the tags to a list
        tags = list(tags.values())

        # Sort tags by total posts
        tags.sort(key=lambda tag: tag.total_posts, reverse=True)

        return tags

    @staticmethod
    def get_next_folder(folder_size=256):
        """Get the next folder to use for a post"""

        # Get total posts
        total_posts = Post.objects.count()

        # Get the next folder
        return math.ceil(float(total_posts + 1) / float(folder_size))

    def get_sample_path(self):
        """Get the path to the sample image"""

        return settings.BOORU_STORAGE_PATH / self.sample_url
    
    def get_thumbnail_path(self):
        """Get the path to the thumbnail image"""

        return settings.BOORU_STORAGE_PATH / self.thumbnail_url
    
    def get_media_path(self):
        """Get the path to the media file"""

        return settings.BOORU_STORAGE_PATH / self.media_url

    @property
    def sample_url(self):
        return f"samples/{self.folder}/sample_{self.md5}.png"
    
    @property
    def thumbnail_url(self):
        return f"thumbnails/{self.folder}/thumbnail_{self.md5}.png"
    
    @property
    def media_url(self):
        return f"media/{self.folder}/{self.filename}"

    @staticmethod
    def validate_file(file_path : str) -> bool:
        # Checking the file path
        # Get the file as a path
        file_path = pathlib.Path(file_path)

        # Make sure that the file exists
        if not file_path.exists():
            raise Exception("File does not exist")

        # Make sure that it is a file and not a directory
        if not file_path.is_file():
            raise Exception("File is not a file")
        
        # Metadata
        # Get the file extension (without the '.')
        file_extension = file_path.suffix
        if file_extension[0] == '.':
            file_extension = file_extension[1:]

        # Make sure that the file extension is valid
        # TODO do deeper checks here
        if file_extension not in settings.BOORU_ALLOWED_FILE_EXTENSIONS:
            raise Exception("File extension is not valid")
        
        return True

    @staticmethod
    def create_from_file(file_path : str, owner=None):
        """Create a post from a file"""

        # Get the file as a path
        file_path = pathlib.Path(file_path)

        # Make sure that it is valid before doing anything else
        Post.validate_file(file_path)
        
        # TODO size check (i.e. dont kill the server with massive images - make this a setting)

        file_extension = file_path.suffix
        if file_extension[0] == '.':
            file_extension = file_extension[1:]

        # Check if the item is a video
        is_video = file_extension in settings.BOORU_VIDEO_FILE_EXTENSIONS

        # Get the file signature
        md5 = boorutils.get_file_checksum(str(file_path))

        # Get the content dimensions
        (width, height) = boorutils.get_content_dimensions(str(file_path))

        # Creating the post
        # Get the folder to store the file in
        folder = Post.get_next_folder()

        # File paths
        sample_path = settings.BOORU_STORAGE_PATH / f"samples/{folder}/sample_{md5}.png"
        thumb_path  = settings.BOORU_STORAGE_PATH / f"thumbnails/{folder}/thumbnail_{md5}.png"
        image_path  = settings.BOORU_STORAGE_PATH / f"media/{folder}/{md5}.{file_extension}"

        # If these folders don't exist, create them
        for p in [sample_path.parent, thumb_path.parent, image_path.parent]:
            if p.exists(): continue
            
            p.mkdir(parents=True)

        # Create the thumbnail
        boorutils.generate_thumbnail(str(file_path), str(thumb_path))

        # Create the sample
        sampled = boorutils.generate_sample(str(file_path), str(sample_path)) if not is_video else False

        # Copy the file to the image storage
        try:
            shutil.copy(str(file_path), str(image_path))
        except Exception as e:
            # Ignore if it is complaining about it already existing
            pass

        # Create the post
        return Post(
            md5=md5,
            owner=owner,
            width=width,
            height=height,
            folder=folder,
            sample=sampled,
            filename=f"{md5}.{file_extension}",
            is_video=is_video
        )
    
    def get_sorted_tags(self):
        """Gets the tags in a sorted manor"""

        # Firstly, get the tags
        all_tags = self.tags.all()

        # Create an object to store the results
        orders = {
            'types': {},
            'type_orders': []
        }

        # Get the default tag type
        default_type = TagType.get_default()

        # Collect the tag types
        for tag in all_tags:
            t = tag.tag_type

            # Handle None as just the default
            if t is None:
                t = default_type
            
            # It might be still None if the database has no types so we will handle that
            t = t.name if t is not None else 'general'

            # Make sure that t is a string
            t = str(t)

            # Add the tag to the list
            if t not in orders['types']:
                orders['types'][t] = []
            
            # Add the tag to the list
            orders['types'][t].append(tag)
        
        # After we have collected the tags, we can sort them
        # We can sort them in their respective types
        for type_name, tags in orders['types'].items():
            orders['types'][type_name] = sorted(tags, key=lambda tag: tag.tag)
        
        # Now we can sort the types
        orders['type_orders'] = sorted(orders['types'].keys())

        # That is all we need to do
        return orders

    def get_proximate_posts(self, search_results : models.QuerySet):
        """Get the posts that are proximate to this one"""

        # Get the first result where the id is less than this one (i.e. it was added earlier)
        older = search_results.filter(id__lt=self.id).first()

        # Get the second result where the id is greater than this one (i.e. it was added later)
        newer = search_results.filter(id__gt=self.id).last()

        # Return the results
        return {
            'older': older,
            'newer': newer
        }

    @property
    def comments(self):
        """Get the comments for this post"""

        # Get the comments model
        Comment = apps.get_model('booru', 'Comment')

        # Get the comments
        return Comment.objects.filter(post=self)

    # Delete flag
    @property
    def delete_flag(self):
        """Gets if the post is marked for deletion"""
        
        # Get the post flags
        flags = PostFlag.objects.filter(post=self)

        # Return if there are any flags
        return flags.exists()

    class Meta:
        # Create a can lock perm
        permissions = (
            ('lock_post', 'Can lock posts'),
        )

class PostFlag(models.Model):
    """A flag for a post"""

    # The post that was flagged
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    # The user that flagged the post
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # The reason for the flag
    reason = models.TextField(default='')

    # The date the flag was created
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}'s flag for {self.post} ('{self.reason}')"
    
    class Meta:
        # Make sure that only one flag per user per post can exist
        unique_together = ('post', 'user')