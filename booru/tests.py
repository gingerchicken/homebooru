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
        # Get the total posts
        before_total_posts = Post.objects.count()

        p = Post(width=420, height=420, folder=0, md5='ca6ffc3babb6f0f58a7e5c0c6b61e7bf')
        
        # Make sure that the tags array is empty
        self.assertEqual(p.tags, [])

        # Add a tag
        p.tags.append('tag1')
        self.assertEqual(p.tags, ['tag1'])

        # Add another tag
        p.tags.append('tag2')
        self.assertEqual(p.tags, ['tag1', 'tag2'])

        # Save it
        p.save()

        # Check that the total
        self.assertEqual(Post.objects.count(), before_total_posts + 1)
    
    def test_tag_array_save(self):
        p = Post(width=420, height=420, folder=0, md5='ca6ffc3babb6f0f58a7e5c0c6b61e7bf')
        
        # Make sure that the tags array is empty
        self.assertEqual(p.tags, [])

        # Add a tag
        p.tags.append('tag1')
        p.tags.append('tag2')

        # Save it
        p.save()

        # Get the post
        p = Post.objects.get(md5='ca6ffc3babb6f0f58a7e5c0c6b61e7bf')

        # Make sure that the tags array is empty
        self.assertEqual(p.tags, ['tag1', 'tag2'])
    
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

# Tags
from .models import TagType, Tag
class TagTest(TestCase):
    def setUp(self):
        # Clear tables
        Tag.objects.all().delete()
        TagType.objects.all().delete()

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
        self.assertEqual(tag.count, 0)

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