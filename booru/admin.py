from django.contrib import admin

# Register your models here.

# Posts
from .models import Post
admin.site.register(Post)

from .models import PostFlag
admin.site.register(PostFlag)

from .models import Rating
admin.site.register(Rating)

from .models import Comment
admin.site.register(Comment)

# Tag
from .models import Tag
admin.site.register(Tag)

from .models import TagType
admin.site.register(TagType)

# Profiles
from .models import Profile
admin.site.register(Profile)