from .tag_automation import TagAutomation
from booru.models import Post, Tag
from booru.models.automation import FaceScan
import random
import booru.boorutils as boorutils

class FaceRelatedTagAutomation(TagAutomation):
    """Adds tags based on the facial groups detected in the image."""

    def __init__(self, order_override: int = None):
        super().__init__(order_override)
    
    def get_tags(self, post : Post) -> list[Tag]:

        # Get the face scan related to this post (if it exists)
        if not FaceScan.objects.filter(post=post).exists():
            return []
        
        # Get the face scan
        face_scan = FaceScan.objects.get(post=post)
        
        # Get the faces found in the scan
        faces = face_scan.faces.all()

        new_tags = []

        # Get the face groups
        for face in faces:
            for tag in face.tags:
                # Skip any tags that are already on the post
                if tag in new_tags:
                    continue
                
                # Add the new tag
                new_tags.append(tag)

        # Return the new tags
        return new_tags

    
    def get_state_hash(self) -> str:

        # Really you want to be doing something like this:
        '''
        # Given that more images were scanned for faces, the state should be different and hence different groups may be detected

        # Get the parent hash
        parent_hash = super().get_state_hash()

        # Get the total amount of face scans
        total_face_scans = FaceScan.objects.all().count()

        # Salt the parent hash with the total face scans
        hashed = boorutils.hash_str(parent_hash + str(total_face_scans))

        # Return the hash
        return hashed
        '''

        # TODO ensure that this gets re-scanned as it currently doesn't always get re-scanned ...

        # But this causes a lot of issues with the database, so we'll just return a random hash
        return boorutils.hash_str(str(random.random()))