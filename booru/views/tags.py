from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from booru.pagination import Paginator
from booru.models.tags import Tag, TagType
import homebooru.settings

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
    
    # Get the paginator
    tags, paginator = Paginator.paginate(tags, page_number, homebooru.settings.BOORU_TAGS_PER_PAGE)

    # Configure paginator
    paginator.page_url = f"{request.path}?tag={search_phrase}&order_by={order_by}&order_direction={order_direction}"

    # Render the tags.html template with the tags
    return render(request, 'booru/tags/tags.html', {
        'tags': tags,
        'search_param': search_phrase,
        'paginator': paginator,
        'order_by': order_by,
        'order_direction': order_direction
    })

def edit_tag(request):
    # Get the tag id url parameter
    tag_name = request.GET.get('tag', '')

    if not Tag.is_name_valid(tag_name):
        return HttpResponse(status=404)
    
    # Get the tag
    tag = None

    try:
        tag = Tag.objects.get(tag=tag_name)
    except Tag.DoesNotExist:
        return HttpResponse("Unable to find tag", status=404)

    # Handle GET request

    if request.method == 'GET':
        # Get the tag types
        tag_types = TagType.objects.all()

        # Render the tags.html template with the tag
        return render(request, 'booru/tags/edit.html', {
            'tag': tag,
            'tag_types': tag_types
        })
    
    # Handle POST request
    if request.method == 'POST':
        # Get the new tag type
        new_tag_type = request.POST.get('tag_type', tag.tag_type.name)

        # Get the tag type
        tag_type = None
        try:
            tag_type = TagType.objects.get(name=new_tag_type)
        except TagType.DoesNotExist:
            return HttpResponse("Unable to find tag type", status=404)

        # Update the tag
        tag.tag_type = tag_type
        tag.save()

        # Redirect to the tags page
        return HttpResponseRedirect(f"/tags?tag={tag.tag}")