from django.test import TestCase

from ...models.tags import TagType, Tag
from ...models.posts import Post

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
        
    def test_create_or_get_creates(self):
        before = Tag.objects.count()
        # Create a tag
        tag = Tag.create_or_get('tag1')

        # Get the tag
        tag = Tag.objects.get(tag='tag1')

        # Make sure the tag type is the default one
        self.assertEqual(tag.tag, 'tag1')

        # Make sure that a new tag was created
        self.assertEqual(Tag.objects.count(), before + 1)
    
    def test_create_or_get_gets(self):
        # Create a tag type
        artist = TagType(name='artist', description='Artist')
        
        # Create a tag
        t = Tag(tag='tag1')
        t.tag_type = artist
        t.save()

        # Get the tag
        tag = Tag.create_or_get('tag1')

        # Make sure the tag type is the default one
        self.assertEqual(tag.tag, 'tag1')
        self.assertEqual(tag.tag_type, artist)

        # Make sure that a new tag was not created
        self.assertEqual(Tag.objects.count(), 1)
    
    def test_is_name_valid_with_valid(self):
        valid_tags = ['1tag', 'funny_monkey', '=.=', ':=>']

        for tag in valid_tags:
            self.assertTrue(Tag.is_name_valid(tag))
    
    def test_is_name_valid_with_invalid(self):
        invalid_tags = ['', '     ', 'e', 'funny-monkey', 'funny monkey', 'HeHehe', '*.*']

        for tag in invalid_tags:
            self.assertFalse(Tag.is_name_valid(tag))