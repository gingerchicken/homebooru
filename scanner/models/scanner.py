from django.db import models
from django.contrib.auth.models import User

import homebooru.settings

import booru.boorutils as boorutils
from booru.models.posts import Rating, Post
from booru.models.tags import Tag

from .booru import Booru
from .searchresult import SearchResult

import os

class Scanner(models.Model):
    # The name of the scanner
    name = models.TextField(unique=True, blank=False, null=False)

    # The path for the root directory of the scanner
    path = models.TextField(unique=True, blank=False, null=False)

    # The owner of all of the found posts
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    # The tags to automatically add to new posts
    auto_tags = models.ManyToManyField(Tag, blank=True, related_name='auto_tags')

    # The boorus to search, by default all of them
    search_boorus = models.ManyToManyField(Booru, blank=True, related_name='boorus')

    # Specify if we should prune the results on startup
    auto_prune_results = models.BooleanField(default=False)

    @property
    def boorus(self):
        # If none of the boorus are selected, return all of them
        if len(self.search_boorus.all()) == 0:
            return Booru.objects.all()
        
        # Return the selected boorus
        return self.search_boorus.all()

    @property
    def default_tags(self) -> list:
        """Returns the default tags for an item when nothing was found"""

        tags = []

        if not homebooru.settings.SCANNER_USE_DEFAULT_TAGS:
            return tags

        for tag in homebooru.settings.SCANNER_DEFAULT_TAGS:
            tags.append(Tag.create_or_get(tag))
        
        return tags

    def __str__(self):
        return self.name
    
    
    def save(self, *args, **kwargs):
        # Make sure that the path exists
        if not os.path.exists(self.path):
            raise ValueError('The path does not exist')

        # Make sure that the path is valid
        if not os.path.isdir(self.path):
            raise ValueError('Invalid scanner path')

        # Call the superclass save method
        super().save(*args, **kwargs)
