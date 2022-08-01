from django.db import models
from django.contrib.auth.models import User

import homebooru.settings

import booru.boorutils as boorutils
from booru.models.posts import Rating, Post
from booru.models.tags import Tag

from .booru import Booru
from .searchresult import SearchResult

import os
import threading
from pathlib import Path

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
    
    def create_post(self, path : str, use_default_tags = True) -> Post:
        """Combines all of the search results and creates a post"""

        # Get a md5 hash for the file
        md5 = boorutils.get_file_checksum(path)

        # Get all the results
        results = SearchResult.objects.filter(md5=md5)

        # Make sure that we got some results
        if len(results) == 0:
            return None
        
        # Find the mostly used rating
        rating = boorutils.mode([
            result.rating for result in results
        ])

        # Find the most common source
        source = boorutils.mode([
            result.source for result in results
        ])

        # Combine the tags
        tags = {}

        # Automatically add the auto tags
        for tag in self.auto_tags.all():
            tags[str(tag)] = tag

        for result in results:
            # Get the tags
            raw_tags = result.tags

            # Split the tags
            tags_list = raw_tags.split(' ')

            # Add the tags to the dictionary
            for tag in tags_list:
                # Skip the tag if we have already added it
                if tag in tags: continue

                # Skip the tag if it is invalid
                if not Tag.is_name_valid(tag): continue

                # Add the tag
                tags[tag] = Tag.create_or_get(tag)
        
        # Convert the tags to a list
        tags_list = list(tags.values())

        # Make sure that we have at least one tag
        if len(tags_list) == 0:
            if homebooru.settings.SCANNER_USE_DEFAULT_TAGS:
                tags_list = self.get_default_tags()
            else:
                return None

        # Create the post
        post = Post.create_from_file(file_path=path, owner=self.owner)
        post.save()

        # Add the tags
        for tag in tags_list:
            post.tags.add(tag)
        
        # Add other information
        post.rating = rating
        post.source = source

        # Save changes
        post.save()

        # Return the post
        return post
    
    def save(self, *args, **kwargs):
        # Make sure that the path exists
        if not os.path.exists(self.path):
            raise ValueError('The path does not exist')

        # Make sure that the path is valid
        if not os.path.isdir(self.path):
            raise ValueError('Invalid scanner path')

        # Call the superclass save method
        super().save(*args, **kwargs)
    
    def scan(self, create_posts : bool = True, use_default_tags : bool = True) -> list:
        """Scans the scanner for new files"""

        # TODO implement multithreading
        multi_thread = False
        max_concurrent_threads = 8

        # Check if we should prune the results
        if self.auto_prune_results:
            # Prune the results
            SearchResult.prune()

        # Store the md5 hashes as the key and the path as the value
        file_hashes = {}

        # Find all the files in the path using the walk function
        for root, dirs, files in os.walk(self.path):
            # Loop through all the files
            for file in files:
                # Get the full path
                path = os.path.join(root, file)

                # Make the path absolute
                path = os.path.abspath(path)

                # Get the md5 hash of the file
                md5 = boorutils.get_file_checksum(path)

                # Check if we already have this file
                if md5 in file_hashes: continue

                # Make sure that we should search the file
                if not self.should_search_file(path): continue

                # Add the file to the list
                file_hashes[md5] = path

        # Store the created posts
        created_posts = []

        # Store the threads
        threads = []
        operations = 0

        # create_post code, this is used to create the posts in a thread
        def create_post(path : str) -> None:
            # Search for the file
            if not self.search_file(path): return

            # ... Successfully found the file

            # Get the required local variables
            nonlocal created_posts

            # Create the post
            post = self.create_post(path)

            # Make sure that it is not None
            if post is None: return

            # Add the post to the list
            created_posts.append(post)

        # Iterate through all the files
        for (md5, path) in file_hashes.items():
            # Check if we should thread
            if not multi_thread:
                # Create the post
                create_post(path)

                # Continue to the next file
                continue

            # Check if we have reached the maximum number of threads
            if len(threads) >= max_concurrent_threads:
                # Get the first thread
                thread = threads.pop(0)

                # Wait for the thread to finish
                thread.join()
                
                # Close the thread
                thread._stop()
                thread._delete()

            # Create a thread for the file
            thread = threading.Thread(target=create_post, args=(path,))

            # Add the thread to the list
            threads.append(thread)

            # Start the thread
            thread.start()
        
        # Wait for all the threads to finish
        for thread in threads:
            # TODO this is repeated code, make this a function
            # Wait for the thread to finish
            thread.join()

            # Remove the thread
            thread._stop()
            thread._delete()
        
        # Return the created posts
        return created_posts

    def should_search_file(self, path : str) -> bool:
        """Checks if the file should be searched"""

        # Get the file_path
        file_path = Path(path)
        file_path = file_path.resolve()

        # Make sure it is an acceptable file type
        try:
            Post.validate_file(file_path=file_path)
        except:
            # If it is not an acceptable file type, return false
            return False

        # Make sure that it is a child of the scanner path
        scanner_path = Path(self.path)
        scanner_path = scanner_path.resolve()
        
        if not str(file_path).startswith(str(scanner_path)): return False
        
        # Get the checksum
        md5 = boorutils.get_file_checksum(path)

        # Make sure that the file is not already in the database as a post
        if Post.objects.filter(md5=md5).exists(): return False
        
        boorus = self.boorus
        checked_boorus = 0
        # Check all of the local boorus
        for booru in self.boorus.all():
            # Make sure that the file is not already in the database as a result
            if SearchResult.objects.filter(md5=md5, booru=booru).exists(): continue

            # Increment the checked boorus
            checked_boorus += 1
        
        # Make sure that we need to check at least one booru
        if checked_boorus == 0: return False

        # All checks passed, return true
        return True

    def search_file(self, path : str) -> bool:
        """Searches for a file"""

        # Get the md5 hash for the file
        md5 = boorutils.get_file_checksum(path)

        # Get the results
        results = SearchResult.objects.filter(md5=md5, found=True)

        bs = [i for i in self.boorus]

        # Check that we have work to do
        for result in results:
            # Get the booru
            booru = result.booru

            # Ignore the check if the booru is not in the list
            if booru not in bs: continue

            # Ignore check if the result is stale
            if result.stale: continue
            
            # Remove the booru from the list
            bs.remove(booru)
        
        new_find = False
        for booru in bs:
            # Search the booru
            result = booru.search_booru_md5(md5)

            # Save the result
            result.save()

            # If we found a result, then mark that we found a new result
            new_find = result.found or new_find
        
        return new_find
