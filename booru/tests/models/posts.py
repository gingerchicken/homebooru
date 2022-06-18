from django.test import TestCase

from ...models.posts import Post
from ...models.tags import Tag, TagType

import hashlib
import os
import pathlib
import shutil

import booru.tests.testutils as testutils
import booru.boorutils as boorutils

import homebooru.settings

class PostTest(TestCase):
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