from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from django.contrib.auth.models import User

import homebooru.settings
import booru.boorutils as boorutils
from booru.models.profile import Profile as ProfileModel
from booru.models.posts import Post

from .filters import *

def login(request):
    if request.method == "POST":
        # Get the credentials
        username = request.POST['username']
        password = request.POST['password']
        
        # Check if the credentials are valid
        user = authenticate(request, username=username, password=password)

        # If the credentials were not valid, send an error message
        if user is None:
            return render(request, 'booru/users/login.html', {'error': 'Invalid credentials', 'username': username}, status=400)

        # If the credentials were valid, log the user in
        auth_login(request, user)

        # Redirect
        return HttpResponseRedirect(homebooru.settings.LOGIN_REDIRECT_URL)
    
    if request.method == "GET":
        return render(request, 'booru/users/login.html')

def register(request):
    if request.method == "POST":
        # Get the credentials
        username = request.POST['username']
        password = request.POST['password']
        conf_password = request.POST['conf_password']

        email = request.POST['email']
        
        # Check that the username is valid
        if not boorutils.is_valid_username(username):
            return render(request, 'booru/users/register.html', {'error': 'Invalid username'}, status=400)

               # Check that the email is valid (ignore if none is provided)
        if len(email) > 0 and not boorutils.is_valid_email(email):
            return render(request, 'booru/users/register.html', {'error': 'Email is not valid', 'username': username}, status=400)

        # Make sure that the passwords match
        if password != conf_password:
            return render(request, 'booru/users/register.html', {'error': 'Passwords do not match', 'username': username, 'email': email}, status=400)
        
        # Check if the password is valid
        if not boorutils.is_valid_password(password):
            return render(request, 'booru/users/register.html', {'error': 'Password is not valid, make sure it: includes at least one digit, contains a special character and is 6 characters or longer.', 'username': username, 'email': email}, status=400)

        # Check if the username is valid
        if User.objects.filter(username=username).exists():
            return render(request, 'booru/users/register.html', {'error': 'Username already exists', 'email': email}, status=400)

        # Check if the email is valid (ignore if none is provided)
        if len(email) > 0 and User.objects.filter(email=email).exists():
            return render(request, 'booru/users/register.html', {'error': 'Email already exists', 'username': username}, status=400)

        # Create the user
        user = User.objects.create_user(username, email, password)

        # Log the user in
        auth_login(request, user)

        # Redirect
        return HttpResponseRedirect(homebooru.settings.LOGIN_REDIRECT_URL)
    
    if request.method == "GET":
        return render(request, 'booru/users/register.html')

def profile(request, user_id : int):
    user = None

    # Get the user
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        pass
    
    # If the user is None, send an error message
    if user is None:
        return render(request, 'booru/users/profile.html', {'error': 'User does not exist'}, status=404)
    
    # Get the user's profile
    profile = ProfileModel.create_or_get(user)
    
    # Render the profile page
    return render(request, 'booru/users/profile.html', {'profile': profile, 'owner': user})

def logout(request):
    # Log the user out
    auth_logout(request)

    # Redirect
    return HttpResponseRedirect(homebooru.settings.LOGOUT_REDIRECT_URL)

def favourites(request, user_id : int):
    user = None

    # Get the user
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        pass

    # If the user is None, send an error message
    if user is None:
        return HttpResponse('User does not exist', status=404)

    # Get the user's profile
    profile = ProfileModel.create_or_get(user)
    
    if request.method == "POST":
        # Get the post id
        post_id = request.POST.get('post_id')

        # Make sure the post exists
        try:
            # Make sure it is a number
            post_id = int(post_id)

            # Get the post
            post = Post.objects.get(id=post_id)

        except ValueError:
            return HttpResponse('Invalid post id.', status=400)

        except Post.DoesNotExist:
            return HttpResponse('Post does not exist.', status=404)
        
        # Check if the user sending the request is the owner of the post
        if request.user != user:
            return HttpResponse('You cannot favourite posts for other users.', status=403)

        # Check if the post is already in the favourites
        if profile.favourites.filter(id=post_id).exists():
            return HttpResponse('Post already in favourites.', status=409)

        # Add the post to the user's favourites
        profile.favourites.add(post)

        # Save the profile
        profile.save()

        # Return 200
        return HttpResponse(status=200)