from django.db import models
from django.apps import apps

import urllib
import json
import requests

class Booru(models.Model):
    # The name of the booru that is going to be scanned
    name = models.TextField(unique=True, blank=False, null=False)

    # The URL for the root of the booru
    url = models.URLField(unique=True, blank=False, null=False)

    def __str__(self):
        return self.name

    @property
    def api_url(self) -> str:
        """The URL with the API for the booru
        
        Subject to pagination!"""

        # Concatenate the URL with the API endpoint
        return self.url + '/index.php?page=dapi&s=post&json=1&q=index'

    def raw_search_booru(self, phrase : str = '') -> list:
        """Searches the booru using the given phrase"""
        
        # Sanitize the phrase to be URL safe
        phrase = urllib.parse.quote(phrase)

        # Concatenate the URL with the search phrase
        url = self.api_url + '&tags=' + phrase

        # Make a request to the booru
        resp = requests.get(url)

        # Make sure that it was a 200
        if resp.status_code != 200:
            return []

        try:
            return resp.json()
        except:
            return []

    def search_booru_md5(self, md5 : str):
        """Search for a file with the given MD5 hash."""

        # Get the SearchResult model
        SearchResult = apps.get_model('scanner', 'SearchResult')

        # Run a search for the MD5
        try:
            post = self.raw_search_md5(md5)
        except:
            post = None

        # If we didn't find anything, return an empty result
        if not post or 'tags' not in post:
            return SearchResult(booru=self, md5=md5, found=False)

        # Create a new search result
        result = SearchResult(md5=md5, booru=self, found=True)

        # Get the tags
        tags = post['tags']

        # Get Rating and Source
        source = None if 'source' not in post else post['source']
        rating = None if 'rating' not in post else post['rating']

        # Set the options
        result.raw_rating   = rating  # Raw rating
        result.source       = source  # Source URL
        result.tags         = tags    # Raw tags

        # Return the result
        return result

    def raw_search_md5(self, md5 : str) -> dict:
        """Search for a file with the given MD5 hash."""
        
        # Get the posts
        posts = self.raw_search_booru('md5:' + md5)

        # Make sure that we got some posts
        if len(posts) == 0:
            return None
        
        # Return the first post
        return posts[0]

    def test(self) -> bool:
        """Verifies that the booru is working"""
        
        # Make a request to the booru
        try:
            resp = requests.get(self.url)
        except:
            return False

        # Make sure that it was a 200
        if resp.status_code != 200:
            return False
        
        # Check that we can access the API
        resp = requests.get(self.api_url)

        # Make sure that it was a 200
        if resp.status_code != 200:
            return False

        # Make sure that we can convert it from JSON
        try:
            data = resp.json()
        except:
            return False

        # Make sure that at least one post was returned
        if len(data) == 0:
            return False

        # Return that the booru is valid
        return True
    
    def save(self, *args, **kwargs):
        # Make sure that the URL is valid
        if not self.test():
            raise ValueError('Invalid booru URL')

        # Call the superclass save method
        super().save(*args, **kwargs)
