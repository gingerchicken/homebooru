import django.db.models as models

from .posts import Post

class TagAutomationRecord(models.Model):
    """A record of a tag automation's state."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    # The hash of the automation's state
    state_hash = models.CharField(max_length=32)

    # The date the record was created
    performed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post} @ State {self.state_hash}"

    # The post must be unique
    class Meta:
        unique_together = ('post', 'state_hash')

class TagSimilarity(models.Model):
    """Bi-directional tag similarity."""

    # The first tag (string)
    tag_x = models.CharField(max_length=255)

    # The second tag (string)
    tag_y = models.CharField(max_length=255)

    # The probability of x given y
    prob_x_impl_y = models.FloatField()

    # The probability of y given x
    prob_y_impl_x = models.FloatField()

    # The number of times x and y have been seen together
    occurrence = models.IntegerField()

    # Was this given manually?
    manual = models.BooleanField(default=True)

    # Override the save method to ensure that the tags are always in the same order
    def save(self, *args, **kwargs):

        # Ensure that the tags are always in the same order
        [self.tag_x, self.tag_y] = sorted([self.tag_x, self.tag_y])

        # If manual is set to True, then the probabilities should be 1 or 0
        # Round them to the nearest integer
        if self.manual:
            self.prob_x_impl_y = round(self.prob_x_impl_y)
            self.prob_y_impl_x = round(self.prob_y_impl_x)

        # The probabilities should be between 0 and 1
        self.prob_x_impl_y = max(0, min(1, self.prob_x_impl_y))
        self.prob_y_impl_x = max(0, min(1, self.prob_y_impl_x))

        # Call the parent save method
        super().save(*args, **kwargs)
    
    class Meta:
        # The tag pair must be unique
        unique_together = ('tag_x', 'tag_y')

        # The plural name is "Tag Similarities"
        verbose_name_plural = "Tag similarities"
    
    def __str__(self):
        return f"{self.tag_x} -> {self.tag_y} ({self.prob_x_impl_y}) | {self.tag_y} -> {self.tag_x} ({self.prob_y_impl_x})"

    @staticmethod
    def find_similar(tag : str, critical_region : float) -> list[str]:
        """Returns a list of tags similar to the given tag."""

        # Find all the tags that are above the critical region (either a or b)
        similar_tags = TagSimilarity.objects.filter(
            models.Q(tag_x=tag, prob_x_impl_y__gte=critical_region) |
            models.Q(tag_y=tag, prob_y_impl_x__gte=critical_region)
        )

        # Filter this this to get only the tags include the tag as either x or y
        similar_tags = similar_tags.filter(
            models.Q(tag_x=tag) | models.Q(tag_y=tag)
        )

        # Create the array to store the new tags
        new_tags = []

        # Iterate through the similar tags
        for similar_tag in similar_tags:
            # Check if the tag is x or y
            is_x = similar_tag.tag_x == tag
            is_y = similar_tag.tag_y == tag

            p = 0
            result_tag = None

            # Check if the tag is x or y
            if is_x:
                # Get the probability of y given x
                p = similar_tag.prob_x_impl_y

                # Set the result tag to y
                result_tag = similar_tag.tag_y
            elif is_y:
                # Get the probability of x given y
                p = similar_tag.prob_y_impl_x

                # Set the result tag to x
                result_tag = similar_tag.tag_x

            # If the probability is less than the critical region, then remove it
            if p < critical_region:
                # Skip this tag
                continue

            # Sanity check to make sure that there is a tag
            if result_tag is None:
                # Show a warning
                print(f"Warning: TagSimilarity {similar_tag} has no tag, this should never be reached!")
                
                # Skip this tag
                continue

            # Add the tag to the list
            new_tags.append(result_tag)

        # Return the new tags
        return new_tags

import face_recognition
import numpy as np
import cv2
import base64
import pickle

def serialize_encoding(encoding : np.ndarray) -> bytes:
    """Serializes the encoding to bytes."""

    # Dump the encoding
    np_bytes = pickle.dumps(encoding)

    # Return the bytes
    return np_bytes

def deserialize_encoding(np_bytes : bytes) -> np.ndarray:
    """Deserializes the encoding from bytes."""

    # Load the pickle
    encoding = pickle.loads(np_bytes)

    # Return the encoding
    return encoding

class FaceScan(models.Model):
    """A record of a facial scan."""
    post = models.OneToOneField(Post, on_delete=models.CASCADE)

    has_scanned = models.BooleanField(default=False)

    def scan(self) -> list:
        """Scans the post for faces, automatically grouping them and adding them to the database."""

        # Check if the post has already been scanned
        if self.has_scanned:
            # Return an empty list
            return []
        
        # Update the scan
        self.has_scanned = True
        self.save()

        faces = Face.from_post(self.post)

        results = []

        # Iterate through the faces
        for face in faces:
            # Set the scan to this
            face.scan = self

            # Save the face
            face.save()

            # Add the face to the results
            results.append(face)

            # Attempt to group the face
            group = FaceGroup.get_group(face.get_np_encoding())

            # Check if the group is None
            if group is None:
                # Create a new group
                group = FaceGroup()
                group.save()

            # Set the group
            face.group = group

            # Save the group and face
            group.save()
            face.save()

        # Return the results
        return results

    def __str__(self):
        return f"Facial Scan for {self.post}"
        
class FaceGroup(models.Model):
    """A record of a group of faces."""

    @property
    def faces(self):
        """Returns the faces in this group."""

        # Return the faces in this group
        return Face.objects.filter(group=self)
    
    def check_encoding(self, encoding : np.ndarray) -> bool:
        """Checks if a given facial encoding matches that of the group."""

        # Get the example faces
        example_faces = self.faces

        # Make sure that they have is_fake set to False
        example_faces = example_faces.filter(is_fake=False)

        # Get the encodings as numpy arrays
        encodings = [face.get_np_encoding() for face in example_faces]

        # Check if the encoding matches any of the encodings
        matches = face_recognition.compare_faces(encodings, encoding)

        # Return if there is a match
        return any(matches)
    
    @staticmethod
    def get_group(encoding : np.ndarray):
        """Returns the group that the encoding matches."""

        # Select all the groups
        groups = FaceGroup.objects.all()

        # Iterate through the groups
        for group in groups:
            # Check if the encoding matches
            if not group.check_encoding(encoding):
                continue
            
            # Success, return the group
            return group
        
        # No group found, return None
        return None

class Face(models.Model):
    """Face data from a given scan"""

    # The scan foreign key
    scan = models.ForeignKey(FaceScan, on_delete=models.CASCADE)

    # Array of bytes for encoding
    encoding = models.BinaryField()

    # Snippet being the face cropped out, stored as a base64 string (it is only 64x64 pixels)
    snippet = models.TextField()

    # Is this marked as "not a face"?
    is_fake = models.BooleanField(default=False)

    # The group that this face belongs to
    group = models.ForeignKey(FaceGroup, on_delete=models.CASCADE, null=True, blank=True)

    def get_np_encoding(self):
        """Converts the encoding to a numpy array."""
        return deserialize_encoding(self.encoding)

    def set_np_encoding(self, encoding : np.ndarray):
        """Sets the encoding from a numpy array."""
        self.encoding = serialize_encoding(encoding)

    # TODO create a method for getting the snippet as a PIL image

    @staticmethod
    def from_post(post) -> list:
        """Grabs the faces from the post and saves them."""

        # Handle videos and images differently
        if post.is_video:
            return [] # TODO - Implement video facial scanning
        
        # Get the image path
        image_path = post.get_media_path()

        # Load the image
        image = face_recognition.load_image_file(image_path)

        # Get the face locations
        face_locations = face_recognition.face_locations(image)

        # Get the encodings
        face_encodings = face_recognition.face_encodings(image, face_locations)

        for encoding, location in zip(face_encodings, face_locations):
            # Select
            top, right, bottom, left = location

            # Crop the image
            face_image = image[top:bottom, left:right]

            # Resize the image
            face_image = cv2.resize(face_image, (64, 64))

            # Encode the image
            _, face_image = cv2.imencode(".jpg", face_image)

            # Convert the image to a base64 string
            face_image = base64.b64encode(face_image).decode("utf-8")

            # Create the face
            face = Face(
                snippet=face_image
            )

            # Set the encoding
            face.set_np_encoding(encoding)

            # Return the face
            yield face


# Hook into the Post save method to re-add the post to be scanned
from django.db.models.signals import post_save
from booru.tasks import perform_automation

def post_save_post(sender, instance, created, **kwargs):
    """Removes the post from the automation records."""

    # Remove the post from the automation records
    TagAutomationRecord.objects.filter(post=instance).delete()

    # Check if the post was created
    if created:
        # Run the automation task
        # This way we don't have to wait for the next scan but it should get scanned anyway.
        perform_automation.delay(instance.id)

# Connect the post save signal
post_save.connect(post_save_post, sender=Post)