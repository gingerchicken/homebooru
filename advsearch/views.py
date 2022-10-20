from django.shortcuts import render

from booru.pagination import Paginator
from booru.models import Post
import homebooru.settings

from .models import search_posts

# Create your views here.
def browse(request):
    # Get the tags from the request
    search_phrase = request.GET.get('tags', '')

    # TODO maybe cache this?
    result_set = None
    try:
        result_set = search_posts(search_phrase)
    except Exception as e:
        return render(request, 'advsearch/posts/browse.html', {
            'adv': True,
            'error': e,
            'search_param': search_phrase,
        })

    # Paginate
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
    posts, pagination = Paginator.paginate(result_set, page, homebooru.settings.BOORU_POSTS_PER_PAGE)

    # Configure the pagination
    pagination.page_url = '/browse?tags=' + search_phrase + '&adv=1'

    # Get the top tags
    top_tags = Post.get_search_tags(posts, depth=homebooru.settings.BOORU_BROWSE_POST_TAGS_DEPTH)[:homebooru.settings.BOORU_BROWSE_TAGS_PER_PAGE]

    return render(request, 'advsearch/posts/browse.html', {
        'adv': True,
        'search_param': search_phrase,
        'posts': posts,
        'paginator': pagination,
        'tags': top_tags,
    })