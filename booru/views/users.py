from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login

import homebooru.settings

from .filters import *

def login(request):
    if request.method == "GET":
        return render(request, 'booru/users/login.html')