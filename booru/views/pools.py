from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

from booru.models import Post, Pool, PoolPost
from booru.pagination import Paginator

import json

import homebooru.settings

def pool(request, pool_id):
    # Get the pool from the pool_id
    pool = None
    try:
        pool = Pool.objects.get(id=pool_id)
    except Pool.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        # Get the posts in the pool
        posts = pool.posts.all()

        # TODO make this a function already...
        # Get the page number
        page = request.GET.get('pid', 1)
        
        try:
            page = int(page)
        except ValueError:
            page = 1

        if page < 1:
            page = 1
        
        # Paginate the posts
        posts, paginator = Paginator.paginate(posts, page, homebooru.settings.BOORU_POSTS_PER_PAGE)

        paginator.page_url = reverse('pool', kwargs={
            'pool_id': pool_id
        }) + '?'

        return render(request, 'booru/pools/view.html', {
            'pool': pool,
            'posts': posts,
            'paginator': paginator
        })


    # API type beat

    # Get the user
    user = request.user

    # Check if the user is logged in
    if not user.is_authenticated:
        return HttpResponse(status=403, content='You must be logged in to manage pools.')

    def get_post(post_id=None):
        """Gets the post from the request."""

        if post_id is None:
            post_id = request.POST.get('post', None)

        # Get the post from the post_id (if it exists)
        post = None
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return False
        except ValueError:
            return False # Invalid post id
        
        return post
    
    if request.method == 'POST':
        # Create a post pool
        # Check if the user can create post pools
        if not user.has_perm('booru.add_poolpost'):
            # Send a 403
            return HttpResponse(status=403, content='You do not have permission to add posts to pools.')
        
        # Get the post
        post = get_post()
        if not post:
            # Send a 404
            return HttpResponse(status=404, content='The post does not exist.')

        # Check that the user has not already added the post to the pool
        if PoolPost.objects.filter(pool=pool, post=post).exists():
            # Send a 409
            return HttpResponse(status=409, content='The post is already in the pool.')
        
        # Create a post pool
        pool_post = PoolPost(
            pool=pool,
            post=post
        )
        pool_post.save()

        # Send a 201
        return HttpResponse(status=201)
    
    if request.method == 'DELETE':
        # Delete a post pool
        # Check if the user can delete post pools
        if not user.has_perm('booru.delete_poolpost'):
            # Send a 403
            return HttpResponse(status=403, content='You do not have permission to remove posts from pools.')

        # Get the delete body
        raw_body = request.body
        post_ids = None
        try:
            # TODO this seems like a bad way to do this
            post_ids = json.loads(raw_body.decode('utf-8'))['posts']
        except Exception as e:
            # Send a 400
            return HttpResponse(status=400, content='The body must be a JSON object with a "posts" key.')

        # Check that the body is not empty
        if post_ids is None:
            # Send a 400
            return HttpResponse(status=400, content='The posts cannot be empty.')
        
        # Ensure that it is a list
        if not isinstance(post_ids, list):
            # Send a 400
            return HttpResponse(status=400, content='The body must be a list of post ids.')
        
        # Ensure that it is not empty
        if len(post_ids) == 0:
            # Send a 400
            return HttpResponse(status=400, content='The body cannot be empty.')

        # Create an array of posts
        posts = []

        # Get the posts from the post ids
        for post_id in post_ids:
            # Get the post from the post_id (if it exists)
            post = get_post(post_id)
            if not post:
                # Send a 404
                return HttpResponse(status=404, content='The post does not exist.')

            # Add the post to the array
            posts.append(post)

        for post in posts:
            pool_post = PoolPost.objects.filter(pool=pool, post=post)
            # Check that the user has not already added the post to the pool
            if not pool_post.exists():
                # Send a 404
                return HttpResponse(status=404, content='The post (' + post + ') is not in the pool.')
            
            # Delete the post pool
            pool_post.delete()

        # Send a 200
        return HttpResponse(status=200)

def pools(request):
    if request.method == 'GET':
        # Check for JSON parameter
        # TODO make this better.
        if 'json' in request.GET:
            # Get the search phrase url parameter
            search_phrase = request.GET.get('search', '').strip()
            print(search_phrase)

            # Search with the given search phrase
            pool_results = Pool.search(search_phrase)

            # Limit the results
            pool_results = pool_results[:homebooru.settings.BOORU_POOLS_PER_SEARCH_PAGE]

            # Convert the pools to JSON
            results = [{
                'id': pool.pk,
                'name': pool.name,
                'description': pool.description,
                'total_posts': pool.posts.count(),
                'creator': pool.creator.username
            } for pool in pool_results]

            # Send the results as JSON
            return HttpResponse(status=200, content_type='application/json', content=json.dumps(results))

        # Get the search phrase url parameter
        search_phrase = request.GET.get('search', '').strip()

        # TODO is there any sanitization that needs to be done here?

        # Get all the pools
        pools = Pool.search(search_phrase)

        # Get the page number
        page = request.GET.get('pid', 1)

        try:
            page = int(page)
        except ValueError:
            page = 1
        
        if page < 1:
            page = 1

        # Paginate the pools
        pools, paginator = Paginator.paginate(pools, page, homebooru.settings.BOORU_POOLS_PER_PAGE)
        paginator.page_url = reverse('pools') + '?search=' + search_phrase

        return render(request, 'booru/pools/browse.html', {
            'pools': pools,
            'paginator': paginator,
            'search_phrase': search_phrase
        })
    
    if request.method == 'POST':
        # Get the user
        user = request.user

        # Check if the user is logged in
        if not user.is_authenticated:
            return HttpResponse(status=403, content='You must be logged in to create pools.')

        # Check if the user has permission to create pools
        if not user.has_perm('booru.add_pool'):
            return HttpResponse(status=403, content='You do not have permission to create pools.')

        # Get the pool name
        pool_name = request.POST.get('name', None)
        
        # Get the pool description
        pool_description = request.POST.get('description', '')

        # Check if the pool name is empty
        if pool_name is None or len(pool_name) < 3:
            return HttpResponse(status=400, content='Pool name must be at least 3 characters long.')

        # Check if the pool name is too long
        if len(pool_name) > 255: # TODO make this a constant
            return HttpResponse(status=400, content='Pool name cannot be longer than 255 characters.')

        # Check if the pool description is too long
        if len(pool_description) > 1024: # TODO make this a constant
            return HttpResponse(status=400, content='Pool description cannot be longer than 1024 characters.')

        # Check if the pool name is already taken
        if Pool.objects.filter(name=pool_name).exists():
            return HttpResponse(status=409, content='A pool with that name already exists.')

        # Create the pool
        pool = Pool(
            name=pool_name,
            creator=user,
            description=pool_description
        )
        pool.save()

        # Send the pool as JSON
        return HttpResponse(status=200, content_type='application/json', content=json.dumps(
            {
                'id': pool.pk,
                'name': pool.name,
                'description': pool.description
            }
        ))

def new_pool(request):
    err = None
    if request.method == 'POST':
        resp = pools(request)

        content = resp.content.decode('utf-8')

        # If it was successful, redirect to the pool
        if resp.status_code == 200:
            # Get the JSON
            content = json.loads(content)            

            return HttpResponseRedirect(reverse('pool', kwargs={
                'pool_id': content['id']
            }))

        # Get the error
        err = content

    return render(request, 'booru/pools/new.html', {
        'error': err
    })
