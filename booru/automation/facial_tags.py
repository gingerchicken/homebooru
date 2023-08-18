from .tag_automation import TagAutomation
from booru.models import Post, Tag
from booru.models.automation import FaceScan
import booru.boorutils as boorutils

class FaceRelatedTagAutomation(TagAutomation):
    """Adds tags based on the facial groups detected in the image."""

    def __init__(self, order_override: int = None):
        super().__init__(order_override)
    
    def get_tags(self, post : Post) -> list[Tag]:

        # Get the face scan related to this post (ensure it exists)
        try:
            face_scan = FaceScan.objects.get(post=post)
        except FaceScan.DoesNotExist:
            return []
        
        # Get the faces found in the scan
        faces = face_scan.faces.all()

        # Go through the face groups and add the tags
        tags = []

        for face in faces:
            # Get the group
            group = face.group

            # Check if it is none
            if group is None:
                continue

            # Loop through the tags
            for tag in group.tags.all():
                # Add the tag
                tags.append(tag)
        
        # Return the tags
        return tags
    
    def get_state_hash(self) -> str:
        # Given that more images were scanned for faces, the state should be different and hence different groups may be detected

        # Get the parent hash
        parent_hash = super().get_state_hash()

        # Get the total amount of face scans
        total_face_scans = FaceScan.objects.all().count()

        # Salt the parent hash with the total face scans
        hashed = boorutils.hash_str(parent_hash + str(total_face_scans))

        # Return the hash
        return hashed