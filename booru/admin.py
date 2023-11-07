from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

# Register your models here.

# Posts
from .models import Post
admin.site.register(Post)

from .models import PostFlag
admin.site.register(PostFlag)

from .models import Rating
admin.site.register(Rating)

# Tag
from .models import Tag
admin.site.register(Tag)

from .models import TagType
admin.site.register(TagType)

# Profiles
from .models import Profile
admin.site.register(Profile)

# Comments
from .models import Comment
admin.site.register(Comment)

# Pools
from .models import Pool
admin.site.register(Pool)

from .models import PoolPost
admin.site.register(PoolPost)

# Automation
from .models import TagSimilarity, TagAutomationRecord
admin.site.register(TagSimilarity)
admin.site.register(TagAutomationRecord)

# Facial Recognition
from .models import FaceScan, FaceGroup, Face
admin.site.register(FaceScan)

# Create a ModelAdmin class to customize the appearance of the admin site
@admin.register(Face)
class FaceAdmin(admin.ModelAdmin):
    """Custom admin page for faces."""

    def face(self, obj):
        """Returns the face as an image."""

        # Get the URL for the face image using the object's primary key
        face_image_url = reverse('face', args=[obj.id])

        # Return the HTML for the image tag
        return format_html('<img src="{}" />', face_image_url)
            
    list_display = ('face', )

@admin.register(FaceGroup)
class FaceGroupAdmin(admin.ModelAdmin):
    """Custom admin page for face groups."""

    def random_faces(self, obj):
        """Returns the face as an image."""

        # The following code gets a list of 5 random faces from the group.
        # Then, it loops through the faces and gets the URL for each face.
        # Finally, it returns the HTML for the image tags.

        # Get the faces in the group
        all_faces = obj.faces

        # Select 5 random faces
        random_faces = all_faces.order_by('?')[:5]

        # Store the html elements
        elements = []

        # Loop through the faces
        for face in random_faces:
            # Get the face image URL
            face_image_url = reverse('face', args=[face.id])
            
            # Create the img html
            img_html = format_html('<img src="{}" />', face_image_url)

            # Create a tag for the face
            face_tag = format_html('<a href="{}">{}</a>', reverse('admin:booru_face_change', args=[face.id]), img_html)

            # Append the image tag to the list of elements
            elements.append(face_tag)

        # Return the HTML for the image tag
        return format_html(''.join(elements))
    
    def name(self, obj):
        """Returns the name"""

        return str(obj)
    
    # Display the default fields and the random faces
    list_display = ('name', 'random_faces' )