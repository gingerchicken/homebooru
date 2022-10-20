from django.shortcuts import render

from .views import browse

class BrowseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Make sure that it is the browse page
        if request.path != '/browse':
            return self.get_response(request)

        # Check if we have the 'advanced' GET parameter
        if not self.perform_advanced(request):
            return self.get_response(request)

        # We're on the browse page, so we can do our thing
        return browse(request)
    
    def perform_advanced(self, request):
        # Check if we have the 'advanced' GET parameter
        return request.GET.get('adv', '0') == '1'

    def update_context(self, request, response):
        response.context_data['adv'] = self.perform_advanced(request)

    def process_template_response(self, request, response):
        # Override the default template so that we can add features to the page

        # Return the response
        response.template_name = 'advsearch/posts/browse.html' if response.template_name == 'booru/posts/browse.html' else response.template_name
        return response