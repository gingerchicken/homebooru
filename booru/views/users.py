from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login

import homebooru.settings

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