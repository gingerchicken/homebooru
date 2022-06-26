from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from booru.models.tags import Tag

from .filters import *

def tags(request):
    # Get the search phrase url parameter
    search_phrase = request.GET.get('tag', '').strip()

    # Get the page number url parameter
    page_number = request.GET.get('pid', '1')

    # Get the order_by url parameter
    order_by = request.GET.get('order_by', 'total_posts')

    # Get the order direction url parameter
    order_direction = request.GET.get('order_direction', 'descending')

    # Make sure that the page number is an integer
    try:
        page_number = int(page_number)
    except ValueError:
        page_number = 1
    
    # Get the tags
    tags = Tag.objects.none()

    # Handle any invalid inputs
    try:
        tags = Tag.search(search_phrase, sort_param=order_by, order=order_direction)
    except ValueError:
        # Send a 400 error as this will be a bad request
        # TODO create a custom error page for 400 errors
        return HttpResponse(status=400)

    # Render the tags.html template with the tags
    return render(request, 'booru/tags/tags.html', {
        'tags': tags,
        'search_param': search_phrase
    })