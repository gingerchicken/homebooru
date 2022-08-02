from django.shortcuts import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from .models import Scanner

def scan(request, scanner_id):
    # Make sure that the user has permission to scan
    if not request.user.has_perm('scanner.scan'): return HttpResponse('You do not have permission to scan.', status=403)

    # Make sure the scanner exists
    try:
        scanner = Scanner.objects.get(id=scanner_id)
    except Scanner.DoesNotExist:
        return HttpResponse('Scanner does not exist.', status=404)

    # Call the Scan function
    posts = scanner.scan()

    # Redirect to the scanner admin page
    return HttpResponseRedirect(reverse('admin:index'))