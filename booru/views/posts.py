from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

from booru.models import Post, Rating, PostFlag, Tag, Comment, Pool, PoolPost
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

    # Get the search result set
    result_set = Post.search(search_phrase)

    # Search with the given search phrase
    posts, pagination = Paginator.paginate(result_set, page, homebooru.settings.BOORU_POSTS_PER_PAGE)

    # Configure the pagination
    pagination.page_url = '/browse?tags=' + search_phrase

    # Find the top tags
    top_tags = Post.get_search_tags(posts, depth=homebooru.settings.BOORU_BROWSE_POST_TAGS_DEPTH)[:homebooru.settings.BOORU_BROWSE_TAGS_PER_PAGE]

    # Render the browse.html template with the posts
    return render(request, 'booru/posts/browse.html', {
        'posts': posts,
        'search_param': search_phrase,
        'tags': top_tags,
        'paginator': pagination
    })

def view(request, post_id):
    # Get the post
    post = None
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        # Send a 404
        return HttpResponse(status=404)

    if request.method == 'GET':
        # Get the resize url parameter
        resize = request.GET.get('resize', '') == '1'

        # Get search phrase url parameter
        search_phrase = request.GET.get('tags', '').strip()
        
        # Get the comment page url parameter
        comment_page = request.GET.get('pid', '1')

        # Make sure that it is an integer
        try:
            comment_page = int(comment_page)
        except ValueError:
            comment_page = 1

        # Get the sorted tags
        sorted_tags = post.get_sorted_tags()

        # Get the tags as a list (Ordered by tag name) (used for editing tags and info)
        list_tags = post.tags.all().order_by('tag')

        # Get proximate posts
        # TODO make sure this is correct after adding pagination
        proximate_posts = post.get_proximate_posts(Post.search(search_phrase))
        
        # Check if the post is flagged if the user is auth'd
        delete_flag = PostFlag.objects.filter(post=post, user=request.user).exists() if request.user.is_authenticated else False

        # Paginate the comments
        comment_set = post.comments.all().order_by('-created') # Newest on the first page etc.
        comments, comments_pagination = Paginator.paginate(comment_set, comment_page, homebooru.settings.BOORU_COMMENTS_PER_PAGE)

        # Convert the comments to a list and reverse it
        comments = list(comments)

        # Set the pagination url
        comments_pagination.page_url = str(post.id) + '?tags=' + search_phrase

        # Render the view.html template with the post
        return render(request, 'booru/posts/view.html', {
            'post': post,
            'tags': sorted_tags,
            'resize': resize,
            'search_param': search_phrase,
            'next': proximate_posts['newer'],
            'previous': proximate_posts['older'],
            'delete_flag': delete_flag,

            # Comments
            'comments': comments,
            'comments_pagination': comments_pagination,

            # Edit
            'ratings': Rating.objects.all(),
            'list_tags': list_tags
        })
    
    if request.method == 'DELETE':
        # Get the user
        user = request.user

        # Check if the user has permission to delete the post
        if user != post.owner and not user.has_perm('booru.delete_post'):
            # Send a 403
            return HttpResponse(status=403)

        # Delete the post
        post.delete()

        # Redirect to the home page
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST': # TODO perhaps this should be a PUT request
        # Get the user
        user = request.user

        # # Check if the user has permission to edit the post
        if user != post.owner and not user.has_perm('booru.change_post'):
            # Send a 403
            return HttpResponse(status=403)

        # TODO there is probably a better way to do this

        # Check if we should update the post's locked
        if 'locked' in request.POST:
            # Check if the user can lock the post
            if not user.has_perm('booru.lock_post'):
                # Send a 403
                return HttpResponse(status=403, content='You do not have permission to lock posts.')

            # TODO make this a form or something - this is a bit of a hack
            # Update the post's locked
            post.locked = boorutils.bool_from_str(request.POST['locked'])
        elif post.locked: # Check if the post is locked (as we wouldn't have locked it if it wasn't)
            # Send a 403
            return HttpResponse(status=403, content='Post is locked.')

        # Other changes here (since the post is not locked)
        if 'rating' in request.POST:
            raw_rating = request.POST['rating']

            # Attempt to get the rating
            rating = None
            try:
                # Check that the rating is a string
                if not isinstance(raw_rating, str):
                    raise ValueError('Rating is not a string')

                rating = Rating.objects.get(name=raw_rating)
            except Exception as e:
                pass # Nothing was found
            
            # Validate the rating
            if rating is None:
                return HttpResponse(status=400, content='Invalid rating')

            # Update the post's rating
            post.rating = rating

        if 'tags' in request.POST:
            raw_tags = request.POST['tags']

            # Strip whitespace
            raw_tags = raw_tags.strip()

            # Split the tags
            tags_list = raw_tags.split(' ')

            # Strip whitespace
            tags_list = [tag.strip() for tag in tags_list]

            # Remove empty tags
            tags_list = [tag for tag in tags_list if len(tag) > 0]

            # Ensure that the tag list is not empty
            if len(tags_list) == 0:
                return HttpResponse(status=400, content='No tags specified')

            # Check if all the tags are valid
            for tag_name in tags_list:
                if Tag.is_name_valid(tag_name):
                    continue
                
                # Failure
                return HttpResponse(status=400, content='Invalid tag name: ' + tag_name) # TODO can this be xss'd? 

            # Convert the list to a set to remove duplicates
            tags_list = list(set(tags_list))

            # Add the tags to the post
            post.tags.clear()
            for tag_name in tags_list:
                tag = Tag.create_or_get(tag_name)
                post.tags.add(tag)

        if 'source' in request.POST:
            source = request.POST['source']

            # Strip whitespace
            source = source.strip()

            # If the source is empty, set it to None
            if len(source) == 0:
                source = None
            elif len(source) > 1000:
                return HttpResponse(status=400, content='Source is too long')

            # I believe normally it should be a URL but for now just allow anything
            post.source = source
        
        if 'title' in request.POST:
            title = request.POST['title']

            # Strip whitespace
            title = title.strip()

            # If the title is empty, set it to None
            if len(title) == 0:
                title = None
            elif len(title) > 512: # Max length
                return HttpResponse(status=400, content='Title is too long')

            post.title = title

        # TODO there may be other fields that need adding here, such as owner but these are the main ones

        post.save()
        return HttpResponse(status=203)

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
        # TODO check if the user is logged in (if required)

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
            print(file_type)
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
        
        # Add the owner
        if request.user.is_authenticated:
            post.owner = request.user

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
        return HttpResponseRedirect(reverse('view', kwargs={'post_id': post.id}))

def post_flag(request, post_id):
    # Login checks first
    # Get the user
    user = request.user

    # Check if the user is logged in
    if not user.is_authenticated:
        return HttpResponse(status=403, content='You must be logged in to manage post flags.')

    # Get the post from the post_id
    post = None
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'POST':
        # Try and create the post flag
        # Check if the user can create post flags
        if not user.has_perm('booru.add_postflag'):
            # Send a 403
            return HttpResponse(status=403, content='You do not have permission to flag posts for deletion.')
        
        # Check that the user has not already flagged the post
        if PostFlag.objects.filter(post=post, user=user).exists():
            # Send a 409
            return HttpResponse(status=409, content='You have already flagged this post for deletion.')

        # Get the reason
        reason = request.POST.get('reason', '')

        # Create a post flag
        flag = PostFlag(
            post=post,
            user=user,
            reason=reason
        )

        flag.save()

        # Send a 201
        return HttpResponse(status=201)
    
    if request.method == 'DELETE':
        # Try and create the post flag
        # Check if the user can remove post flags
        if not user.has_perm('booru.delete_postflag'):
            # Send a 403
            return HttpResponse(status=403, content='You do not have permission to unflag posts for deletion.')
        
        # Get the potential flags
        flags = PostFlag.objects.filter(post=post, user=user)

        # Check that the user has not already flagged the post
        if not flags.exists():
            # Send a 404
            return HttpResponse(status=404, content='You have not flagged this post for deletion.')

        # Delete the post flag
        flags.delete()

        # Send a 200
        return HttpResponse(status=200)

def post_comment(request, post_id):
    # Get the user
    user = request.user

    # Check if the user is logged in
    is_anon = not user.is_authenticated

    # Check if the user is logged in OR if we allow anonymous comments
    if not homebooru.settings.BOORU_ANON_COMMENTS and is_anon:
        return HttpResponse(status=403, content='You must be logged in to comment on posts.')
    
    # Get the post from the post_id
    post = None

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return HttpResponse(status=404)
    
    if request.method == 'POST':
        # Make sure that the user has permission to comment
        if not is_anon and not user.has_perm('booru.add_comment'):
            return HttpResponse(status=403, content='You do not have permission to comment on posts.')

        # Get the anonymous part of the comment
        want_anon = request.POST.get('as_anonymous', 'false').lower() == 'true'

        # Check if the user is allowed to post anonymously
        if want_anon:
            if not homebooru.settings.BOORU_ANON_COMMENTS:
                return HttpResponse(status=403, content='Anonymous comments are not allowed on this instance.')

            is_anon = True

        # Get the comment textposts,site_homepage
        comment_text = request.POST.get('comment', '')

        # Strip whitespace
        comment_text = comment_text.strip()

        # Check if the comment is empty
        if len(comment_text) == 0:
            return HttpResponse(status=400, content='Comment cannot be empty.')
        
        user = request.user if not is_anon else None

        # Create the comment
        comment = Comment(
            post=post,
            user=user,
            content=comment_text
        )
        comment.save()

        # Send a 201
        return HttpResponse(status=201)

def random(request):
    # Check if the total number of posts is 0
    if Post.objects.count() == 0:
        # Redirect to the home page
        return HttpResponseRedirect(reverse('index'))

    # Get the random post
    post = Post.objects.order_by('?').first()

    # Redirect to the post
    return HttpResponseRedirect(reverse('view', kwargs={'post_id': post.id}))