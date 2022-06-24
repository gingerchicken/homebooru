from django.db import models
from django.apps import apps

import homebooru.settings
import booru.boorutils as boorutils

class TagType(models.Model):
    """Describes what a tag's category is."""

    # We will use the type name as the primary key
    name = models.CharField(max_length=100, primary_key=True)

    # Description of the tag type
    description = models.CharField(max_length=1000, blank=True, null=True)

    @staticmethod
    def get_default():
        """Get the default tag type."""
        try:
            return TagType.objects.get(name=homebooru.settings.BOORU_DEFAULT_TAG_TYPE_PK)
        except TagType.DoesNotExist:
            # This should never happen unless the database is completely broken
            return None
    
    def __str__(self):
        """Returns the tag type's name."""
        return self.name

class Tag(models.Model):
    """Used to tag posts."""

    # We will use the tag name as the primary key
    tag = models.CharField(max_length=100, primary_key=True)

    # Tag type as a foreign key to the TagType model
    tag_type = models.ForeignKey(TagType, on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        """Saves the tag."""

        # If the tag type is not set, set it to the default
        if not self.tag_type:
            self.tag_type = TagType.get_default()
        
        super().save(*args, **kwargs)

    @property
    def total_posts(self):
        """Returns the total number of posts that have this tag."""
        # Get the modes model
        Post = apps.get_model('booru', 'Post')

        # Get all the posts that have this tag
        posts = Post.objects.filter(tags__tag=self.tag)

        # Return the count
        return posts.count()
    
    @staticmethod
    def create_or_get(tag):
        """Creates a tag if it doesn't exist, or returns the existing tag."""

        # Store the tag
        t = None

        # Check if the tag exists
        if Tag.objects.filter(tag=tag).exists():
            # Get the tag
            t = Tag.objects.get(tag=tag)
        else:
            # Create the tag
            t = Tag(tag=tag)
            t.save()
        
        # Return the tag
        return t
    
    @staticmethod
    def is_name_valid(name : str) -> bool:
        """Checks if the name is valid."""

        # Check if the name is valid
        if len(name) > 100:
            return False
        
        # Check that it is at least two characters long
        if len(name) < 2:
            return False
        
        # Check if it contains spaces
        if ' ' in name:
            return False
        
        # Check if it contains wildcards
        if '*' in name:
            return False
        
        # Check if it contains -
        if '-' in name:
            return False

        # Check that it is lowercase
        if name != name.lower():
            return False

        # Make sure that they don't start with an attribute
        potential_attribute = name.split(':')[0]
        disallowed_params = {
            'md5': True,
            'rating': True,
            'title': True,
            'width': True,
            'height': True
        }

        if potential_attribute in disallowed_params:
            return False

        # All checks passed
        return True
    
    def __str__(self):
        """Returns the tag's name."""

        return self.tag

    def search(phase : str, sort_param : str = "tag", order : str = "ascending", wild_card : str = "*") -> list:
        """Searches for tags."""

        # Check that the order is valid
        if order not in ["ascending", "descending"]:
            raise ValueError("Invalid order")

        # If the phrase is empty, return all tags
        if phase == "":
            return Tag.objects.all()

        # Make sure that the sort_param is valid
        if sort_param not in ["tag", "total_posts", "type"]:
            raise ValueError("Invalid sort parameter")

        # If the tag contains spaces, return nothing
        if ' ' in phase:
            return Tag.objects.none()
        
        qs = Tag.objects.all()

        # Handle wildcards
        if wild_card in phase:
            regex = boorutils.wildcard_to_regex(phase, wildcard=wild_card)

            qs = qs.filter(tag__regex=regex)
        else:
            # Search for where the tag's name is equal to the phase
            qs = qs.filter(tag=phase)

        # Sort the tags
        if sort_param != "total_posts":
            if sort_param == "type":
                sort_param = "tag_type__name"

            p = sort_param if order == "ascending" else "-" + sort_param

            qs = qs.order_by(p)
        else:
            # This is slightly different as this is a functional attribute within the Python model
            # TODO this is a repeated line, fix it
            p = sort_param if order == "ascending" else "-" + sort_param

            qs = qs.annotate(total_posts=models.Count('posts')).order_by(p)
        
        # Return the tags
        return qs