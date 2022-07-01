from django.urls import path

from . import views

urlpatterns = [
    # Index
    path('', views.index, name='index'),

    # Posts
    path('browse', views.browse, name='browse'),
    path('upload', views.upload, name='upload'),
    path('view', views.view, name='view'),

    # Tags
    path('tags', views.tags, name='tags'),
    path('tags/edit', views.edit_tag, name='edit_tag'),

    # Accounts
    path('accounts/login', views.login, name='login'),
    # path('accounts/logout', views.logout, name='logout'),
    # path('accounts/register', views.register, name='register')
]