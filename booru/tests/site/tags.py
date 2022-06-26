from django.test import TestCase

from ...models.tags import Tag, TagType

class TagEdit(TestCase):
    fixtures = ['tagtypes.json']

    tag = None

    def setUp(self):
        super().setUp()

        # Add a tag
        self.tag = Tag.create_or_get('test_tag')
        self.tag.tag_type = TagType.objects.get(name='general')
        self.tag.save()

    def make_request(self, tag_type, tag_name):
        response = self.client.post('/tags/edit?tag=' + tag_name, {
            'tag_type': tag_type
        })

        return response


    def test_valid_tag_edit(self):
        # Get the tag type before
        before = self.tag.tag_type.name

        # Make a request to edit the tag
        response = self.make_request('artist', 'test_tag')

        # Get the tag type after
        self.tag = Tag.objects.get(tag='test_tag')

        # Check that the tag type was changed
        self.assertEqual(self.tag.tag_type.name, 'artist')

        # Make sure that the first one is different from the second
        self.assertNotEqual(before, self.tag.tag_type.name)

        # Make sure that the response was a redirect
        self.assertEqual(response.status_code, 302)

        # Make sure that it redirects to the correct page
        self.assertEqual(response.url, '/tags?tag=test_tag')

    def test_invalid_tag_type_tag_edit(self):
        # Make a request to edit the tag
        response = self.make_request('invalid', 'test_tag')

        # Check that the response was a 404
        self.assertEqual(response.status_code, 404)

        # Make sure that the tag type was not changed
        self.tag = Tag.objects.get(tag='test_tag')
        self.assertEqual(self.tag.tag_type.name, 'general')

    
    def test_invalid_tag_name_tag_edit(self):
        # Make a request to edit the tag
        response = self.make_request('artist', 'invalid')

        # Check that the response was a 404
        self.assertEqual(response.status_code, 404)

        # Make sure that the tag type was not changed
        self.tag = Tag.objects.get(tag='test_tag')

        # Check that the tag type was not changed
        self.assertEqual(self.tag.tag_type.name, 'general')