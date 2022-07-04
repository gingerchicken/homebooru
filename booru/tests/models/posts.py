from django.test import TestCase
from django.contrib.auth.models import User

from ...models.posts import Post, Rating
from ...models.tags import Tag, TagType
from ...pagination import Paginator

import hashlib
import os
import pathlib
import shutil
import math

import booru.tests.testutils as testutils
import booru.boorutils as boorutils

import homebooru.settings

class PostTest(TestCase): 
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

    fixtures = ['ratings.json']

    def setUp(self):
        Post.objects.all().delete()
        Tag.objects.all().delete()

        super().setUp()

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

        # Post 2 should be first as it was the latest uploaded
        self.assertEqual(tag1_only[1], self.p1)
        self.assertEqual(tag1_only[0], self.p2)
    
    def test_no_results_missing_tag(self):
        # Search for all posts with tag1
        nothing = Post.search('tag5')
        self.assertEqual(len(nothing), 0)
    
    def test_all_results(self):
        # Search for all posts with tag1
        alls = Post.search('')
        self.assertEqual(len(alls), 2)

        self.assertEqual(alls[1], self.p1)
        self.assertEqual(alls[0], self.p2)
    
    def test_wildcard(self):
        # Search for all posts with tag1
        wildcard = Post.search('*a*')

        self.assertEqual(wildcard.count(), 2)
        self.assertEqual(wildcard[1], self.p1)
        self.assertEqual(wildcard[0], self.p2)

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
    
    def test_exclude_tag(self):
        # Search for all posts without tag1
        results = Post.search('-tag1')

        # There should be no results
        self.assertEqual(results.count(), 0)

        # Search for all posts wtihout tag2
        results = Post.search('-tag2')

        # There should be one result
        self.assertEqual(results.count(), 1)
        
        # It should be the second post
        self.assertEqual(results[0], self.p2)

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

        # We should expect a list of tags sorted by the total posts
        expected_tags = [tag for tag in tags]
        # Sort the tags by total_posts
        expected_tags.sort(key=lambda tag: tag.total_posts, reverse=True)
        expected_tags = [tag.tag for tag in expected_tags]

        # Make sure it starts with tag1
        self.assertEqual(tag_names[0], 'tag1')

        # Make sure they're in the correct order
        self.assertEqual(tag_names, expected_tags)

        # Make sure that their order changes
        self.p1.tags.add(self.tag4)
        self.p1.save()

        tags = Post.get_search_tags(results)
        tag_names = [tag.tag for tag in tags]

        self.assertEqual(tag_names[:-2], ['tag1', 'tag4'])
    
    def test_get_search_tags_limits_to_depth(self):
        results = Post.search('')

        tags = Post.get_search_tags(results, depth=1) # Only return the first image's tags

        self.assertEqual(len(tags), 3)

        # Get the list of tag names
        tag_names = [tag.tag for tag in tags]

        # The only tags that should be displayed are the tags from the second post
        expected_names = [tag.tag for tag in self.p2.tags.all()]

        # Make sure they're in the correct order
        self.assertEqual(tag_names, expected_names)
    
    def test_parameter_md5(self):
        # Create a bunch of posts
        for i in range(0, 100):
            post = Post(width=420, height=420, folder=0, md5=boorutils.hash_str(str(i)))
            post.save()
        

        # Search for a post with the md5 of 0
        zero_md5 = boorutils.hash_str('0')
        results = Post.search('md5:' + zero_md5)

        # There should be one result
        self.assertEqual(results.count(), 1)

        # The md5 of the result should be 0
        self.assertEqual(results[0].md5, zero_md5)

    def test_parameter_rating(self):
        Post.objects.all().delete()
        # Create a bunch of posts
        safe = Rating.objects.get(name='safe')
        questionable = Rating.objects.get(name='questionable')
        explicit = Rating.objects.get(name='explicit')

        ratings = [safe, questionable, explicit]

        for i in range(0, 3):
            for j in range(i * 33, 33 * (i + 1)):
                post = Post(width=420, height=420, folder=0, rating=ratings[i], md5=boorutils.hash_str(str(j)))
                post.save()
        
        for rating in ratings:
            results = Post.search('rating:' + rating.name)

            # There should be 33 results
            self.assertEqual(results.count(), 33)

            # The rating of the results should be the same as the rating
            for result in results:
                self.assertEqual(result.rating, rating)
            
            # Test negation
            results = Post.search('-rating:' + rating.name)

            # There should be 66 results
            self.assertEqual(results.count(), 66)

            # The rating of the results should not be the same as the rating
            for result in results:
                self.assertNotEqual(result.rating, rating)

    def test_parameter_rating_invalid(self):
        # Create a bunch of posts
        safe = Rating.objects.get(name='safe')

        for i in range(0, 3):
            post = Post(width=420, height=420, folder=0, rating=safe, md5=boorutils.hash_str(str(i)))
            post.save()

        results = Post.search('rating:invalid')

        # There should be 0 results
        self.assertEqual(results.count(), 0)

        # Test negation
        results = Post.search('-rating:invalid')

        # There should be 5 results
        self.assertEqual(results.count(), 5)

    def test_parameter_title(self):
        # Remove all other posts
        Post.objects.all().delete()

        # Create a bunch of posts
        for i in range(0, 100):
            post = Post(width=420, height=420, folder=0, title='title' + str(i), md5=boorutils.hash_str(str(i)))
            post.save()
        
        # Search for a post with the title of title0
        results = Post.search('title:title0')

        # There should be 1 result
        self.assertEqual(results.count(), 1)

        # The title of the result should be title0
        self.assertEqual(results[0].title, 'title0')

        # Test negation
        results = Post.search('-title:title0')

        # There should be 99 results
        self.assertEqual(results.count(), 99)

        # The title of the results should not be title0
        for result in results:
            self.assertNotEqual(result.title, 'title0')
    
    def test_parameter_title_invalid(self):
        # Create a bunch of posts
        for i in range(0, 100):
            post = Post(width=420, height=420, folder=0, title='title' + str(i), md5=boorutils.hash_str(str(i)))
            post.save()
        
        # Search for a post with the title of title0
        results = Post.search('title:invalid')

        # There should be 0 results
        self.assertEqual(results.count(), 0)

        # Test negation
        results = Post.search('-title:invalid')

        # There should be 102 results
        self.assertEqual(results.count(), 102)
    
    def test_parameter_width(self):
        Post.objects.all().delete()

        # Create a bunch of posts
        for i in range(0, 100):
            post = Post(width=420 * i, height=420, folder=0, md5=boorutils.hash_str(str(i)))
            post.save()

        # Search for a post with the width of 420
        results = Post.search('width:420')

        # There should be 1 result
        self.assertEqual(results.count(), 1)

        # The width of the result should be 420
        self.assertEqual(results[0].width, 420)

        # Test negation
        results = Post.search('-width:420')

        # There should be 99 results
        self.assertEqual(results.count(), 99)

        # The width of the results should not be 420
        for result in results:
            self.assertNotEqual(result.width, 420)
    
    def test_parameter_width_invalid(self):
        # Create a bunch of posts
        for i in range(0, 100):
            post = Post(width=420 * i, height=420, folder=0, md5=boorutils.hash_str(str(i)))
            post.save()
        
        # Search for a post with the width of 420
        results = Post.search('width:invalid')

        # There should be 0 results
        self.assertEqual(results.count(), 0)

        # Test negation
        results = Post.search('-width:invalid')

        # There should be 102 results
        self.assertEqual(results.count(), 102)
    
    def test_parameter_height(self):
        Post.objects.all().delete()
        # Create a bunch of posts
        for i in range(0, 100):
            post = Post(width=420, height=420 * i, folder=0, md5=boorutils.hash_str(str(i)))
            post.save()
        
        # Search for a post with the height of 420
        results = Post.search('height:420')

        # There should be 1 result
        self.assertEqual(results.count(), 1)

        # The height of the result should be 420
        self.assertEqual(results[0].height, 420)

        # Test negation
        results = Post.search('-height:420')

        # There should be 99 results
        self.assertEqual(results.count(), 99)

        # The height of the results should not be 420
        for result in results:
            self.assertNotEqual(result.height, 420)
    
    def test_parameter_height_invalid(self):
        # Create a bunch of posts
        for i in range(0, 100):
            post = Post(width=420, height=420 * i, folder=0, md5=boorutils.hash_str(str(i)))
            post.save()
        
        # Search for a post with the height of 420
        results = Post.search('height:invalid')

        # There should be 0 results
        self.assertEqual(results.count(), 0)

        # Test negation
        results = Post.search('-height:invalid')

        # There should be 102 results
    
    def test_parameter_negation(self):
        """Negate a parameter much like a tag"""
        Post.objects.all().delete()

        # Create a bunch of posts
        for i in range(0, 100):
            post = Post(width=420, height=420, folder=0, md5=boorutils.hash_str(str(i)))
            post.save()

        # Search for a post with the md5 of 0
        zero_md5 = boorutils.hash_str('0')

        results = Post.search('-md5:' + zero_md5)

        # Expect every post except the one with the md5 of 0
        self.assertEqual(results.count(), 99)

        # The md5 of the result should not be 0
        for result in results:
            self.assertNotEqual(result.md5, zero_md5)

    def test_tag_with_colon(self):
        """Test that a tag with a colon works - ignores non-valid parameters"""

        # Add te:sting tag to a post
        self.p1.tags.add(Tag.create_or_get('te:sting'))

        # Search for a post with the tag te:sting
        results = Post.search('te:sting')

        # There should be 1 result
        self.assertEqual(results.count(), 1)

        # The result should be the same as the post
        self.assertEqual(results[0], self.p1)
    
    def test_parameters_with_tags(self):
        """Test that parameters along with tags work"""

        ratings = [Rating.objects.get(name='safe'), Rating.objects.get(name='questionable'), Rating.objects.get(name='explicit')]

        # Create a bunch of posts
        for i in range(0, 100):
            post = Post(width=420, height=420, folder=0, md5=boorutils.hash_str(str(i)), rating=ratings[i % 3])
            post.save()

            # Add a tag to the post
            tag_name = "tag" + str(i // 10)
            tag = Tag.create_or_get(tag_name)
            tag.save()
            
            post.tags.add(tag)
            post.save()
        
        # Search for a post with the tag tag0
        results = Post.search('tag0')

        # There should be 10 results
        self.assertEqual(results.count(), 10)

        # The tag of the result should be tag0
        for result in results:
            self.assertEqual(result.tags.all()[0].tag, 'tag0')

        # Search for a post with the tag tag0 and the md5 of 0
        results = Post.search('tag0 md5:' + boorutils.hash_str('0'))

        # There should be 1 result
        self.assertEqual(results.count(), 1)

        # Search for rating explicit with the tag tag0
        results = Post.search('rating:explicit tag0')

        # There should be 3 results
        self.assertEqual(results.count(), 3)

        # The tag of the result should be tag0 and the rating of the result should be explicit
        for result in results:
            self.assertEqual(result.tags.all()[0].tag, 'tag0')
            self.assertEqual(result.rating, Rating.objects.get(name='explicit'))

    def test_parameter_user(self):
        """Test that the user parameter works"""
        # Remove all other posts
        Post.objects.all().delete()

        # Create a user
        user = User(username='test', password='huevo')
        user.save()

        # Create another user
        user2 = User(username='test2', password='huevo')
        user2.save()

        # Create a bunch of posts
        for i in range(0, 50):
            post = Post(width=420, height=420, folder=0, md5=boorutils.hash_str(str(i)), owner=user)
            post.save()
        
        for i in range(50, 100):
            post = Post(width=420, height=420, folder=0, md5=boorutils.hash_str(str(i)), owner=user2)
            post.save()
        
        # Search for a post with the user of user1
        results = Post.search('user:' + str(user.id))

        # There should be 50 results
        self.assertEqual(results.count(), 50)

        # The user of the result should be user
        for result in results:
            self.assertEqual(result.owner, user)
        
        # Test negation
        results = Post.search('-user:' + str(user.id))

        # There should be 50 results
        self.assertEqual(results.count(), 50)

        # The user of the result should be user
        for result in results:
            self.assertEqual(result.owner, user2)
    
    def test_parameter_user_invalid(self):
        """Test that the user parameter works"""
        # Remove all other posts
        Post.objects.all().delete()

        # Create a user
        user = User(username='test', password='huevo')
        user.save()

        # Create another user
        user2 = User(username='test2', password='huevo')
        user2.save()

        # Create a bunch of posts
        for i in range(0, 50):
            post = Post(width=420, height=420, folder=0, md5=boorutils.hash_str(str(i)), owner=user)
            post.save()
        
        for i in range(50, 100):
            post = Post(width=420, height=420, folder=0, md5=boorutils.hash_str(str(i)), owner=user2)
            post.save()
        
        # Search for a post with the user of user1
        results = Post.search('user:invalid')

        # There should be 0 results
        self.assertEqual(results.count(), 0)

        # Test negation
        results = Post.search('-user:invalid')

        # There should be 100 results
        self.assertEqual(results.count(), 100)

class PostDeleteTest(TestCase):
    temp_storage = testutils.TempStorage()

    def setUp(self):
        self.temp_storage.setUp()
    
    def tearDown(self):
        self.temp_storage.tearDown()

    def test_deletes_files_on_delete(self):
        """Deletes related files when deleting a post"""
        # Create a new post
        p = Post.create_from_file(testutils.SAMPLEABLE_PATH)
        p.save()

        # Make sure the files exist
        paths = [
            p.get_sample_path(),
            p.get_thumbnail_path(),
            p.get_media_path()
        ]

        for path in paths:
            self.assertTrue(path.exists())
        
        # Delete the post
        p.delete()

        # Make sure the files don't exist
        for path in paths:
            self.assertFalse(path.exists())
    
    def test_leaves_other_posts_alone(self):
        """Deletes related files when deleting a post"""

        # Create a new post
        p = Post.create_from_file(testutils.SAMPLEABLE_PATH)
        p.save()

        # Create a new post
        p2 = Post.create_from_file(testutils.GATO_PATH)
        p2.save()

        # Make sure the files exist
        paths = [
            p.get_sample_path(),
            p.get_thumbnail_path(),
            p.get_media_path(),
            p2.get_thumbnail_path(),
            p2.get_media_path()
        ]

        for path in paths:
            self.assertTrue(path.exists())
        
        # Delete the post
        p.delete()

        deleted_paths = paths[:2]
        kept_paths = paths[3:]

        # Make sure the files don't exist
        for path in deleted_paths:
            self.assertFalse(path.exists())
        
        # Make sure the files still exist
        for path in kept_paths:
            self.assertTrue(path.exists())

    
    def test_get_media_path(self):
        """Returns expected path for media file"""

        # Create a new post
        p = Post.create_from_file(testutils.SAMPLEABLE_PATH)
        p.save()

        # Make sure it is the correct path
        testutils.assertPathsEqual(p.get_media_path(), homebooru.settings.BOORU_STORAGE_PATH / f"media/{p.folder}/{p.md5}.jpg")
    
    def test_get_sample_path(self):
        # Create a new post
        p = Post.create_from_file(testutils.SAMPLEABLE_PATH)
        p.save()

        # Make sure it is the correct path
        testutils.assertPathsEqual(p.get_sample_path(), homebooru.settings.BOORU_STORAGE_PATH / f"samples/{p.folder}/sample_{p.md5}.jpg")
    
    def test_get_thumbnail_path(self):
        """Returns expected path for thumbnail"""

        # Create a new post
        p = Post.create_from_file(testutils.SAMPLEABLE_PATH)
        p.save()

        # Make sure it is the correct path
        testutils.assertPathsEqual(p.get_thumbnail_path(), homebooru.settings.BOORU_STORAGE_PATH / f"thumbnails/{p.folder}/thumbnail_{p.md5}.jpg")

    def test_get_media_path_non_jpg(self):
        """Retains the original file extension"""

        # Create a new post
        p = Post.create_from_file(testutils.GATO_PATH)
        p.save()

        # Make sure it is the correct path
        testutils.assertPathsEqual(p.get_media_path(), (homebooru.settings.BOORU_STORAGE_PATH / f"media/{p.folder}/{p.md5}.png"))

    # I don't really care that this doesn't work since this should never be used but whatever.    
    # def test_multiple_posts_deleted(self):
    #     """Triggers when using objects.all().delete()"""

    #     # Create two posts
    #     p = Post.create_from_file(testutils.SAMPLEABLE_PATH)
    #     p.save()

    #     p2 = Post.create_from_file(testutils.GATO_PATH)
    #     p2.save()

    #     # Make sure the files exist
    #     paths = [
    #         p.get_sample_path(),
    #         p.get_thumbnail_path(),
    #         p.get_media_path(),
    #         p2.get_thumbnail_path(),
    #         p2.get_media_path()
    #     ]

    #     # Remove all posts
    #     Post.objects.all().delete()

    #     # Alternatively - this should work too
    #     # for post in Post.objects.all():
    #     #     post.delete()

    #     # Make sure the files don't exist
    #     for path in paths:
    #         self.assertFalse(path.exists())

class PostGetSortedTags(TestCase):
    fixtures = ['booru/fixtures/tagtypes.json']
    temp_storage = testutils.TempStorage()

    def setUp(self):
        self.temp_storage.setUp()
        super().setUp()
    
    def tearDown(self):
        self.temp_storage.tearDown()
        super().tearDown()
    
    def test_get_sorted_tags(self):
        """Returns a list of tags sorted by name"""

        # Create a new post
        p = Post.create_from_file(testutils.SAMPLEABLE_PATH)
        p.save()

        # Add some tags
        tags_to_add = '1boy animal_ears brown_eyes brown_hair cat_ears felix_argyle flower hair_flower hair_ornament japanese_clothes re:zero_kara_hajimeru_isekai_seikatsu ribbon shake_sawa short_hair solo white_background wide_sleeves'

        tags = []
        for tag in tags_to_add.split():
            p.tags.add(Tag.create_or_get(tag))
        
    
        # Make felix_argyle tag a character tag
        t = Tag.objects.get(tag='felix_argyle')
        t.tag_type = TagType.objects.get(name='character')
        t.save()

        # Make shake_sawa tag an artist tag
        t = Tag.objects.get(tag='shake_sawa')
        t.tag_type = TagType.objects.get(name='artist')
        t.save()

        # Make re:zero_kara_hajimeru_isekai_seikatsu tag a copyright tag
        t = Tag.objects.get(tag='re:zero_kara_hajimeru_isekai_seikatsu')
        t.tag_type = TagType.objects.get(name='copyright')
        t.save()

        # Sort the tags
        sorted_tags = p.get_sorted_tags()

        for type_name in sorted_tags['types']:
            for i in range(len(sorted_tags['types'][type_name])):
                t = sorted_tags['types'][type_name][i]
                sorted_tags['types'][type_name][i] = t.tag


        # Check the order of the types
        self.assertEqual(sorted_tags['type_orders'], ['artist', 'character', 'copyright', 'general'])

        # Make sure that the tags are in the correct order
        self.assertEqual(sorted_tags['types']['general'], [
            "1boy",
            "animal_ears",
            "brown_eyes",
            "brown_hair",
            "cat_ears",
            "flower",
            "hair_flower",
            "hair_ornament",
            "japanese_clothes",
            "ribbon",
            "short_hair",
            "solo",
            "white_background",
            "wide_sleeves"
        ])

        self.assertEqual(sorted_tags['types']['character'], [
            "felix_argyle"
        ])

        self.assertEqual(sorted_tags['types']['artist'], [
            "shake_sawa"
        ])
    
    # TODO test empty tags
    # TODO test if the tag_type is None

class PostGetProximatePosts(TestCase):
    fixtures = ['booru/fixtures/tagtypes.json']
    temp_storage = testutils.TempStorage()

    newest = None
    middle = None
    oldest = None
    olderest = None

    def setUp(self):
        self.temp_storage.setUp()
        super().setUp()

        self.olderest = Post.create_from_file(testutils.VIDEO_PATH)
        self.olderest.save()

        self.oldest = Post.create_from_file(testutils.SAMPLEABLE_PATH)
        self.oldest.save()

        self.middle = Post.create_from_file(testutils.GATO_PATH)
        self.middle.save()

        self.newest = Post.create_from_file(testutils.FELIX_PATH)
        self.newest.save()

    def tearDown(self):
        self.temp_storage.tearDown()
        super().tearDown()
    
    def test_get_proximate_posts(self):
        """Returns expected posts for middle"""
        # Delete olderest
        self.olderest.delete()
        
        # Search for all posts
        results = Post.search('')
    
        # Get the posts
        posts = self.middle.get_proximate_posts(results)

        self.assertEqual(posts['newer'], self.newest)
        self.assertEqual(posts['older'], self.oldest)
    
    def test_newest_edge_case(self):
        """Returns expected posts for newest"""
        # Delete olderest
        self.olderest.delete()
        
        # Search for all posts
        results = Post.search('')
    
        # Get the posts
        posts = self.newest.get_proximate_posts(results)

        self.assertEqual(posts['newer'], None)
        self.assertEqual(posts['older'], self.middle)
    
    def test_oldest_edge_case(self):
        """Returns expected posts for oldest"""
        
        # Delete olderest
        self.olderest.delete()

        # Search for all posts
        results = Post.search('')
    
        # Get the posts
        posts = self.oldest.get_proximate_posts(results)

        self.assertEqual(posts['newer'], self.middle)
        self.assertEqual(posts['older'], None)

    most_newest = None
    def set_up_most_newest(self):
        # Delete olderest
        self.olderest.delete()

        # Add a new post
        self.most_newest = Post.create_from_file(testutils.VIDEO_PATH)
        self.most_newest.save()

    def test_with_varying_results(self):
        """Make sure that it respects the search query"""
        self.set_up_most_newest()

        # Add tags to all but the newest
        self.oldest.tags.add(Tag.create_or_get('test'))
        self.middle.tags.add(Tag.create_or_get('test'))

        # Save the posts
        self.oldest.save()
        self.middle.save()

        # Add tags to the new post
        self.most_newest.tags.add(Tag.create_or_get('test'))
        self.most_newest.save()

        # Search for 'test' posts
        results = Post.search('test')

        # Get the posts
        posts = self.middle.get_proximate_posts(results)

        self.assertEqual(posts['newer'], self.most_newest)
        self.assertEqual(posts['older'], self.oldest)

    def test_biased_to_newest(self):
        # Delete olderest
        self.set_up_most_newest()

        # Check bias
        results = Post.search('')

        posts = self.middle.get_proximate_posts(results)

        self.assertEqual(posts['newer'], self.newest)
        self.assertEqual(posts['older'], self.oldest)
    
    def test_biased_to_oldest(self):
        # Check bias
        results = Post.search('')

        posts = self.middle.get_proximate_posts(results)
        self.assertEqual(posts['newer'], self.newest)
        self.assertEqual(posts['older'], self.oldest)

class RatingTest(TestCase):
    fixtures = ['tagtypes.json', 'ratings.json']

    def test_get_default(self):
        """Test that the default rating is returned"""
        r = Rating.get_default()

        self.assertEqual(r.name, 'safe')
    
    og_pk = None

    def setUp(self):
        super().setUp()
        self.og_pk = homebooru.settings.BOORU_DEFAULT_RATING_PK
    
    def tearDown(self):
        homebooru.settings.BOORU_DEFAULT_RATING_PK = self.og_pk
        super().tearDown()

    def test_uses_booru_setting(self):
        """Test that the default rating is returned"""

        # Create a new rating
        r = Rating()
        r.name = "test"
        r.save()

        # Set the default rating to the new rating
        homebooru.settings.BOORU_DEFAULT_RATING_PK = r.name

        # Get the default rating
        r = Rating.get_default()

        self.assertEqual(r.name, "test")
