from .tag_automation import TagAutomation
from booru.models import Post, Tag

class AnimatedContentTagAutomation(TagAutomation):
    """Metadata detection for animated content (webm, gif)"""

    def get_tags(self, post : Post) -> list[Tag]:
        """Returns a list of tags to be added to the post, or an empty list if no tags are to be added."""

        # Check the metadata flags
        is_gif = post.filename.endswith(".gif")
        is_webm = post.is_video
        is_animated = is_gif or is_webm

        # Create a list of tags
        tags = []

        # Add relevant tags
        if is_animated:
            tags.append(Tag.create_or_get("animated"))
        
        # Check if it is a gif or a video
        if is_gif:
            tags.append(Tag.create_or_get("gif"))
        elif is_webm:
            tags.append(Tag.create_or_get("webm"))

        # Return the tags
        return tags

class LargeFileSizeTagAutomation(TagAutomation):
    """Metadata detection for large file sizes"""

    def __init__(self, large_file_size: int = 5 * 1024 * 1024, order_override: int = None):
        super().__init__(order_override)

        self.large_file_size = large_file_size # By default, 5MB

    def get_tags(self, post : Post) -> list[Tag]:
        """Returns a list of tags to be added to the post, or an empty list if no tags are to be added."""

        # Get the file path
        file_path = post.get_media_path()

        # Get the file size in bytes
        file_size = file_path.stat().st_size

        # Check if the file size is larger than the threshold
        if file_size < self.large_file_size:
            # If not, return an empty list
            return []
        
        # Create a list of tags
        return [Tag.create_or_get("large_filesize")]

        