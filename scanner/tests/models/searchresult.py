from django.test import TestCase

from scanner.models import SearchResult, Booru, Rating, Post

from datetime import datetime

import scanner.tests.testutils as scanner_testutils
import booru.boorutils as boorutils

class ResultStaleTest(TestCase):
    stale_date = datetime(2020, 2, 1)

    def setUp(self):
        # Create a booru
        self.booru = Booru(url=scanner_testutils.VALID_BOORUS[0], name='imagebooru')
        self.booru.save()

    def test_stale(self):
        """Returns true with stale results"""

        # Create a new result
        result = SearchResult(md5=boorutils.hash_str('s'), booru=self.booru)
        result.save()

        result.created = self.stale_date
        result.save()

        # Make sure that the result is stale
        self.assertTrue(result.stale)
    
    def test_not_stale(self):
        """Returns false with non-stale results"""

        # Create a new result
        result = SearchResult(created=datetime.now(), booru=self.booru)

        # Make sure that the result is not stale
        self.assertFalse(result.stale)

class ResultPruneTest(TestCase):
    stale_date = datetime(2020, 2, 1)

    def setUp(self):
        # Create a new booru
        self.booru = Booru.objects.create(
            name='imageboard',
            url=scanner_testutils.VALID_BOORUS[0]
        )
        self.booru.save()

        # Create 32 stale results
        for i in range(32):
            r = SearchResult(booru=self.booru, md5=boorutils.hash_str('stale' + str(i)))
            r.save()

            r.created = self.stale_date
            r.save()
        
        # Create 32 non-stale results
        for i in range(32):
            SearchResult(booru=self.booru, md5=boorutils.hash_str('not stale' + str(i))).save()
        
    def test_deletes_stale(self):
        """Deletes stale results"""

        # Prune the results
        SearchResult.prune()

        # Get all the results
        results = SearchResult.objects.all()

        # Make sure that the correct number of results were deleted
        self.assertEqual(results.count(), 32)

        # Make sure they're all not stale
        for result in results:
            self.assertFalse(result.stale)

class ResultStrTest(TestCase):
    def setUp(self):
        self.booru = Booru(url=scanner_testutils.VALID_BOORUS[0], name='imagebooru')
        self.booru.save()

        self.result = SearchResult(
            booru=self.booru,
            md5='88d087c21ed70168c35ed4b503e641ea',
            tags='tag1 tag2 tag3',
            raw_rating='safe',
            found=True
        )
        self.result.save()
    
    def test_str(self):
        """Returns a string representation of the result"""

        # Make sure that the string representation is correct
        self.assertEqual(str(self.result), self.result.md5 + ' @ ' + self.booru.name)

class ResultRatingTest(TestCase):
    fixtures = ['ratings.json']

    @property
    def ratings(self):
        return [
            r.name for r in Rating.objects.all()
        ]

    def setUp(self):
        self.booru = Booru(url=scanner_testutils.VALID_BOORUS[0], name='imagebooru')
        self.booru.save()
    
    def test_rating(self):
        """Returns the rating of the result"""

        for rating in self.ratings:
            result = SearchResult(
                booru=self.booru,
                md5='88d087c21ed70168c35ed4b503e641ea',
                tags='tag1 tag2 tag3',
                raw_rating=rating,
                found=True
            )
            result.save()

            # Make sure that the rating is correct
            self.assertEqual(result.raw_rating, rating)

            # Make sure that the rating is correct
            self.assertEqual(result.rating, Rating.objects.get(name=rating))

            result.delete()
    
    def test_invalid(self):
        """Defaults it to the default rating"""

        # Get the default rating
        default = Rating.get_default()

        # Create a new result
        result = SearchResult(
            booru=self.booru,
            md5='88d087c21ed70168c35ed4b503e641ea',
            tags='tag1 tag2 tag3',
            raw_rating='invalid',
            found=True
        )

        # Make sure that the rating is correct
        self.assertEqual(result.raw_rating, 'invalid')

        # Make sure that the rating is correct
        self.assertEqual(result.rating, default)
    
    def test_not_found(self):
        """Returns nothing if the result is not found"""

        # Create a new result
        result = SearchResult(
            booru=self.booru,
            md5='88d087c21ed70168c35ed4b503e641ea',
            raw_rating='safe', # This will never happen but still let's see if it ignores data
            found=False
        )

        # Make sure that the rating is correct
        self.assertEqual(result.raw_rating, 'safe')

        # Make sure that the rating is correct
        self.assertEqual(result.rating, None)

class ResultSaveDupePostTest(TestCase):
    def setUp(self):
        self.booru = Booru(url=scanner_testutils.VALID_BOORUS[0], name='imagebooru')
        self.booru.save()

        #  Create a post
        self.post = Post(
            md5=boorutils.hash_str('s'),
            folder=1,
            width=1,
            height=1
        )
        self.post.save()

    def test_rejects_for_post(self):
        # Create a new result with same md5
        result = SearchResult(
            booru=self.booru,
            md5=self.post.md5,
            tags='tag1 tag2 tag3',
            raw_rating='safe',
            found=True
        )

        # Make sure that it throws an error on save
        with self.assertRaises(Exception):
            result.save()
        
        # Delete the post
        self.post.delete()

        # Make sure it saves
        result.save()