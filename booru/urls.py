from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('browse/', views.browse, name='browse')
]