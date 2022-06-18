from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('browse/', views.browse, name='browse'),
    path('upload', views.upload, name='upload'),
    path('view', views.view, name='view'),
]