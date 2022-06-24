from django.test import TestCase

from ...models.tags import TagType, Tag
from ...models.posts import Post

import homebooru.settings

class TagTest(TestCase):
    fixtures = ['booru/fixtures/tagtypes.json']
    
    def test_reference_type(self):
        """Adds reference to a tag type correctly"""

        # Get the default tag type
        artist = TagType.objects.get(name='artist')

        # Create a tag
        tag = Tag(tag='tag1', tag_type=artist)
        tag.save()

        # Get the tag
        tag = Tag.objects.get(tag='tag1')

        # Make sure the tag type is the default one
        self.assertEqual(tag.tag_type, artist)
    
    def test_type_default(self):
        """Defaults the tag type to the default tag type"""

        # Create a tag
        tag = Tag(tag='tag1')
        tag.save()

        # Get the tag
        tag = Tag.objects.get(tag='tag1')

        # Make sure the tag type is the default one
        self.assertEqual(tag.tag_type, TagType.objects.get(name=homebooru.settings.BOORU_DEFAULT_TAG_TYPE_PK))
    
    def test_defaults_count_zero(self):
        """Defaults the count to zero"""

        # Create a tag
        tag = Tag(tag='tag1')
        tag.save()

        # Get the tag
        tag = Tag.objects.get(tag='tag1')

        # Make sure the tag type is the default one
        self.assertEqual(tag.tag, 'tag1')

    def test_total_posts(self):
        """Gets correct total count"""

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
        """Creates or gets if the tag isn't in the database"""

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
        """Gets the tag if it is in the database"""

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
        """Accepts valid tag names"""

        valid_tags = ['1tag', 'funny_monkey', '=.=', ':=>', ':3', 're:zero']

        for tag in valid_tags:
            self.assertTrue(Tag.is_name_valid(tag))
    
    def test_is_name_valid_with_invalid(self):
        """Rejects invalid tag names"""

        invalid_tags = ['', '     ', 'e', 'funny-monkey', 'funny monkey', 'HeHehe', '*.*']

        for tag in invalid_tags:
            self.assertFalse(Tag.is_name_valid(tag))
    
    def test_is_name_valid_with_parameters(self):
        """Rejects parameter-like tags"""

        invalid_tags = ['md5:something', 'rating:safe', 'rating:', 'width:42', 'height:432423', 'height:', 'title:test']

        for tag in invalid_tags:
            self.assertFalse(Tag.is_name_valid(tag))

class TagSearchTest(TestCase):
    fixtures = ['booru/fixtures/tagtypes.json']
    
    def test_search_with_tag(self):
        """Searches for a tag"""

        # Create a tag
        tag = Tag(tag='tag1')
        tag.save()

        # Search for the tag
        tags = Tag.search('tag1')

        # Make sure the tag is in the list
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0].tag, 'tag1')
    
    def test_search_with_empty(self):
        """Returns all tags when searching for an empty string"""

        # Create a tag
        tag = Tag(tag='tag1')
        tag.save()

        # Make another tag
        tag = Tag(tag='tag2')
        tag.save()

        # Search for the tag
        tags = Tag.search('')

        # Make sure the tag is in the list
        self.assertEqual(len(tags), 2)

        # Make sure the tags are in the list
        self.assertEqual(tags[0].tag, 'tag1')
        self.assertEqual(tags[1].tag, 'tag2')

    def test_search_with_wildcard(self):
        """Searches for a tag with a wildcard"""

        # Create a tag
        tag = Tag(tag='tag1')
        tag.save()

        # Create another tag
        tag = Tag(tag='hag1')
        tag.save()

        # Search for the tag
        tags = Tag.search('tag*')

        # Make sure the tag is in the list
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0].tag, 'tag1')

        # Searcg for another wildcard
        tags = Tag.search('*ag1')

        # Make sure the tag is in the list
        self.assertEqual(len(tags), 2)
        self.assertEqual(tags[0].tag, 'hag1')
        self.assertEqual(tags[1].tag, 'tag1')

    def test_sort_param(self):
        """Sorts accordingly to sort_param"""

        # Create a tag
        tag1 = Tag(tag='tag1')
        tag1.save()

        tag1.tag_type = TagType.objects.get(name='copyright')
        tag1.save()

        # Create another tag
        tag2 = Tag(tag='tag2')
        tag2.save()

        tag2.tag_type = TagType.objects.get(name='artist')
        tag2.save()

        # Create another tag
        tag3 = Tag(tag='tag3')
        tag3.save()

        tag3.tag_type = TagType.objects.get(name='deprecated')
        tag3.save()

        # Search for the tag
        tags = Tag.search('', sort_param='tag')

        # Make sure the tag is in the list
        self.assertEqual(len(tags), 3)

        # Make sure the tags are in the list
        self.assertEqual(tags[0].tag, 'tag1')
        self.assertEqual(tags[1].tag, 'tag2')
        self.assertEqual(tags[2].tag, 'tag3')

        # Search for the tag
        tags = Tag.search('', sort_param='type')

        # Make sure the tag is in the list
        self.assertEqual(len(tags), 3)

        # Make sure the tags are in the list
        self.assertEqual(tags[0].tag, 'tag2')
        self.assertEqual(tags[1].tag, 'tag1')
        self.assertEqual(tags[2].tag, 'tag3')

        # TODO add test for total posts