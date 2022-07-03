from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User

import homebooru.settings
import booru.boorutils as boorutils

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
            return render(request, 'booru/users/login.html', {'error': 'Invalid credentials'})

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

        # Make sure that the passwords match
        if password != conf_password:
            return render(request, 'booru/users/register.html', {'error': 'Passwords do not match'}, status=400)

        # Check that the username is valid
        if not boorutils.is_valid_username(username):
            return render(request, 'booru/users/register.html', {'error': 'Invalid username'}, status=400)

        # Check if the password is valid
        if not boorutils.is_valid_password(password):
            return render(request, 'booru/users/register.html', {'error': 'Password is not valid'}, status=400)

        # Check if the username is valid
        if User.objects.filter(username=username).exists():
            return render(request, 'booru/users/register.html', {'error': 'Username already exists'}, status=400)
        
        # Check that the email is valid (ignore if none is provided)
        if len(email) > 0 and not boorutils.is_valid_email(email):
            return render(request, 'booru/users/register.html', {'error': 'Email is not valid'}, status=400)

        # Check if the email is valid (ignore if none is provided)
        if len(email) > 0 and User.objects.filter(email=email).exists():
            return render(request, 'booru/users/register.html', {'error': 'Email already exists'}, status=400)

        # Create the user
        user = User.objects.create_user(username, email, password)

        # Log the user in
        auth_login(request, user)

        # Redirect
        return HttpResponseRedirect(homebooru.settings.LOGIN_REDIRECT_URL)
    
    if request.method == "GET":
        return render(request, 'booru/users/register.html')

def profile(request):
    # Get the user id url parameter
    user_id = request.GET.get('id', None)

    
    # If the user id is not None, use the requester's user id
    if user_id is None:
        return render(request, 'booru/users/profile.html', {'user': request.user})
    
    user = None

    # Convert the user id to an integer
    try:
        user_id = int(user_id)
    except ValueError:
        return render(request, 'booru/users/profile.html', {'error': 'Invalid user id'}, status=400)
    
    # Get the user
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return render(request, 'booru/users/profile.html', {'error': 'User does not exist'}, status=404)
    
    return render(request, 'booru/users/profile.html', {'user': user})