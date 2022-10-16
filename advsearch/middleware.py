from django.shortcuts import render

from booru.views import browse as booru_browse

    # Swap out the template with our own (i.e. process_template_response)
class BrowseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if response.template_name != 'booru/posts/browse.html':
            return response

        # We're on the browse page, so we can do our thing
        response.template_name = 'advsearch/posts/browse.html'
        
        # Check if we have the 'advanced' GET parameter
        if request.GET.get('adv', '0') == '1':
            # Add `adv_only` to the context
            response.context_data['adv'] = True

        return response