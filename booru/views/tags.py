from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.db import models

from booru.pagination import Paginator
from booru.models.tags import Tag, TagType, SearchSave
import homebooru.settings

from .filters import *

import json

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

def autocomplete(request, tag):
    # Get the tags include the post count
    tags = Tag.objects.filter(tag__istartswith=tag)

    # Annotate the tags with the post count
    tags = tags.annotate(**{
        'total': models.Count('posts')
    })

    # Sort by the total posts
    tags = tags.order_by('-total')

    # Limit it to the autocomplete limit
    tags = tags[:homebooru.settings.BOORU_AUTOCOMPLETE_MAX_TAGS]

    # Convert to an array
    flat = [{'tag': tag.tag, 'total': tag.total, 'type': str(tag.tag_type)} for tag in tags]

    # Return the tags as json
    return HttpResponse(json.dumps(flat), content_type="application/json")

def saved_searches(request):
    # Get the user
    user = request.user

    # Check if the user is logged in
    if not user.is_authenticated:
        # Redirect to the login page
        return HttpResponseRedirect('/accounts/login')

    # Get the page number url parameter
    page_number = request.GET.get('pid', '1')

    # Try to convert the page number to an integer
    try:
        page_number = int(page_number)
    except ValueError:
        page_number = 1

    # Get the saved searches
    searches = SearchSave.get_latest_searches(user)

    # Paginate the searches
    searches, paginator = Paginator.paginate(searches, page_number, homebooru.settings.BOORU_SAVED_SEARCHES_PER_PAGE)

    # Render the saved_searches.html template with the user
    return render(request, 'booru/tags/saved-searches.html', {
        'user': user,
        'searches': searches,
        'paginator': paginator
    })