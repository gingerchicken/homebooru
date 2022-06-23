from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

from booru.models.tags import Tag
from booru.models import Post, Rating
from booru.pagination import Paginator

from .filters import *

import magic
import os
import time
import json

import booru.boorutils as boorutils
import homebooru.settings

def browse(request):
    # Get the search phrase url parameter
    search_phrase = request.GET.get('tags', '').strip()

    # Get the page url parameter
    page = request.GET.get('pid', '1')

    # Make sure that page is an integer
    try:
        page = int(page)
    except ValueError:
        page = 1

    # Make sure that page is greater than 0
    if page < 1:
        page = 1

    # Search with the given search phrase
    posts, pagination = Post.search(
        search_phrase,
        paginate=True,
        page=page,
        per_page=homebooru.settings.BOORU_POSTS_PER_PAGE
    )

    # Configure the pagination
    pagination.page_url = '/browse?tags=' + search_phrase

    # Find the top tags
    top_tags = Post.get_search_tags(posts)

    # Render the browse.html template with the posts
    return render(request, 'booru/posts/browse.html', {
        'posts': posts,
        'search_param': search_phrase,
        'tags': top_tags,
        'paginator': pagination
    })

def view(request):
    # Get the post id url parameter
    post_id = request.GET.get('id', '')

    # Get the resize url parameter
    resize = request.GET.get('resize', '') == '1'

    # Get search phrase url parameter
    search_phrase = request.GET.get('tags', '').strip()

    # Get the post
    post = None
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        # Send a 404
        return HttpResponse(status=404)
    
    # Get the sorted tags
    sorted_tags = post.get_sorted_tags()

    # Get proximate posts
    # TODO make sure this is correct after adding pagination
    proximate_posts = post.get_proximate_posts(Post.search(search_phrase))
    
    # Render the view.html template with the post
    return render(request, 'booru/posts/view.html', {
        'post': post,
        'tags': sorted_tags,
        'resize': resize,
        'search_param': search_phrase,
        'next': proximate_posts['newer'],
        'previous': proximate_posts['older']
    })

def upload(request):
    # Check if it is a GET request
    if request.method == 'GET':
        # Get all of the ratings
        ratings = Rating.objects.all()

        return render(request, 'booru/posts/upload.html', {
            'ratings': ratings,
            'default_rating': Rating.get_default()
        })
    
    # Check if it is a POST request
    if request.method == 'POST':
        # Make sure that the uploaded file is there
        if 'upload' not in request.FILES:
            return HttpResponse('No file uploaded', status=400)
        
        # Get the image file
        uploaded_file = request.FILES['upload']

        # Get the tags
        tags = request.POST.get('tags', '')
        if len(tags.strip()) < 3:
            return HttpResponse('Tags must be at least 3 characters long', status=400)

        # Get the post title
        title = request.POST.get('title', '')

        # Get the post source
        source = request.POST.get('source', '')

        # Get the post rating
        rating_pk = request.POST.get('rating', '')
        # TODO check if the rating is valid (for now this is hardcoded)
        if len(rating_pk) < 1:
            # Default it to safe
            rating_pk = homebooru.settings.BOORU_DEFAULT_RATING_PK

        rating = None
        try:
            rating = Rating.objects.get(pk=rating_pk)
        except Rating.DoesNotExist:
            return HttpResponse('Invalid rating', status=400)

        # Create the upload folder if it doesn't exist
        upload_folder = homebooru.settings.BOORU_UPLOAD_FOLDER
        if not os.path.exists(upload_folder):
            upload_folder.mkdir(parents=True)
        
        # Check the mimetype
        m = magic.Magic(mime=True)
        mimetype = m.from_buffer(uploaded_file.read())
        file_type = mimetype.split('/')[-1]

        # Check if the file type is allowed
        if file_type not in homebooru.settings.BOORU_ALLOWED_FILE_EXTENSIONS:
            return HttpResponse('File type not allowed', status=400)

        # Get the filename
        filename = None
        save_path = None
        while save_path is None:
            filename = str(time.time()) + '_' + boorutils.hash_str(uploaded_file.name) + '.' + file_type

            # Calculate the save path
            save_path = upload_folder / filename

            # Check if the file already exists
            if save_path.exists():
                save_path = None
                continue
        
        # Save the file (required for ffmpeg processing)
        with open(save_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        # Get the file checksum
        checksum = boorutils.get_file_checksum(save_path)

        # Make sure that there are no posts with the same checksum
        if Post.objects.filter(md5=checksum).exists():
            return HttpResponse('File already exists', status=400)

        # Check all of the tags
        tag_names = tags.lower().split(' ')

        for tag_name in tag_names:
            if not Tag.is_name_valid(tag_name):
                return HttpResponse('Contains invalid tag name', status=400)
        
        # Create the post
        try:
            post = Post.create_from_file(str(save_path))
        except Exception as e:
            print(e.with_traceback())
            return HttpResponse(status=500)

        # Add the additional metadata
        post.title = title
        post.source = source
        post.rating = rating

        # Add the post
        post.save()

        # Add the tags to the post
        for tag_name in tag_names:
            tag = Tag.create_or_get(tag_name)
            post.tags.add(tag)
        
        # Save the post
        post.save()

        # TODO check that the file isn't too big
        # TODO check that there aren't too many tags (add a setting for this)

        # Redirect to the view page
        return HttpResponseRedirect(reverse('view') + '?id=' + str(post.id))