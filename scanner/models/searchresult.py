from django.db import models

import homebooru.settings

from booru.models.posts import Rating, Post
from .booru import Booru

from datetime import datetime

class SearchResult(models.Model):
    # The booru that was scanned
    booru = models.ForeignKey(Booru, on_delete=models.CASCADE, blank=False)

    # The MD5 hash of the file
    md5 = models.TextField(blank=False, null=False)

    # The raw tags list
    tags = models.TextField(blank=True)

    # The source URL of the file
    source = models.URLField(blank=True)

    # Raw Rating from the booru
    raw_rating = models.TextField(blank=True)

    # Mark if the file was found
    found = models.BooleanField(default=False)

    # Mark when the search result was created
    created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def get_stale_date():
        """The date after which a search result is considered stale"""

        return datetime.fromtimestamp(
            datetime.now().timestamp() - homebooru.settings.SCANNER_STALENESS_THRESHOLD
        )

    @property
    def stale(self) -> bool:
        """Returns true if the search result is stale"""

        return self.created.timestamp() < SearchResult.get_stale_date().timestamp()
    
    @staticmethod
    def prune():
        """Prunes stale search results"""

        # Find all the stale search results
        stale_results = SearchResult.objects.filter(created__lte=SearchResult.get_stale_date())

        # Delete them
        stale_results.all().delete()

    @property
    def rating(self) -> Rating:
        """The mapped rating from the booru"""

        # If we cannot find the rating, return None
        if not self.found:
            return None

        # Attempt to convert the rating
        try:
            return Rating.objects.get(name=self.raw_rating)
        except Rating.DoesNotExist:
            # If it cannot be found, return the default rating
            return Rating.get_default()

    class Meta:
        # Make sure that the md5 and the booru are unique
        unique_together = ('md5', 'booru')

    def __str__(self):
        return self.md5 + ' @ ' + self.booru.name
    
    def save(self, *args, **kwargs):
        # Make sure that a post with the same MD5 hash does not exist
        if Post.objects.filter(md5=self.md5).exists():
            raise ValueError('A post with the same MD5 hash already exists')

        # Call the superclass save method
        super().save(*args, **kwargs)
