from django.contrib import admin

# Register your models here.
from .models import Booru
admin.site.register(Booru)

from .models import SearchResult
admin.site.register(SearchResult)

# Add scan button to admin page
from django.utils.html import format_html
from django.urls import reverse

from .models import Scanner
@admin.register(Scanner)
class ScannerAdmin(admin.ModelAdmin):
    # Add a button to the scanner admin page that adds a button that calls Scanner.scan()
    def scan_button(self, obj):
        return format_html('<a class="button" href="{}">Scan</a>', reverse('scan', args=[obj.id]))
    
    scan_button.short_description = 'Scan'
    scan_button.allow_tags = True
    
    list_display = ('name', 'scan_button')
