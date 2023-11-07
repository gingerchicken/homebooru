from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse
from django.shortcuts import render
import io

from booru.models import Face

def face(request, face_id):
    """Returns the face as an image."""

    # Ensure that the user is authenticated
    if not request.user.is_authenticated:
        # Return a 403
        return HttpResponse("You must be logged in to view this page.", status=403)
    
    # Ensure that the user has permission to view faces
    if not request.user.has_perm("booru.view_faces"):
        # Return a 403
        return HttpResponse("You do not have permission to view faces.", status=403)

    # Get the face
    try:
        face = Face.objects.get(id=face_id)
    except Face.DoesNotExist:
        return HttpResponseNotFound("Face not found")

    # Get the image as a pillow image
    image = face.face_image

    # Ensure that the image isn't None
    if image is None:
        return HttpResponse("No image found.")

    # Return the image
    return HttpResponse(image.getvalue(), content_type="image/jpeg")