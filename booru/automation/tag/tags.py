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