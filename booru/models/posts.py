from django.db import models

from .tags import Tag

# Create your models here.
class Post(models.Model):
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
        to_include = []
        to_exclude = []

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

            tags = None

            # Handle wild cards
            if wild_card in word:
                r = word

                # Regex escape the all of the characters, unless it is a wild card
                escaped = ''
                for c in r:
                    if c == wild_card:
                        escaped += c
                        continue
                    
                    escaped += f"[{c}]"
                
                r = escaped.replace(wild_card, '.*')

                # Get all of the tags where their names match the regex
                tags = Tag.objects.filter(tag__regex=r)

                # TODO we need to check that it includes at least one of these tags

                # This is kinda bad because this could cause a lot of queries, maybe consider putting a limit on it or something
            else:
                # Get the tag by name or if it doesn't exist, make it none
                tag = Tag.objects.filter(tag=word).first()

                # If the tag doesn't exist, return an empty query set
                if tag is None:
                    return Post.objects.none()
                
                tags = [tag]

            # If it is an exclusion, add the tag to the exclusion list
            for tag in tags:
                if should_exclude:
                    to_exclude.append(tag)
                    continue

                # Otherwise, add it to the inclusion list
                to_include.append(tag)
        
        # If both are empty, return all posts
        if len(to_include) == 0 and len(to_exclude) == 0:
            return Post.objects.all()
        
        posts = Post.objects.exclude(tags__in=to_exclude)

        for tag in to_include:
            posts = posts.filter(tags=tag)
        
        return posts
