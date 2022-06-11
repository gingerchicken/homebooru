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