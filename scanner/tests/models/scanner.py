from django.test import TestCase

from scanner.models import Booru, Scanner, SearchResult, Tag
from booru.models import Rating

import booru.tests.testutils as booru_testutils
import scanner.tests.testutils as scanner_testutils
import booru.boorutils as boorutils

import homebooru.settings

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