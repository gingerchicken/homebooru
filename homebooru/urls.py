"""homebooru URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from django.conf.urls.static import static
from homebooru import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('booru.urls')), # This makes the posts page the homepage
]

# Scanner
if settings.DIRECTORY_SCAN_ENABLED:
    # Include the scanner urls
    urlpatterns += [
        path('scanner/', include('scanner.urls')),
    ]

if settings.DEBUG:
    # Append storage folders
    for folder in settings.BOORU_STORAGE_SUBFOLDERS:
        url = settings.BOORU_STORAGE_URL + folder + '/'
        p = settings.BOORU_STORAGE_PATH / folder

        urlpatterns += static(url, document_root=p)