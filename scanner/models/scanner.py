from django.db import models
from django.contrib.auth.models import User
from django.apps import apps

import homebooru.settings

import booru.boorutils as boorutils
from booru.models.posts import Rating, Post
from booru.models.tags import Tag

from .booru import Booru
from .searchresult import SearchResult

import os
import datetime
from pathlib import Path

class Scanner(models.Model):
    # The name of the scanner
    name = models.CharField(unique=True, blank=False, null=False, max_length=256)

    # The path for the root directory of the scanner
    path = models.CharField(unique=True, blank=False, null=False, max_length=512)

    # The owner of all of the found posts
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    # The tags to automatically add to new posts
    auto_tags = models.ManyToManyField(Tag, blank=True, related_name='auto_tags')

    # The boorus to search, by default all of them
    search_boorus = models.ManyToManyField(Booru, blank=True, related_name='boorus')

    # Specify if we should prune the results on startup
    auto_prune_results = models.BooleanField(default=True)

    # Specify if we should add posts on failure
    add_posts_on_failure = models.BooleanField(default=False)

    # The tags to be automatically added to posts that failed to be found
    auto_failure_tags = models.ManyToManyField(Tag, blank=True, related_name='auto_failure_tags')

    @property
    def status(self):
        """Returns the status of the scanner"""

        # Get the ScannerStatus model
        ScannerStatus = apps.get_model('scanner', 'ScannerStatus')

        # Get the status
        status = ScannerStatus.objects.filter(scanner=self)

        if not status.exists(): 
            # Create a new status
            status = ScannerStatus(scanner=self)
            status.save()
        else:
            # Get the status
            status = status.first()
        
        # Return the status
        return str(status)

    # Setter for the status field
    def __set_status(self, new_status : str):
        """Sets the status of the scanner"""

        # Get the ScannerStatus model
        ScannerStatus = apps.get_model('scanner', 'ScannerStatus')

        # Delete all previous statuses
        status = ScannerStatus.objects.filter(scanner=self)
        
        # Remove it if it exists
        if status.exists(): status.delete()

        # Create a new status
        status = ScannerStatus(scanner=self, status=new_status)

        # Save the status
        status.save()

        # Return the status
        return status

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
        
        # Automatically add the auto failure tags
        if self.add_posts_on_failure and not results.filter(found=True).exists():
            for tag in self.auto_failure_tags.all():
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
        if len(tags_list) == 0: return None

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
        
        if self.add_posts_on_failure:
            # Make sure that we have at least one auto tag or auto failure tag
            if self.auto_failure_tags.all().count() == 0 and self.auto_tags.all().count() == 0:
                raise ValueError('No auto tags or auto failure tags were specified')

        # Call the superclass save method
        super().save(*args, **kwargs)
    
    def scan(self, create_posts : bool = True, use_default_tags : bool = True) -> list:
        """Scans the scanner for new files"""

        # Check if we should prune the results
        if self.auto_prune_results:
            # Prune the results
            SearchResult.prune()

        # Store the md5 hashes as the key and the path as the value
        file_hashes = {}
        post_hashes = {}

        # Set the status
        self.__set_status('Finding files')

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
                if md5 in file_hashes or md5 in post_hashes: continue

                # Check if we should search the file
                if self.should_search_file(path):
                    # Add the file to the list
                    file_hashes[md5] = path

                    continue

                # Check if we should create the post
                if self.should_create_post(path):
                    # Add the file to the list
                    post_hashes[md5] = path

                    continue
        
        # Save the total files
        total_files = len(file_hashes) + len(post_hashes)

        # Update the status
        self.__set_status(f'Looking up {len(file_hashes)} files')

        # Store the created posts
        created_posts = []

        # Iterate through all the files to search for
        for (md5, path) in file_hashes.items():
            # Search for the file
            if not self.search_file(path) and not self.add_posts_on_failure: continue

            # ... Successfully found the file

            # Add the file to the post hashes
            post_hashes[md5] = path

        # Update the status
        self.__set_status(f'Creating {len(post_hashes)} new posts')

        # Iterate through all the files to create posts for
        for (md5, path) in post_hashes.items():
            # Create the post
            post = self.create_post(path)

            # Make sure that it is not None
            if post is None: continue

            # Add the post to the list
            created_posts.append(post)
        
        # Update the status
        self.__set_status(f'Finished at {datetime.datetime.now()} creating {len(created_posts)} new posts, {total_files} new files were detected, {len(file_hashes)} files were scanned')

        # Return the created posts
        return created_posts

    def should_create_post(self, path : str) -> bool:
        """Returns whether or not we should create a post for the file"""

        # Get the md5 hash of the file
        md5 = boorutils.get_file_checksum(path)

        # Check that there are search results for the file
        if not SearchResult.objects.filter(md5=md5).exists() and not self.add_posts_on_failure: return False

        # Check if there are already posts for the file
        if Post.objects.filter(md5=md5).exists(): return False

        # Return true
        return True

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

    class Meta:
        permissions = (
            ('scan', 'Can use a scanner'),
        )