from django.urls import path

from . import views

urlpatterns = [
    # Index
    path('', views.index, name='index'),

    # Posts
    path('browse', views.browse, name='browse'),
    path('upload', views.upload, name='upload'),
    path('post/<int:post_id>', views.view, name='view'),
    path('post/<int:post_id>/flag', views.post_flag, name='post_flag'),
    path('post/<int:post_id>/comments', views.post_comment, name='post_comment'),
    path('random', views.random, name='random'),

    # Pools
    path('pools', views.pools, name='pools'),
    path('pools/<int:pool_id>', views.pool, name='pool'),
    path('pool', views.new_pool, name='new_pool'),
    path('pools/<int:pool_id>/edit', views.edit_pool, name='edit_pool'),

    # Tags
    path('tags', views.tags, name='tags'),
    path('tags/edit', views.edit_tag, name='edit_tag'),
    path('tags/autocomplete/<str:tag>', views.autocomplete, name='autocomplete'),
    path('tags/savedsearches', views.saved_searches, name='saved_searches'),
    path('tags/savedsearches/<int:saved_search_id>', views.saved_search, name='saved_search'),

    # Accounts
    path('accounts/login', views.login, name='login'),
    path('accounts/logout', views.logout, name='logout'),
    path('accounts/register', views.register, name='register'),
    path('accounts/profile/<int:user_id>', views.profile, name='profile'),
    path('accounts/profile/<int:user_id>/favourites', views.favourites, name='favourites'),
]