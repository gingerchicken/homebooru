from .tag_automation import TagAutomation
from booru.models import Post, Tag

class AnimatedContentTagAutomation(TagAutomation):
    """An automation for adding the webm tag to posts with webms."""

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