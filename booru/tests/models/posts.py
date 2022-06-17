from django.test import TestCase

from ...models.posts import Post, Tag

import hashlib
import os
import pathlib
import shutil

import booru.tests.testutils as testutils
import booru.boorutils as boorutils

import homebooru.settings

class PostTest(TestCase):
    def test_inc_total(self):
        """Increments the total posts counter"""

        before_total_posts = Post.objects.count()

        p = Post(width=420, height=420, folder=0, md5='ca6ffc3babb6f0f58a7e5c0c6b61e7bf')

        # Save it
        p.save()

        # Check that the total
        self.assertEqual(Post.objects.count(), before_total_posts + 1)
    
    def test_tag_array(self):
        """Adds tags to a post correctly"""

        p = Post(width=420, height=420, folder=0, md5='ca6ffc3babb6f0f58a7e5c0c6b61e7bf')
        p.save()

        # Make sure that the tags array is empty
        self.assertEqual(list(p.tags.all()), [])

        first_tag = Tag(tag='tag1')
        first_tag.save()

        second_tag = Tag(tag='tag2')
        second_tag.save()

        # Add a tag
        p.tags.add(first_tag)
        p.tags.add(second_tag)

        # Save it
        p.save()

        # Get the post
        p = Post.objects.get(md5='ca6ffc3babb6f0f58a7e5c0c6b61e7bf')

        # Make sure that the tags array is empty
        self.assertEqual(list(p.tags.all()), [first_tag, second_tag])
    
    def test_md5_unique(self):
        """Verifies that the md5 is unique"""

        p = Post(width=420, height=420, folder=0, md5='ca6ffc3babb6f0f58a7e5c0c6b61e7bf')
        p.save()

        # Get the post
        p = Post.objects.get(md5='ca6ffc3babb6f0f58a7e5c0c6b61e7bf')

        # Try to save it again
        with self.assertRaises(Exception):
            b = Post(width=420, height=420, folder=1, md5='ca6ffc3babb6f0f58a7e5c0c6b61e7bf')
            b.save()

    # Before each, clear the posts table
    def setUp(self):
        Post.objects.all().delete()

class PostCreateFromFileTest(TestCase):
    test_image_path = 'assets/TEST_DATA/content/felix.jpg'
    test_sampleable_path = 'assets/TEST_DATA/content/sampleable_image.jpg'
    test_video_path = 'assets/TEST_DATA/content/ana_cat.mp4'
    test_png_path = 'assets/TEST_DATA/content/gato.png'
    test_text_path = 'assets/TEST_DATA/content/test.txt'
    test_corrupt_path = 'assets/TEST_DATA/content/corrupt_image.jpg'

    temp_storage = testutils.TempStorage()

    def setUp(self):
        self.temp_storage.setUp()
    
    def tearDown(self):
        self.temp_storage.tearDown()
    
    def test_create_post(self):
        """Creates a post from a file"""

        # Create a post from a file
        p = Post.create_from_file(self.test_image_path)
        p.save()

        # Check that the post was created
        self.assertEqual(Post.objects.count(), 1)

        # Check that the post was created with the correct attributes
        self.assertEqual(p.width,  500)
        self.assertEqual(p.height, 688)

        # Check that the post was created with the correct md5
        self.assertEqual(p.md5, '2dcd09f6c874b36355336112d17434e1')

        # Check that the post was created with the correct folder
        self.assertEqual(p.folder, 1)

        # Make sure that the sample flag is false
        self.assertEqual(p.sample, 0)

        # Make sure that filename is correct
        self.assertEqual(p.filename, '2dcd09f6c874b36355336112d17434e1.jpg')
    
        # Make sure that it isn't marked as a video
        self.assertEqual(p.is_video, 0)

    def test_files_exists(self):
        """Creates files correctly"""

        # Create a post from a file
        p = Post.create_from_file(self.test_image_path)
        p.save()

        # Check that the media file exists
        self.assertTrue(os.path.exists(os.path.join(self.temp_storage.temp_storage_path, 'media', '1', '2dcd09f6c874b36355336112d17434e1.jpg')))

        # Check that the thumbnail file exists
        self.assertTrue(os.path.exists(os.path.join(self.temp_storage.temp_storage_path, 'thumbnails', '1', 'thumbnail_2dcd09f6c874b36355336112d17434e1.jpg')))

        # Make sure that the sample file is not created
        self.assertFalse(os.path.exists(os.path.join(self.temp_storage.temp_storage_path, 'samples', '1', 'sample_2dcd09f6c874b36355336112d17434e1.jpg')))

    def test_thumbnail_smaller(self):
        """Creates smaller thumbnail"""

        # Create a post from a file
        p = Post.create_from_file(self.test_image_path)
        p.save()

        # Check that the thumbnail file exists
        self.assertTrue(os.path.exists(os.path.join(self.temp_storage.temp_storage_path, 'thumbnails', '1', 'thumbnail_2dcd09f6c874b36355336112d17434e1.jpg')))

        # Check that the thumbnail file is smaller than the image file
        self.assertLess(os.path.getsize(os.path.join(self.temp_storage.temp_storage_path, 'thumbnails', '1', 'thumbnail_2dcd09f6c874b36355336112d17434e1.jpg')), os.path.getsize(os.path.join(self.temp_storage.temp_storage_path, 'media', '1', '2dcd09f6c874b36355336112d17434e1.jpg')))

    def test_create_sample(self):
        """Creates a sample from a file"""

        # Create a post from a file
        p = Post.create_from_file(self.test_sampleable_path)
        p.save()

        # Check that the sample file exists
        self.assertTrue(os.path.exists(os.path.join(self.temp_storage.temp_storage_path, 'samples', '1', 'sample_656bc10f9f3a6a8f7e017892c8aabcb8.jpg')))

        # Check that the sample flag is true
        self.assertEqual(p.sample, 1)
    
    def test_create_video(self):
        """Creates a video from a file"""

        # Create a post from a file
        p = Post.create_from_file(self.test_video_path)
        p.save()

        # Check that the video flag is true
        self.assertEqual(p.is_video, 1)

        # Check that the video file exists
        self.assertTrue(os.path.exists(os.path.join(self.temp_storage.temp_storage_path, 'media', '1', '11e0a9c6b20d54593b8fc8f134a25256.mp4')))

        # Check that the thumbnail file exists
        self.assertTrue(os.path.exists(os.path.join(self.temp_storage.temp_storage_path, 'thumbnails', '1', 'thumbnail_11e0a9c6b20d54593b8fc8f134a25256.jpg')))

        # Make sure sampled is false (this video is technically sampleable but we don't want to sample videos)
        self.assertEqual(p.sample, 0)

    def test_rejects_corrupt_files(self):
        """Rejects corrupt files"""

        # Create a post from a file

        # Make sure that it throws
        with self.assertRaises(Exception):
            Post.create_from_file(self.test_corrupt_path)

        # Check that the post was not created
        self.assertEqual(Post.objects.count(), 0)

        # List the directories in the storage path
        dirs = os.listdir(os.path.join(self.temp_storage.temp_storage_path))

        # Make sure that the directories are empty
        self.assertEqual(len(dirs), 0)

    def test_jpg_thumbnails(self):
        """Creates a thumbnail from a jpg file"""
        # Create a post from a file
        p = Post.create_from_file(self.test_image_path)
        p.save()

        # Check that the thumbnail file exists (and is a jpg)
        self.assertTrue(os.path.exists(os.path.join(self.temp_storage.temp_storage_path, 'thumbnails', '1', 'thumbnail_2dcd09f6c874b36355336112d17434e1.jpg')))
    
    def test_jpg_samples(self):
        """Creates samples as JPG files"""

        # Create a post from a file
        p = Post.create_from_file(self.test_sampleable_path)
        p.save()

        # Check that the sample file exists (and is a jpg)
        self.assertTrue(os.path.exists(os.path.join(self.temp_storage.temp_storage_path, 'samples', '1', 'sample_656bc10f9f3a6a8f7e017892c8aabcb8.jpg')))

    def test_raises_against_directories(self):
        """Raises an error when trying to create a post from a directory"""

        # Create a post from a file
        with self.assertRaises(Exception):
            Post.create_from_file(self.test_directory_path)

        # Check that the post was not created
        self.assertEqual(Post.objects.count(), 0)

    def test_raises_against_non_images(self):
        """Raises an error when trying to create a post from a non-image file"""

        # Create a post from a file
        with self.assertRaises(Exception):
            Post.create_from_file(self.test_text_path)

        # Check that the post was not created
        self.assertEqual(Post.objects.count(), 0)

    # We should be testing for web accessibility but the way it works in production should be slightly different to the way it works in testing

class PostSearchTest(TestCase):
    p1 = None
    p2 = None
    tag1 = None
    tag2 = None
    tag3 = None
    tag4 = None

    def setUp(self):
        Post.objects.all().delete()
        Tag.objects.all().delete()

        # Create two posts with different tags
        self.p1 = Post(width=420, height=420, folder=0, md5='ca6ffc3babb6f0f58a7e5c0c6b61e7bf')
        self.p1.save()

        self.p2 = Post(width=420, height=420, folder=0, md5='ca6ffc3b4bb6f0f58a7e5c0c6b61e7bf')
        self.p2.save()

        self.tag1 = Tag(tag='tag1')
        self.tag1.save()

        self.tag2 = Tag(tag='tag2')
        self.tag2.save()

        self.tag3 = Tag(tag='tag3')
        self.tag3.save()

        self.tag4 = Tag(tag='tag4')
        self.tag4.save()

        # Add to the first post
        self.p1.tags.add(self.tag1)
        self.p1.tags.add(self.tag2)
        self.p1.save()

        # Add to the second post
        self.p2.tags.add(self.tag3)
        self.p2.tags.add(self.tag4)
        self.p2.tags.add(self.tag1)

        self.p2.save()
    
    def test_one_result(self):
        # Search for all posts with tag1
        tag2_only = Post.search('tag2')
        self.assertEqual(len(tag2_only), 1)
        self.assertEqual(tag2_only[0], self.p1)
    
    def test_multiple_results(self):
        # Search for all posts with tag1
        tag1_only = Post.search('tag1')
        self.assertEqual(len(tag1_only), 2)
        self.assertEqual(tag1_only[0], self.p1)
        self.assertEqual(tag1_only[1], self.p2)
    
    def test_no_results_missing_tag(self):
        # Search for all posts with tag1
        nothing = Post.search('tag5')
        self.assertEqual(len(nothing), 0)
    
    def test_all_results(self):
        # Search for all posts with tag1
        alls = Post.search('')
        self.assertEqual(len(alls), 2)
        self.assertEqual(alls[0], self.p1)
        self.assertEqual(alls[1], self.p2)
    
    def test_wildcard(self):
        # Search for all posts with tag1
        wildcard = Post.search('*a*')

        self.assertEqual(wildcard.count(), 2)
        self.assertEqual(wildcard[0], self.p1)
        self.assertEqual(wildcard[1], self.p2)

        wildcard = Post.search('*2')
        self.assertEqual(wildcard.count(), 1)
        self.assertEqual(wildcard[0], self.p1)
    
    def test_exclude_wildcard(self):
        wildcard = Post.search('-*a*')

        self.assertEqual(wildcard.count(), 0)

        # Create a bloke tag
        bloke_tag = Tag(tag='bloke')
        bloke_tag.save()

        # Add the bloke tag to a new post
        new_post = Post(width=420, height=420, folder=0, md5='ca6ffc3b4bb643458a7e5c0c6b61e7bf')
        new_post.save()

        new_post.tags.add(bloke_tag)

        # Redo the search
        wildcard = Post.search('-*a*')
        
        self.assertEqual(wildcard.count(), 1)
        self.assertEqual(wildcard[0], new_post)
    
    def test_escape_regex_characters(self):
        # This should only occur with wildcards
        wildcard = Post.search('tag\\*')

        # There should be no results
        self.assertEqual(wildcard.count(), 0)

        # Add a tag that contains slashes
        tag_with_slashes = Tag(tag='tag\\5')
        tag_with_slashes.save()

        # Add the tag to the first post
        self.p1.tags.add(tag_with_slashes)

        # Redo the search
        wildcard = Post.search('tag\\*')

        # There should be one result
        self.assertEqual(wildcard.count(), 1)

        # The result should be the first post
        self.assertEqual(wildcard[0], self.p1)
    
    def test_escape_regex_dot(self):
        # This should only occur with wildcards
        wildcard = Post.search('=.=*')

        # There should be no results
        self.assertEqual(wildcard.count(), 0)

        # Add a tag that contains slashes
        t = Tag(tag='=.=')
        t.save()

        # Add the tag to the first post
        self.p1.tags.add(t)

        phrases = [
            '=.*', '*.=', '*.*', '=.='
        ]

        for phrase in phrases:
            # Redo the search
            wildcard = Post.search(phrase)
            # There should be one result
            self.assertEqual(wildcard.count(), 1)
            # The result should be the first post
            self.assertEqual(wildcard[0], self.p1)
    
    def test_escape_regex_non_english(self):
        non_english = Tag(tag="金玉")
        non_english.save()

        # Add the tag to the first post
        self.p1.tags.add(non_english)
        self.p1.save()

        # Search for the tag
        non_english_search = Post.search("金*")
        
        # There should be one result
        self.assertEqual(non_english_search.count(), 1)
        
        # The result should be the first post
        self.assertEqual(non_english_search[0], self.p1)
    
    def test_get_search_tags(self):
        results = Post.search('')

        tags = Post.get_search_tags(results)

        self.assertEqual(len(tags), 4)

        # Get the list of tag names
        tag_names = [tag.tag for tag in tags]

        # Make sure they're in the correct order
        self.assertEqual(tag_names, ['tag1', 'tag2', 'tag3', 'tag4'])

        # Make sure that their order changes
        
        self.p1.tags.add(self.tag4)
        self.p1.save()

        tags = Post.get_search_tags(results)
        tag_names = [tag.tag for tag in tags]

        self.assertEqual(tag_names[:-2], ['tag1', 'tag4'])
    
    def test_get_search_tags_limits_to_depth(self):
        results = Post.search('')

        tags = Post.get_search_tags(results, depth=1) # Only return the first image's tags

        self.assertEqual(len(tags), 2)

        # Get the list of tag names
        tag_names = [tag.tag for tag in tags]

        # Make sure they're in the correct order
        self.assertEqual(tag_names, ['tag1', 'tag2'])
    
    def test_get_next_folder(self):
        # Current total posts = 2
        # Current folder = 1

        self.assertEqual(Post.get_next_folder(), 1)

        # Create a more posts
        new_posts = 500

        for i in range(new_posts):
            md5 = boorutils.hash_str(str(i))

            post = Post(width=420, height=420, folder=Post.get_next_folder(), md5=md5)
            post.save()

        # Current total posts = 2 + 500
        
        # Current folder should be ceil(502 / 256) = 2
        self.assertEqual(Post.get_next_folder(), 2)
    
    def test_get_next_folder_variable_size(self):
        # Create a more posts
        new_posts = 500

        for i in range(new_posts):
            md5 = boorutils.hash_str(str(i))

            post = Post(width=420, height=420, folder=Post.get_next_folder(), md5=md5)
            post.save()

        # Current total posts = 2 + 500
        
        # Current folder should be ceil(502 / 50) = 11
        self.assertEqual(Post.get_next_folder(50), 11)
    
    def test_md5_ignore_case(self):
        md5 = boorutils.hash_str('test')

        # Make the md5 uppercase
        md5 = md5.upper()

        post = Post(width=420, height=420, folder=1, md5=md5)
        post.save()

        # Make sure that the md5 is lowercase
        self.assertEqual(post.md5, md5.lower())
    
    def test_rejects_invalid_md5(self):
        md5 = 'invalid'

        post = Post(width=420, height=420, folder=1, md5=md5)
        with self.assertRaises(ValueError):
            post.save()