from django.test import TestCase

from scanner.models import Booru, Scanner, SearchResult, Tag, Post
from booru.models import Rating

import booru.tests.testutils as booru_testutils
import scanner.tests.testutils as scanner_testutils
import booru.boorutils as boorutils

import homebooru.settings

import shutil
import os
import datetime

class BoorusTest(TestCase):
    def setUp(self):
        # Create a scanner
        self.scanner = Scanner(name='test_scanner', path=booru_testutils.CONTENT_PATH)
        self.scanner.save()

        # Create some boorus
        self.boorus = []
        for booru_url in scanner_testutils.VALID_BOORUS:
            booru = Booru(url=booru_url, name='imagebooru ' + str(len(self.boorus)))
            booru.save()

            self.boorus.append(booru)


    def test_expected_boorus(self):
        """Returns expected boorus"""

        # Add a booru to the scanner
        self.scanner.search_boorus.add(self.boorus[0])
        self.scanner.save()

        # Get the expected boorus
        expected_boorus = [self.boorus[0]]

        # Get the actual boorus
        actual_boorus = self.scanner.boorus.all()

        # Make sure the same amount of boorus are returned
        self.assertEqual(len(expected_boorus), len(actual_boorus))
    
        # Make sure it was the expected booru
        for booru in expected_boorus:
            self.assertTrue(booru in actual_boorus)

    def test_empty_boorus(self):
        """Returns all boorus if none are specified"""
        # Get the expected boorus
        expected_boorus = self.boorus

        # Get the actual boorus
        actual_boorus = self.scanner.boorus

        # Make sure the same amount of boorus are returned
        self.assertEqual(len(expected_boorus), len(actual_boorus))

        # Make sure all boorus are returned
        for booru in expected_boorus:
            self.assertTrue(booru in actual_boorus)

class ScannerStrTest(TestCase):
    def setUp(self):
        self.scanner = Scanner(name='test_scanner', path=booru_testutils.CONTENT_PATH)
        self.scanner.save()

    def test_str(self):
        """Returns the name of the scanner"""
        self.assertEqual(str(self.scanner), 'test_scanner')

class DefaultTagsTest(TestCase):
    def setUp(self):
        self.og_setting = homebooru.settings.SCANNER_USE_DEFAULT_TAGS
        homebooru.settings.SCANNER_USE_DEFAULT_TAGS = True

        self.og_tags = homebooru.settings.SCANNER_DEFAULT_TAGS
        homebooru.settings.SCANNER_DEFAULT_TAGS = ['test_tag', 'test_tag2']

        self.scanner = Scanner(name='test_scanner', path=booru_testutils.CONTENT_PATH)
        self.scanner.save()
    
    def tearDown(self):
        homebooru.settings.SCANNER_USE_DEFAULT_TAGS = self.og_setting
        homebooru.settings.SCANNER_DEFAULT_TAGS = self.og_tags

    def test_default_tags(self):
        """Returns the default tags"""

        # Get the raw tags
        raw_tags = homebooru.settings.SCANNER_DEFAULT_TAGS

        # Get the actual tags
        actual_tags = self.scanner.default_tags

        for tag in actual_tags:
            raw_tag = tag.tag
            self.assertTrue(raw_tag in raw_tags, 'Tag ' + raw_tag + ' not in ' + str(raw_tags))

            # Remove the tag from the raw tags (i.e. only appear once)
            raw_tags.remove(raw_tag)
    
    def test_default_tags_not_used(self):
        """Returns no default tags if the scanner does not use them"""
        homebooru.settings.SCANNER_USE_DEFAULT_TAGS = False

        # Get the actual tags
        actual_tags = self.scanner.default_tags

        # Make sure that the actual tags are empty
        self.assertEqual(len(actual_tags), 0)

class ScannerSaveTest(TestCase):
    def test_rejects_invalid_path(self):
        """Rejects invalid paths"""

        scanner = Scanner(name='test_scanner', path='/invalid/path')
        self.assertRaises(ValueError, scanner.save)
    
    def test_rejects_non_directory(self):
        """Rejects non-directory paths"""

        scanner = Scanner(name='test_scanner', path=booru_testutils.FELIX_PATH)
        self.assertRaises(ValueError, scanner.save)
    
    def test_accepts_directory(self):
        """Accepts directory paths"""

        scanner = Scanner(name='test_scanner', path=booru_testutils.CONTENT_PATH)
        scanner.save()

        self.assertTrue(scanner.pk is not None)

class ScannerCreatePostTest(TestCase):
    fixtures = ['ratings.json']

    temp_storage = booru_testutils.TempStorage()

    def setUp(self):
        # Disable default tags
        self.og_setting = homebooru.settings.SCANNER_USE_DEFAULT_TAGS
        homebooru.settings.SCANNER_USE_DEFAULT_TAGS = False

        self.temp_storage.setUp()

        # Create a scanner
        self.scanner = Scanner(name='test_scanner', path=booru_testutils.CONTENT_PATH)
        self.scanner.save()

        # Get some booru urls
        self.booru_urls = [i for i in scanner_testutils.VALID_BOORUS]

        # Remove the / from the end of the urls and append them
        # This probably shouldn't be a thing but it's easier to test this way
        new_urls = []
        for url in self.booru_urls:
            if url[-1] == '/':
                new_urls.append(url[:-1])
            
        # Add the urls
        self.booru_urls += new_urls

        # Create some boorus
        self.boorus = []

        for booru_url in self.booru_urls:
            booru = Booru(url=booru_url, name='imagebooru ' + str(len(self.boorus)))
            booru.save()

            self.boorus.append(booru)
        
        # Create some results
        self.result_path = booru_testutils.FELIX_PATH

        # get the md5
        self.md5 = boorutils.get_file_checksum(self.result_path)

        self.results = []
        for i in range(0, len(self.boorus)):
            result = SearchResult(
                booru=self.boorus[i],
                md5=self.md5,
                found=True,
                raw_rating='safe',
                source='https://example.com/'
            )
            result.save()

            # Add a tag to the result
            result.tags = 'common_tag booru_' + str(i)
            result.save()

            self.results.append(result)
        
        # Make sure there are more than 2 results
        self.assertGreater(len(self.results), 2)
    
    def tearDown(self):
        self.temp_storage.tearDown()
        homebooru.settings.SCANNER_USE_DEFAULT_TAGS = self.og_setting

    def test_selects_mode_rating(self):
        """Selects the most common rating"""

        # Create the post
        post = self.scanner.create_post(self.result_path)
        post.save()

        # Make sure that the post rating is safe
        self.assertEqual(post.rating.name, 'safe')

        # Delete the post
        post.delete()

        # Update some of the results to be questionable
        questionable = Rating.objects.get(name='questionable')
        for i in range(1, len(self.results)):
            self.results[i].raw_rating = str(questionable)
            self.results[i].save()
        
        # Create the post
        post = self.scanner.create_post(self.result_path)
        post.save()

        # Make sure that the post rating is questionable
        self.assertEqual(post.rating, questionable)
    
    def test_selects_mode_source(self):
        """Selects the most common source"""

        # Create the post
        post = self.scanner.create_post(self.result_path)
        post.save()

        # Make sure that the post source is correct
        self.assertEqual(post.source, 'https://example.com/')

        # Delete the post
        post.delete()

        # Update some of the results to have a different source
        for i in range(1, len(self.results)):
            self.results[i].source = 'https://sample.com/'
            self.results[i].save()
        
        # Create the post
        post = self.scanner.create_post(self.result_path)
        post.save()

        # Make sure that the post source is correct but different this time
        self.assertEqual(post.source, 'https://sample.com/')

    def test_merges_tags(self):
        """Merges the tags"""

        # Create the post
        post = self.scanner.create_post(self.result_path)
        post.save()

        raw_tags = []

        for tag in post.tags.all():
            raw_tags.append(tag.tag)


        raw_tags.sort()
        raw_tags = ' '.join(raw_tags)

        # Make sure that the post tags are correct
        self.assertEqual(raw_tags, 'booru_0 booru_1 booru_2 booru_3 common_tag')
    
    def test_adds_auto_tags(self):
        """Adds auto tags"""

        # Add some auto tags to the scanner
        test_tag = Tag(tag='test_tag')
        test_tag.save()

        self.scanner.auto_tags.add(test_tag)
        self.scanner.save()

        # Create the post
        post = self.scanner.create_post(self.result_path)
        post.save()

        # Check the tags
        raw_tags = []

        for tag in post.tags.all():
            raw_tags.append(tag.tag)

        raw_tags.sort()
        raw_tags = ' '.join(raw_tags)

        # Make sure that the post tags are correct
        self.assertEqual(raw_tags, 'booru_0 booru_1 booru_2 booru_3 common_tag test_tag')
    
    def test_none_with_no_results(self):
        """Returns None if there are no results"""

        # Delete the results
        for result in self.results:
            result.delete()

        # Create the post
        post = self.scanner.create_post(self.result_path)

        # Make sure that the post is None
        self.assertEqual(post, None)

class ScannerShouldSearchTest(TestCase):
    def setUp(self):
        self.scanner = Scanner(name='test_scanner', path=booru_testutils.CONTENT_PATH)
        self.scanner.save()

        # Create a booru
        self.booru = Booru(url=scanner_testutils.VALID_BOORUS[0], name='imagebooru')
        self.booru.save()

        # Copy an image to /tmp/scanner.jpg
        shutil.copy(booru_testutils.FELIX_PATH, '/tmp/scanner.jpg')

    def tearDown(self):
        # Delete the image
        os.remove('/tmp/scanner.jpg')

    def test_invalid_file(self):
        """Returns false if the file is an invalid type"""

        self.assertFalse(self.scanner.should_search_file(booru_testutils.NON_IMAGE_PATH))

    def test_outside_path(self):
        """Returns false if the file is outside the path"""
    
        self.assertFalse(self.scanner.should_search_file('/tmp/scanner.jpg'))
    
    def test_valid_file(self):
        """Returns true if the file is valid"""

        self.assertTrue(self.scanner.should_search_file(booru_testutils.FELIX_PATH))


    def test_post(self):
        """Returns false if the image is already a post"""

        # Create a post
        post = Post.create_from_file(booru_testutils.FELIX_PATH)
        post.save()

        self.assertFalse(self.scanner.should_search_file(booru_testutils.FELIX_PATH))
    
    def test_result(self):
        """Returns false if there are valid results"""

        # Create a result
        result = SearchResult(
            booru=self.booru,
            md5=boorutils.get_file_checksum(booru_testutils.FELIX_PATH),
            found=True,
            raw_rating='safe',
            source='https://example.com/',
            tags='common_tag'
        )
        result.save()

        self.assertFalse(self.scanner.should_search_file(booru_testutils.FELIX_PATH))

class ScannerSearchFileTest(TestCase):
    def setUp(self):
        self.scanner = Scanner(name='test_scanner', path=booru_testutils.CONTENT_PATH)
        self.scanner.save()

        # Create a booru
        self.booru = Booru(url=scanner_testutils.VALID_BOORUS[0], name='imagebooru')
        self.booru.save()

        self.booru_image = booru_testutils.BOORU_IMAGE
    
    def test_new_found(self):
        """Returns expected results for a new file"""

        # Scan and add the results to the database
        self.assertTrue(self.scanner.search_file(self.booru_image))

        # Check the results
        results = SearchResult.objects.filter(booru=self.booru)

        # Make sure there is one result
        self.assertEqual(len(results), 1)

        # Get the first result
        result = results.first()

        # Make sure that it is is found
        self.assertTrue(result.found)

        # Make sure that the result isn't None
        self.assertIsNotNone(result, 'Didn\'t return a result')

        # Make sure that the result has tags
        self.assertGreater(len(result.tags), 0)

        # Make sure that the tags contain the correct tags
        for tag in ['astolfo_(fate)', '1boy', 'pink_hair']:
            self.assertIn(tag, result.tags)

        # Make sure that the result has a rating
        self.assertEqual(result.raw_rating, 'safe')
    
    def test_override_stale(self):
        """Overrides stale results with fresh results"""

        # Create a stale result
        result = SearchResult(
            booru=self.booru,
            md5=boorutils.get_file_checksum(self.booru_image),
            found=True,
            raw_rating='safe',
            source='https://example.com/',
            tags='common_tag'
        )
    
        result.save()

        # Make it stale
        result.created = datetime.datetime(2000, 1, 1).astimezone()
        result.save()

        # Make sure it is stale
        self.assertTrue(result.stale)

        # Scan and add the results to the database
        self.assertTrue(self.scanner.search_file(self.booru_image))

        # Check the results
        results = SearchResult.objects.filter(booru=self.booru)

        # Make sure there is one result
        self.assertEqual(len(results), 1)

        # Get the first result
        result = results.first()

        # Make sure that it is is found
        self.assertTrue(result.found)

        # Make sure that the result isn't None
        self.assertIsNotNone(result, 'Didn\'t return a result')

        # Make sure that the result has different tags
        self.assertNotEqual(result.tags, 'common_tag')

        # Make sure that it has expected tags
        for tag in ['astolfo_(fate)', '1boy', 'pink_hair']:
            self.assertIn(tag, result.tags)
        
        # Make sure that the old tag is not in the new tags
        self.assertNotIn('common_tag', result.tags)

        # Make sure that the result has a rating
        self.assertEqual(result.raw_rating, 'safe')
        
        # Make sure that it doesn't have a source
        self.assertEqual(result.source, None)

    def test_override_non_found(self):
        """Overrides when found is false"""

        # Create a result
        result = SearchResult(
            booru=self.booru,
            md5=boorutils.get_file_checksum(self.booru_image),
            found=False,
        )
        result.save()

        # Scan and add the results to the database
        self.assertTrue(self.scanner.search_file(self.booru_image))

        # Check the results
        results = SearchResult.objects.filter(booru=self.booru)

        # Make sure there is one result
        self.assertEqual(len(results), 1)

        # Get the first result
        result = results.first()

        # Make sure that it is is found
        self.assertTrue(result.found)

        # Make sure that the result has tags
        self.assertGreater(len(result.tags), 0)

        # Make sure that the tags contain the correct tags
        for tag in ['astolfo_(fate)', '1boy', 'pink_hair']:
            self.assertIn(tag, result.tags)
        
        # Make sure that the result has a rating
        self.assertEqual(result.raw_rating, 'safe')

    def test_ignores_non_stale(self):
        """Ignores checks for non-stale result"""

        # Create a result
        result = SearchResult(
            booru=self.booru,
            md5=boorutils.get_file_checksum(self.booru_image),
            found=True,
            raw_rating='explicit',
            source='https://example.com/',
            tags='common_tag'
        )
        result.save()

        # Scan and add the results to the database
        self.assertFalse(self.scanner.search_file(self.booru_image))

        # Check the results
        results = SearchResult.objects.filter(booru=self.booru)

        # Make sure there is one result
        self.assertEqual(len(results), 1)

        # Get the first result
        result = results.first()

        # Make sure that it is is found
        self.assertTrue(result.found)

        # Make sure that the result has tags
        self.assertGreater(len(result.tags), 0)

        # Make sure that it has expected the tag
        self.assertEqual(result.tags, 'common_tag')

        # Check the source
        self.assertEqual(result.source, 'https://example.com/')

        # Make sure that the result has a rating
        self.assertEqual(result.raw_rating, 'explicit')
    
    def test_ignores_other_boorus(self):
        """Ignores boorus that are not its own"""

        # Create another booru
        other_booru = Booru(url=scanner_testutils.VALID_BOORUS[1], name='imagebooru 2')
        other_booru.save()

        # Create a result
        result = SearchResult(
            booru=other_booru,
            md5=boorutils.get_file_checksum(self.booru_image),
            found=True,
            raw_rating='safe',
            source='https://example.com/',
            tags='common_tag'
        )
        result.save()

        # Scan and add the results to the database
        self.assertTrue(self.scanner.search_file(self.booru_image))

        # Check the results
        results = SearchResult.objects.filter(booru=self.booru)

        # Make sure there is one result
        self.assertEqual(len(results), 1)

        # Get the first result
        result = results.first()

        # Make sure that it is is found
        self.assertTrue(result.found)

        # Make sure that the result has the astolfo tag
        self.assertIn('astolfo_(fate)', result.tags)

        # Check that the other result was not touched
        results = SearchResult.objects.filter(booru=other_booru)

        # Make sure there is one result
        self.assertEqual(len(results), 1)

        # Get the first result
        result = results.first()

        # Make sure that it is is found
        self.assertTrue(result.found)

        # Make sure that the result has the other tag
        self.assertIn('common_tag', result.tags)

class ScannerScanTest(TestCase):
    temp_scan_dir = scanner_testutils.TempScanFolder()

    fixtures = ['ratings.json']

    def setUp(self):
        self.temp_scan_dir.add_file(booru_testutils.BOORU_IMAGE)
        self.temp_scan_dir.setUp()

        # Create the scanner
        self.scanner = Scanner(
            path=str(self.temp_scan_dir.folder),
            name='Test Scanner'
        )
        self.scanner.save()

        # Create a booru
        self.booru = Booru(
            url=scanner_testutils.VALID_BOORUS[0],
            name='imagebooru'
        )
        self.booru.save()

        # Add the booru to the scanner
        self.scanner.search_boorus.add(self.booru)
        self.scanner.save()
    
    def tearDown(self):
        self.temp_scan_dir.tearDown()

        self.temp_scan_dir.remove_all_files()
    
    def test_scan_dir(self):
        """Scans a directory"""

        # Run the scan
        posts = self.scanner.scan()

        # Make sure that there is one post
        self.assertEqual(len(posts), 1)

        # Get the first post
        post = posts[0]

        # Make sure that it is the correct post
        self.assertEqual(post.md5, boorutils.get_file_checksum(booru_testutils.BOORU_IMAGE))

        # Make sure that it has tags
        self.assertGreater(post.tags.all().count(), 1)

        # Make sure that the item has a rating
        self.assertEqual(str(post.rating), 'safe')
    
    # TODO test recursive scan
    # TODO test scan with multiple boorus
    # TODO test auto_prune
    # TODO test auto-tagging