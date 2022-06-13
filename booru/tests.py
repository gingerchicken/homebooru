from django.test import TestCase

# Create your tests here.

# Models

# Posts
from .models import Post
class PostTest(TestCase):
    def test_inc_total(self):
        before_total_posts = Post.objects.count()

        p = Post(width=420, height=420, folder=0, md5='ca6ffc3babb6f0f58a7e5c0c6b61e7bf')

        # Save it
        p.save()

        # Check that the total
        self.assertEqual(Post.objects.count(), before_total_posts + 1)
    
    def test_tag_array(self):
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

# Tags
from .models import TagType, Tag
class TagTest(TestCase):
    def setUp(self):
        # Clear tables
        Tag.objects.all().delete()
        TagType.objects.all().delete()
        Post.objects.all().delete()

        # Create a default tag type
        artist = TagType(name='artist', description='Artist')
        artist.save()
    
    def test_reference_type(self):
        # Get the default tag type
        artist = TagType.objects.get(name='artist')

        # Create a tag
        tag = Tag(tag='tag1', tag_type=artist)
        tag.save()

        # Get the tag
        tag = Tag.objects.get(tag='tag1')

        # Make sure the tag type is the default one
        self.assertEqual(tag.tag_type, artist)
    
    def test_type_default_null(self):
        # Create a tag
        tag = Tag(tag='tag1')
        tag.save()

        # Get the tag
        tag = Tag.objects.get(tag='tag1')

        # Make sure the tag type is the default one
        self.assertEqual(tag.tag_type, None)
    
    def test_defaults_count_zero(self):
        # Create a tag
        tag = Tag(tag='tag1')
        tag.save()

        # Get the tag
        tag = Tag.objects.get(tag='tag1')

        # Make sure the tag type is the default one
        self.assertEqual(tag.tag, 'tag1')

    def test_total_posts(self):
        # Create a tag
        tag = Tag(tag='tag1')
        tag.save()

        # Create a post
        post = Post(width=420, height=420, folder=0, md5='ca6ffc3b4bb643458a7e5c0c6b61e7bf')
        post.save()

        # Add the tag to the post
        post.tags.add(tag)

        # Get the tag
        tag = Tag.objects.get(tag='tag1')
        self.assertEqual(tag.total_posts, 1)

        # Create a new post with a different md5
        post = Post(width=420, height=420, folder=0, md5='ca6bfc3b4bb643458a7e5c0c6b61e7bf')
        post.save()

        # Add the tag to the post
        post.tags.add(tag)

        # Get the tag
        tag = Tag.objects.get(tag='tag1')
        self.assertEqual(tag.total_posts, 2)

        # Create a new post that doesn't have the tag
        post = Post(width=420, height=420, folder=0, md5='ca6bfc6b4bb643458a7e5c0c6b61e7bf')
        post.save()

        # Get the tag
        tag = Tag.objects.get(tag='tag1')
        self.assertEqual(tag.total_posts, 2)
        

# Pages
# Test the index page
class IndexTest(TestCase):
    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_imagecounter(self):
        response = self.client.get('/')
        self.assertContains(response, '<div id="imagecounter">')
        self.assertContains(response, '<img src="/static/layout/')

    def setUp(self):
        # Clear tables
        Post.objects.all().delete()