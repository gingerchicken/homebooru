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
    
    def test_tag_search(self):
        # Create two posts with different tags
        p1 = Post(width=420, height=420, folder=0, md5='ca6ffc3babb6f0f58a7e5c0c6b61e7bf')
        p1.save()

        tag1 = Tag(tag='tag1')
        tag1.save()
        tag2 = Tag(tag='tag2')
        tag2.save()

        p1.tags.add(tag1)
        p1.tags.add(tag2)

        p1.save()

        p2 = Post(width=420, height=420, folder=0, md5='ca6ffc3b4bb6f0f58a7e5c0c6b61e7bf')
        p2.save()

        tag3 = Tag(tag='tag3')
        tag3.save()
        tag4 = Tag(tag='tag4')
        tag4.save()

        p2.tags.add(tag3)
        p2.tags.add(tag4)

        p2.save()

        # Search for the tag 'tag1'
        posts = Post.objects.filter(tags=tag1)

        # Make sure that only one post was returned
        self.assertEqual(len(posts), 1)

        # Make sure that the post returned is the correct one
        self.assertEqual(posts[0].md5, 'ca6ffc3babb6f0f58a7e5c0c6b61e7bf')

        # Search for tags that contain 'tag1' and 'tag3' (only if they contain both)
        posts = Post.objects.filter(tags=tag1).filter(tags=tag3)

        # Make sure that no posts were returned
        self.assertEqual(len(posts), 0)

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
        self.assertEqual(tag.tag, 'tag1')

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