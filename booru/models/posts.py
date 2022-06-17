from django.db import models

from .tags import Tag, TagType

import homebooru.settings as settings
import booru.boorutils as boorutils

import math
import pathlib
import shutil
import re

# Create your models here.
class Post(models.Model):
    """A post is a picture or video that has been uploaded to the site."""

    # Unique ID for each post
    id = models.AutoField(primary_key=True)

    tags = models.ManyToManyField(Tag, related_name='posts')

    # SFW Rating (either safe, questionable, or explicit) (not null, default safe)
    rating = models.CharField(max_length=64, default='safe')

    # Score (i.e. number of upvotes minus number of downvotes), not null, default 0
    score = models.IntegerField(default=0)

    # Post md5 checksum
    md5 = models.CharField(max_length=32, unique=True)

    # Sample flag (i.e. true when there is a sample for the post - happens when the post is a large image)
    sample = models.BooleanField(default=False)

    # Post folder (which folder in the storage directory the post is stored in) (this is indicated as an integer)
    folder = models.IntegerField()

    # Owner as a user id foreign key, but for now we will just store the owner as a string
    # TODO add foreign key to user table
    owner = models.CharField(max_length=100, blank=True, null=True)

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

    def save(self, *args, **kwargs):
        """Saves the post to the database."""

        # Make sure that the md5 is lower case
        self.md5 = self.md5.lower()

        # Make sure that the md5 is a valid md5
        if not re.match("^[0-9a-f]{32}$", self.md5):
            raise ValueError("Invalid md5")

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
                
            # Handle wild cards
            if wild_card in word:
                r = word

                # Regex escape the all of the characters, unless it is a wild card
                escaped = ''
                for c in r:
                    if c == wild_card:
                        escaped += c
                        continue
                    
                    # Escape the character but if it is a number don't make it the character code
                    if c.isdigit() or c.isalpha():
                        escaped += f"[{c}]"
                        continue
                        
                    # Escape the character as a character code
                    escaped += '\\' + c
                
                r = escaped.replace(wild_card, '.*')

                # Get all of the tags where their names match the regex
                tags = Tag.objects.filter(tag__regex=r)

                # Add the search criteria
                search_criteria.append(SearchCriteriaExcludeWildCardTags(tags) if should_exclude else SearchCriteriaWildCardTags(tags))

                # TODO This is kinda bad because this could cause a lot of queries, maybe consider putting a limit on it or something
            else:
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

        return settings.BOORU_STORAGE_PATH / f"samples/{self.folder}/sample_{self.md5}.jpg"
    
    def get_thumbnail_path(self):
        """Get the path to the thumbnail image"""

        return settings.BOORU_STORAGE_PATH / f"thumbnails/{self.folder}/thumbnail_{self.md5}.jpg"
    
    def get_media_path(self):
        """Get the path to the media file"""

        return settings.BOORU_STORAGE_PATH / f"media/{self.folder}/{self.filename}"

    @staticmethod
    def create_from_file(file_path : str, owner=None):
        """Create a post from a file"""

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
        
        # TODO size check (i.e. dont kill the server with massive images - make this a setting)

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
        sample_path = settings.BOORU_STORAGE_PATH / f"samples/{folder}/sample_{md5}.jpg"
        thumb_path  = settings.BOORU_STORAGE_PATH / f"thumbnails/{folder}/thumbnail_{md5}.jpg"
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


# Search criteria for the post search

class SearchCriteria:
    """Interface for creating search criteria"""

    def __init__(self) -> None:
        pass

    def search(self, s) -> models.QuerySet:
        return s

class SearchCriteriaTag(SearchCriteria):
    """Used to search for posts that contain a certain tag"""

    def __init__(self, tag: Tag) -> None:
        self.tag = tag

    def search(self, s) -> models.QuerySet:
        return s.filter(tags=self.tag)

class SearchCriteriaExcludeTag(SearchCriteria):
    """Used to exclude tags from a search"""

    def __init__(self, tag: Tag) -> None:
        self.tag = tag

    def search(self, s) -> models.QuerySet:
        return s.exclude(tags=self.tag)

class SearchCriteriaWildCardTags(SearchCriteria):
    """Used to search for posts that contain a certain tag"""

    def __init__(self, tags: [Tag]) -> None:
        self.tags = tags

    def search(self, s) -> models.QuerySet:
        # It must include at least one of the tags, without duplicates
        return s.filter(tags__in=self.tags).distinct('id')

class SearchCriteriaExcludeWildCardTags(SearchCriteria):
    """Used to exclude tags from a search"""

    def __init__(self, tags: [Tag]) -> None:
        self.tags = tags

    def search(self, s) -> models.QuerySet:
        return s.exclude(tags__in=self.tags).distinct('id')
