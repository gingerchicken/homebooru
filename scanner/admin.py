from django.contrib import admin

# Register your models here.
from .models import Scanner
admin.site.register(Scanner)

from .models import Booru
admin.site.register(Booru)

from .models import SearchResult
admin.site.register(SearchResult)