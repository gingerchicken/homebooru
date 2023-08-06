from .tag_automation import TagAutomation
from booru.models import Post, Tag

class TagmeTagAutomation(TagAutomation):
    """Tagme tag automation"""

    def __init__(self, order_override: int = None):
        super().__init__(order_override)

    def get_tags(self, post : Post) -> list[Tag]:
        """Returns a list of tags to be added to the post, or an empty list if no tags are to be added."""

        total_tags = post.tags.all().count()

        # Check if the post has more than 5 tags
        if total_tags + 1 >= 5:
            # If so, return an empty list
            return []
        
        # Create a list of tags
        return [Tag.create_or_get("tagme")]

from booru.models.automation import TagSimilarity
import homebooru.settings

class ProbableTagDependenceAutomation(TagAutomation):
    """Adds tags that are likely to be dependent on other tags already present."""

    def __init__(self, order_override: int = None):
        super().__init__(order_override)
    
    def get_tags(self, post : Post) -> list[Tag]:
        post_tags = post.tags.all()
        raw_tags = [tag.tag for tag in post_tags]

        critical_value = homebooru.settings.BOORU_AUTOMATIC_TAG_ADD_SIMILARITY_THRESHOLD

        last_length = 0

        # Iterate until there are no more tags to add
        # This method ensures breadth-first searching, but eventually gets to all the tags
        while last_length != len(raw_tags):
            # Update the last length
            last_length = len(raw_tags)

            # Iterate through the tags
            for tag in post_tags:
                # Calculate the similar tags using the function
                similar_tags = TagSimilarity.find_similar(tag, critical_value)

                # Append these tags to the raw tags
                raw_tags += similar_tags

        # Return the list of tags
        return [Tag.create_or_get(tag) for tag in raw_tags]