from django.shortcuts import render

# Create your views here.
def browse(request):
    # Get the tags from the request
    search_param = request.GET.get('tags', '')

    return render(request, 'advsearch/posts/browse.html', {
        'adv': True,
        'search_param': search_param,
    })