from django.test import TestCase, modify_settings

from scanner.models import Booru, Scanner, SearchResult, ScannerError, ScannerIgnore
from booru.models import Rating, Post, Tag

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

        if not scanner_testutils.SHOULD_TEST_EXT_BOORU:
            self.skipTest('Skipping external booru tests')
            return

        # Add a booru to the scanner
        self.scanner.boorus.add(self.boorus[0])
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
    
    def test_rejects_sub_directory(self):
        """Rejects directories that are already being scanned as sub-directories"""

        # Create a scanner
        scanner = Scanner(name='test_scanner', path=booru_testutils.TEST_DATA_PATH)
        scanner.save()

        # Create a sub-scanner
        sub_scanner = Scanner(name='sub_test_scanner', path=booru_testutils.CONTENT_PATH)
        self.assertRaises(ValueError, sub_scanner.save)
    
    def test_rejects_sub_directory_deep(self):
        """Rejects directories that are deeply nested"""

        # Create a scanner for app
        scanner = Scanner(name='test_scanner', path='/app')
        scanner.save()

        # Create a sub-scanner for the content directory
        sub_scanner = Scanner(name='sub_test_scanner', path=booru_testutils.CONTENT_PATH)
        self.assertRaises(ValueError, sub_scanner.save)
    
    def test_rejects_non_abs_sub_directory(self):
        """Rejects directories that are sub-directories of the scanner path (non-absolute)"""

        # Create a scanner
        scanner = Scanner(name='test_scanner', path='./assets')
        scanner.save()

        # Create a sub-scanner
        sub_scanner = Scanner(name='sub_test_scanner', path='/app/assets/TEST_DATA')
        self.assertRaises(ValueError, sub_scanner.save)
    
    def test_rejects_parent(self):
        """Rejects directories that are parent directories of the scanner path"""

        # Create a scanner
        scanner = Scanner(name='test_scanner', path='/app/assets/TEST_DATA')
        scanner.save()

        # Create a sub-scanner
        sub_scanner = Scanner(name='sub_test_scanner', path='/app')
        self.assertRaises(ValueError, sub_scanner.save)

    # TODO maybe check for symbolic links being used as paths

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

        if not scanner_testutils.SHOULD_TEST_EXT_BOORU:
            self.skipTest('Skipping external booru tests')
            return

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

            # Add to the scanner
            self.scanner.boorus.add(booru)
            self.scanner.save()
        
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

        # TODO Use modify_settings
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
    
    def test_add_posts_on_failure_correct(self):
        """add_posts_on_failure is flagged correctly"""

        # Clear the auto_failure_tags
        self.scanner.auto_failure_tags.clear()
        self.scanner.save()

        # Make sure that add_posts_on_failure is false
        self.assertFalse(self.scanner.add_posts_on_failure)

        # Add a tag to the auto_failure_tags
        test_tag = Tag(tag='test_tag')
        test_tag.save()

        self.scanner.auto_failure_tags.add(test_tag)
        self.scanner.save()

        # Make sure that add_posts_on_failure is true
        self.assertTrue(self.scanner.add_posts_on_failure)
    
    def test_gets_mode_rating_ignore_not_found(self):
        """Selects the most common rating ignoring not found"""

        questionable = Rating.objects.get(name='questionable')
        explicit = Rating.objects.get(name='explicit')

        # Update some of the results to be questionable
        for i in range(1, len(self.results)):
            self.results[i].raw_rating = str(questionable)
            self.results[i].found = False
            self.results[i].save()
        
        # Update the first result to be found and explicit
        self.results[0].found = True
        self.results[0].raw_rating = str(explicit)
        self.results[0].save()

        # Create the post
        post = self.scanner.create_post(self.result_path)
        post.save()

        # Make sure that the post rating is explicit
        self.assertEqual(post.rating, explicit)


class ScannerShouldSearchTest(TestCase):
    def setUp(self):
        self.scanner = Scanner(name='test_scanner', path=booru_testutils.CONTENT_PATH)
        self.scanner.save()

        if not scanner_testutils.SHOULD_TEST_EXT_BOORU:
            self.skipTest('Skipping external booru tests')
            return

        # Create a booru
        self.booru = Booru(url=scanner_testutils.VALID_BOORUS[0], name='imagebooru')
        self.booru.save()

        # Add the booru to the scanner  
        self.scanner.boorus.add(self.booru)
        self.scanner.save()

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

    def test_global_ignore(self):
        """Returns false if the file is globally ignored"""

        # Make sure that we should search the file
        self.assertTrue(self.scanner.should_search_file(booru_testutils.FELIX_PATH))

        # Get the MD5
        md5 = boorutils.get_file_checksum(booru_testutils.FELIX_PATH)

        # Create an ignore
        ignore = ScannerIgnore(md5=md5)
        ignore.save()

        self.assertFalse(self.scanner.should_search_file(booru_testutils.FELIX_PATH))
    
    def test_exempt_ignore(self):
        """Returns true if we are exempt to the ignore"""

        # Make sure that we should search the file
        self.assertTrue(self.scanner.should_search_file(booru_testutils.FELIX_PATH))

        # Get the MD5
        md5 = boorutils.get_file_checksum(booru_testutils.FELIX_PATH)

        # Create an ignore
        ignore = ScannerIgnore(md5=md5)
        ignore.save()

        # Add the ignore to the scanner
        self.scanner.exempt_ignores.add(ignore)
        self.scanner.save()

        self.assertTrue(self.scanner.should_search_file(booru_testutils.FELIX_PATH))

        # Remove the exemption
        self.scanner.exempt_ignores.remove(ignore)
        self.scanner.save()

        self.assertFalse(self.scanner.should_search_file(booru_testutils.FELIX_PATH))

class ScannerSearchFileTest(TestCase):
    def setUp(self):
        self.scanner = Scanner(name='test_scanner', path=booru_testutils.CONTENT_PATH)
        self.scanner.save()

        if not scanner_testutils.SHOULD_TEST_EXT_BOORU:
            self.skipTest('Skipping external booru tests')
            return

        # Create a booru
        self.booru = Booru(url=scanner_testutils.VALID_BOORUS[0], name='imagebooru')
        self.booru.save()

        # Add the booru to the scanner
        self.scanner.boorus.add(self.booru)
        self.scanner.save()

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
        self.og_SCANNER_USE_DEFAULT_TAGS = homebooru.settings.SCANNER_USE_DEFAULT_TAGS
        self.og_BOORU_ALLOWED_FILE_EXTENSIONS = [i for i in homebooru.settings.BOORU_ALLOWED_FILE_EXTENSIONS]

        self.temp_scan_dir.add_file(booru_testutils.BOORU_IMAGE)
        self.temp_scan_dir.setUp()

        # Create the scanner
        self.scanner = Scanner(
            path=str(self.temp_scan_dir.folder),
            name='Test Scanner'
        )
        self.scanner.save()

        if not scanner_testutils.SHOULD_TEST_EXT_BOORU:
            self.skipTest('Skipping external booru tests')
            return

        # Create a booru
        self.booru = Booru(
            url=scanner_testutils.VALID_BOORUS[0],
            name='imagebooru'
        )
        self.booru.save()

        # Add the booru to the scanner
        self.scanner.boorus.add(self.booru)
        self.scanner.save()
    
    def tearDown(self):
        homebooru.settings.SCANNER_USE_DEFAULT_TAGS = self.og_SCANNER_USE_DEFAULT_TAGS
        homebooru.settings.BOORU_ALLOWED_FILE_EXTENSIONS = self.og_BOORU_ALLOWED_FILE_EXTENSIONS

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
    
    def test_recursive_search(self):
        """Finds files in subdirectories"""

        # Create a subdirectory
        folder_path = self.temp_scan_dir.folder / 'subdir'
        folder_path.mkdir()

        # Image name
        image_name = scanner_testutils.BOORU_MD5 + booru_testutils.BOORU_IMAGE.suffix

        # Move the file into the subdirectory
        shutil.move(
            str(self.temp_scan_dir.folder / image_name),
            str(folder_path / image_name)
        )

        # Make sure that the original file is gone
        self.assertFalse((self.temp_scan_dir.folder / image_name).exists())

        # Run the scan
        posts = self.scanner.scan()

        # Make sure that there is one post
        self.assertEqual(len(posts), 1)

        # Get the first post
        post = posts[0]

        # Make sure that it is the correct post
        self.assertEqual(post.md5, scanner_testutils.BOORU_MD5)

        # Make sure that it has tags
        self.assertGreater(post.tags.all().count(), 1)

        # Make sure that the item has a rating
        self.assertEqual(str(post.rating), 'safe')

    # TODO test scan with multiple boorus
    
    def test_auto_tag_with_tags(self):
        """Appends tags to images with tags"""

        # Add default tags
        for i in [
            Tag.create_or_get(tag='auto'),
            Tag.create_or_get(tag='tagme')
        ]:
            self.scanner.auto_tags.add(i)
        
        # Save the scanner
        self.scanner.save()

        # Run the scan
        posts = self.scanner.scan()

        # Make sure that there is one post
        self.assertEqual(len(posts), 1)

        # Get the first post
        post = posts[0]

        # Make sure that it has the tags
        for tag in ['auto', 'tagme']:
            self.assertIn(tag, post.tags.all().values_list('tag', flat=True))
        
        # Make sure that the item has a rating
        self.assertEqual(str(post.rating), 'safe')
    
    def test_auto_tag_without_tags(self):
        """Appends tags to images without tags"""

        homebooru.settings.SCANNER_USE_DEFAULT_TAGS = True

        # Create a search result without tags
        result = SearchResult(
            booru=self.booru,
            md5=scanner_testutils.BOORU_MD5,
            found=True,
            raw_rating='safe',
            source='https://example.com/',
            tags=''
        )
        result.save()

        # Add default tags
        for i in [
            Tag.create_or_get(tag='auto'),
            Tag.create_or_get(tag='tagme')
        ]:
            self.scanner.auto_tags.add(i)
        
        # Save the scanner
        self.scanner.save()

        # Run the scan
        posts = self.scanner.scan()

        # Make sure that there is one post
        self.assertEqual(len(posts), 1)

        # Get the first post
        post = posts[0]

        # Make sure that it only has 2 tags
        self.assertEqual(post.tags.all().count(), 2)

        # Make sure that it has the tags
        for tag in ['auto', 'tagme']:
            self.assertIn(tag, post.tags.all().values_list('tag', flat=True))
        
        # Make sure that the item has a rating
        self.assertEqual(str(post.rating), 'safe')

    def test_uses_previous_results(self):
        """Creates posts from previous results if they are not stale"""

        # Create a search result with some tags
        result = SearchResult(
            booru=self.booru,
            md5=scanner_testutils.BOORU_MD5,
            found=True,
            raw_rating='explicit',
            source='https://example.com/',
            tags='tag1 tag2'
        )
        result.save()

        # Run the scan
        posts = self.scanner.scan()

        # Make sure that there is one post
        self.assertEqual(len(posts), 1)

        # Get the first post
        post = posts[0]

        # Make sure it only has 2 tags
        self.assertEqual(post.tags.all().count(), 2)

        # Make sure that it has the tags
        for tag in ['tag1', 'tag2']:
            self.assertIn(tag, post.tags.all().values_list('tag', flat=True))
        
        # Make sure that the item has a rating
        self.assertEqual(str(post.rating), 'explicit')
    
    def test_ignores_previous_stale_results_on_auto_prune(self):
        """Ignores previous results if they are stale with auto pruning"""

        # Create a search result with some tags
        result = SearchResult(
            booru=self.booru,
            md5=scanner_testutils.BOORU_MD5,
            found=True,
            raw_rating='explicit',
            source='https://example.com/',
            tags='tag1 tag2'
        )
        result.save()

        # Make the result stale
        result.created = SearchResult.get_stale_date()
        result.save()

        # Enable auto pruning
        self.scanner.auto_prune_results = True

        # Run the scan
        posts = self.scanner.scan()

        # Make sure that there is one post
        self.assertEqual(len(posts), 1)

        # Get the first post
        post = posts[0]

        # Make sure it has more than 2 tags
        self.assertNotEqual(post.tags.all().count(), 2)

        # Make sure that it doesn't have the original tags
        for tag in ['tag1', 'tag2']:
            self.assertNotIn(tag, post.tags.all().values_list('tag', flat=True))
        
        # Make sure it has the expected tags
        for tag in scanner_testutils.BOORU_TAGS:
            self.assertIn(tag, post.tags.all().values_list('tag', flat=True))

        # Make sure that the item has a rating
        self.assertEqual(str(post.rating), 'safe')

    def setUp_failure(self, remove_old_files=True):
        self.temp_scan_dir.tearDown()

        # Remove the booru image
        if remove_old_files:
            self.temp_scan_dir.remove_all_files()
        
        # Add a new non-booru image
        self.temp_scan_dir.add_file(booru_testutils.GATO_PATH)

        # Copy it
        self.temp_scan_dir.setUp()

        # Configure the scanner
        self.scanner.path                 = self.temp_scan_dir.folder
        self.scanner.auto_prune_results   = True
    
        # Add some tags
        no_here = Tag(tag='no_here')
        no_here.save()

        both = Tag(tag='both')
        both.save()

        # Add the tags to the scanner
        self.scanner.auto_failure_tags.add(no_here)
        self.scanner.auto_tags.add(both)

        # Save the scanner
        self.scanner.save()

    def test_add_posts_on_failure_adds_tags(self):
        """Adds tags to posts that were not found"""

        self.setUp_failure()

        # Run the scan
        posts = self.scanner.scan()

        # Make sure that there is one post
        self.assertEqual(len(posts), 1)

        # Get the first post
        post = posts[0]

        # Make sure that it has the tags
        for tag in ['no_here', 'both']:
            self.assertIn(tag, post.tags.all().values_list('tag', flat=True))
        
        # Make sure it only has 2 tags
        self.assertEqual(post.tags.all().count(), 2)

    def test_add_posts_on_failure_doesnt_add_tags_if_already_added(self):
        """Doesn't add tags to post that were found"""

        self.setUp_failure(False)

        # Run the scan
        posts = self.scanner.scan()

        # Make sure that there are two posts
        self.assertEqual(len(posts), 2)

        # Sort the posts by the amount of tags they have
        posts = sorted(posts, key=lambda x: x.tags.all().count())
        posts.reverse()

        # Get the first post
        post = posts[0]

        # Make sure that it has more than 2 tags
        self.assertNotEqual(post.tags.all().count(), 2)

        # Make sure that it has the correct md5
        self.assertEqual(post.md5, scanner_testutils.BOORU_MD5)

        # Make sure that it doesn't have the 'not here' tag
        self.assertNotIn('no_here', post.tags.all().values_list('tag', flat=True))

        # Make sure that it has the 'both' tag
        self.assertIn('both', post.tags.all().values_list('tag', flat=True))

        # Check the other post
        post = posts[1]

        # Make sure that it has 2 tags
        self.assertEqual(post.tags.all().count(), 2)

        # Make sure that it has both the 'both' and 'not here' tags
        for tag in ['both', 'no_here']:
            self.assertIn(tag, post.tags.all().values_list('tag', flat=True))
        
        # Make sure that it has the correct md5
        self.assertEqual(post.md5, boorutils.get_file_checksum(booru_testutils.GATO_PATH))

    def test_updates_status(self):
        """Updates the status of the scanner"""

        # Check that the status is 'Idle'
        self.assertEqual(self.scanner.status, 'Idle')

        # Run the scan
        self.scanner.scan()

        # Finished at ... creating 1 new posts, 1 new files were detected, 1 files were scanned
        
        # Make sure it starts with 'Finished at'
        self.assertTrue(self.scanner.status.startswith('Finished at'))

        # Make sure that the status ends with the correct amount of new posts and files
        self.assertTrue(self.scanner.status.endswith('1 unique files found, creating 1 new posts, 1 new files were detected, 1 files were scanned, 0 errors occurred'), self.scanner.status)

    def test_auto_prune(self):
        """Automatically removes stale search results"""

        # Enable auto prune
        self.scanner.auto_prune_results = True
        self.scanner.save()

        # Add a stale result
        result = SearchResult(
            booru=self.booru,
            md5=scanner_testutils.BOORU_MD5,
            found=True,
            raw_rating='explicit',
            source='https://example.com/',
            tags='tagme123'
        )
        result.save()

        # Change the date of the result
        result.created = SearchResult.get_stale_date()
        result.save()

        # Run the scan
        posts = self.scanner.scan()

        # Make sure that there is one post
        self.assertEqual(len(posts), 1)

        # Get the first post
        post = posts[0]

        # Make sure that it doesn't have the tags
        self.assertNotIn('tagme123', post.tags.all().values_list('tag', flat=True))

        # Make sure that the item has a rating
        self.assertEqual(str(post.rating), 'safe')
    
    def test_skips_disallowed_extensions(self):
        """Skips files with disallowed extensions"""

        # Remove jpg from the allowed extensions
        homebooru.settings.BOORU_ALLOWED_FILE_EXTENSIONS = ['png']

        # Run the scan
        posts = self.scanner.scan()

        # Make sure that there are no posts
        self.assertEqual(len(posts), 0)

        # Make sure that there are no scan results
        self.assertEqual(SearchResult.objects.count(), 0)

        # Restore the allowed extensions
        homebooru.settings.BOORU_ALLOWED_FILE_EXTENSIONS = self.og_BOORU_ALLOWED_FILE_EXTENSIONS

        # Run the scan
        posts = self.scanner.scan()

        # Make sure that there is one post
        self.assertEqual(len(posts), 1)

        # Get the first post
        post = posts[0]

        # Make sure that it has the correct md5
        self.assertEqual(post.md5, scanner_testutils.BOORU_MD5)

    def test_skips_corrupt(self):
        """Skips corrupt files"""

        # Remove old files
        self.temp_scan_dir.tearDown()

        # Add a corrupt file
        self.temp_scan_dir.add_file(booru_testutils.CORRUPT_IMAGE_PATH)
        
        # Setup
        self.temp_scan_dir.setUp()

        self.scanner.path = self.temp_scan_dir.folder

        # Run the scan
        posts = self.scanner.scan()

        # Make sure there is only one post
        self.assertEqual(len(posts), 1, 'The corrupt file was not skipped')

        # Make sure there is only one scan result (i.e. the corrupt file was skipped)
        self.assertEqual(SearchResult.objects.count(), 1, 'The corrupt file was not skipped when scanning')

        # Make sure that the only scan result is the valid file
        result = SearchResult.objects.first()
        self.assertEqual(result.md5, scanner_testutils.BOORU_MD5)
    
    def test_corrupt_image(self):
        """Make sure that it counts a corrupt image as an error"""

        # Remove all images 
        self.temp_scan_dir.tearDown()
        self.temp_scan_dir.remove_all_files()

        # Add a corrupt file
        self.temp_scan_dir.add_file(booru_testutils.CORRUPT_FELIX_PATH)

        # Setup
        self.temp_scan_dir.setUp()
        
        # Change the scanner's path
        self.scanner.path = self.temp_scan_dir.folder
        self.scanner.save()

        corrupt_tag = Tag.create_or_get('corrupt')
        corrupt_tag.save()

        # Make sure that the scanner would add any image
        self.scanner.auto_failure_tags.add(corrupt_tag)
        self.scanner.save()

        # Run the scan
        posts = self.scanner.scan()

        # Make sure that there are no posts
        self.assertEqual(len(posts), 0, 'The corrupt file was not skipped')

        # Get the status
        status = self.scanner.status

        # Make sure that the status includes '1 error'
        self.assertIn('1 error', status)
    
    def test_scan_active_scanner(self):
        """Rejects when scanner is scanning"""

        # Mark the scanner as active
        self.scanner.is_active = True
        self.scanner.save()

        # Run the scan and expect an error
        with self.assertRaises(ScannerError):
            self.scanner.scan()
        
        # Set the scanner as inactive
        self.scanner.is_active = False
        self.scanner.save()

        # Run the scan and expect no error
        self.scanner.scan()

        # Make sure that after it has finished, the scanner is inactive
        self.assertFalse(self.scanner.is_active)

class PostDeleteHookTest(TestCase):
    temp_storage = booru_testutils.TempStorage()

    def setUp(self):
        self.temp_storage.setUp()

        # Create a post
        self.post = Post.create_from_file(booru_testutils.FELIX_PATH)
        self.post.save()

        # Get the md5
        self.md5 = self.post.md5
    
    def tearDown(self):
        self.temp_storage.tearDown()
    
    def test_adds_ignore(self):
        """Creates ignore case when post is deleted"""

        # Make sure there are no ignore cases
        self.assertEqual(ScannerIgnore.objects.count(), 0)

        # Delete the post
        self.post.delete()

        # Make sure that there is one ignore case
        self.assertEqual(ScannerIgnore.objects.count(), 1)

        # Get the ignore case
        ignore = ScannerIgnore.objects.first()

        # Make sure that the ignore case has the correct md5
        self.assertEqual(ignore.md5, self.md5)

        # Make sure the reason includes the word 'deleted'
        self.assertIn('deleted', ignore.reason)
    
    def test_does_not_add_ignore(self):
        """Does not override an already placed ignore"""

        # Create the ignore case
        ignore = ScannerIgnore(md5=self.md5, reason='Test')
        ignore.save()

        # Make sure that there is one ignore case
        self.assertEqual(ScannerIgnore.objects.count(), 1)

        # Delete the post
        self.post.delete()

        # Make sure that there is still only one ignore case
        self.assertEqual(ScannerIgnore.objects.count(), 1)

        # Get the ignore case
        ignore = ScannerIgnore.objects.first()

        # Make sure that the ignore case has the correct md5
        self.assertEqual(ignore.md5, self.md5)

        # Make sure that the reason is still 'Test'
        self.assertEqual(ignore.reason, 'Test')