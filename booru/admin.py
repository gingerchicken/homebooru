from django.contrib import admin

# Register your models here.

# Posts
from .models import Post
admin.site.register(Post)

from .models import Rating
admin.site.register(Rating)

# Tag
from .models import Tag
admin.site.register(Tag)

from .models import TagType
admin.site.register(TagType)