from django.db import models

from .tags import Tag

# Create your models here.
class Post(models.Model):
    """A post is a picture or video that has been uploaded to the site."""

    # Unique ID for each post
    id = models.AutoField(primary_key=True)

    tags = models.ManyToManyField(Tag, related_name='posts')

    # SFW Rating (either safe, questionable, or explicit) (not null, default safe)
    rating = models.CharField(max_length=10, default='safe')

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
