from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from booru.models.tags import Tag

from .filters import *

def tags(request):
    # Get the search phrase url parameter
    search_phrase = request.GET.get('tag', '').strip()

    # TODO implement search functionality

    # For now we will just get all of the tags
    tags = Tag.objects.all()

    # Render the tags.html template with the tags
    return render(request, 'booru/tags/tags.html', {
        'tags': tags,
        'search_param': search_phrase
    })