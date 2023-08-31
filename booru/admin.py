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
admin.site.register(FaceGroup)

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