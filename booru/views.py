from django.shortcuts import render
from django.http import HttpResponse

from .models import Post

# Create your views here.
def index(request):
    # Get the total posts
    total_posts = Post.objects.count()

    # Get each digit of the total posts
    total_posts_digits = [x for x in str(total_posts)]

    # Render the homepage.html template with the total posts and the total posts digits
    return render(request, 'booru/homepage.html', {'digits': total_posts_digits})

def browse(request):
    # Get the search phrase url parameter
    search_phrase = request.GET.get('tags', '')

    # Search with the given search phrase
    posts = Post.search(search_phrase)

    # Find the top tags
    top_tags = Post.get_search_tags(posts)

    # Render the browse.html template with the posts
    return render(request, 'booru/posts/browse.html', {'posts': posts, 'search_phrase': search_phrase, 'tags': top_tags})