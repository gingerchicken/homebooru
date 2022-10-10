from django.test import TestCase

from booru.models import Tag, TagType, Post
import booru.tests.testutils as testutils
import homebooru.settings

class AutocompleteTest(TestCase):
    def setUp(self):
        # Create 60 tags, where the first 15 are of type 1, the next 15 are of type 2, and the last 30 are of type 3

        # First, create the tag types
        self.tag_type_1 = TagType.objects.create(name="tag_type_1")
        self.tag_type_2 = TagType.objects.create(name="tag_type_2")
        self.tag_type_3 = TagType.objects.create(name="tag_type_3")

        # Create the first 15 tags
        for i in range(15):
            Tag.objects.create(tag=f"tag_{i}", tag_type=self.tag_type_1)

        # Create the next 15 tags
        for i in range(15, 30):
            Tag.objects.create(tag=f"tag_{i}", tag_type=self.tag_type_2)
        
        # Create the last 30 tags
        for i in range(30, 60):
            Tag.objects.create(tag=f"tag_{i}", tag_type=self.tag_type_3)
        
        # Save the BOORU_AUTOCOMPLETE_MAX_TAGS setting
        self.autocomplete_max_tags = homebooru.settings.BOORU_AUTOCOMPLETE_MAX_TAGS
    
    def tearDown(self) -> None:
        # Restore the BOORU_AUTOCOMPLETE_MAX_TAGS setting
        homebooru.settings.BOORU_AUTOCOMPLETE_MAX_TAGS = self.autocomplete_max_tags
    
    def send_request(self, tag):
        return self.client.get(f"/tags/autocomplete/{tag}")

    def test_autocomplete(self):
        """Returns expected tags when given a partial tag"""

        homebooru.settings.BOORU_AUTOCOMPLETE_MAX_TAGS = 100

        # Test that the autocomplete endpoint returns the correct number of tags
        resp = self.send_request("tag_")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 60)

        actual_names = [
            i["tag"] for i in resp.json()
        ]

        # Make sure that they are all there
        for i in range(60):
            self.assertIn(f"tag_{i}", actual_names)
        
    def test_exact(self):
        """Returns the exact tag when given an exact tag"""

        # Test that the autocomplete endpoint returns the correct number of tags
        resp = self.send_request("tag_0")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.json()[0]["tag"], "tag_0")

    def test_format(self):
        """Returns the correct tag information"""

        # Test that the autocomplete endpoint returns the correct number of tags
        resp = self.send_request("tag_0")

        self.assertEqual(resp.status_code, 200)

        # Get the tag from the response
        tag = resp.json()[0]

        # Make sure that the tag is a dict
        self.assertIsInstance(tag, dict)

        # Make sure that it has the right tag value
        self.assertEqual(tag["tag"], "tag_0")

        # Make sure that it has the right tag type
        self.assertEqual(tag["type"], str(self.tag_type_1))

        # Make sure that it has the correct number of posts (0)
        self.assertEqual(tag["total"], 0)
    
    def test_sorts_by_posts(self):
        """Sorts tags by the number of posts they have"""

        # Create a basic post
        post = Post.create_from_file(
            testutils.FELIX_PATH
        )
        post.save()

        # Add the first tag to the post
        post.tags.add(Tag.objects.get(tag="tag_1"))
        post.save()

        # Search for the tag
        resp = self.send_request("tag_")

        # Make sure that the first tag is the one with the post
        self.assertEqual(resp.json()[0]["tag"], "tag_1")

        # Make sure that the total is 1
        self.assertEqual(resp.json()[0]["total"], 1)

        # Make sure that the second tag is the one without the post
        self.assertEqual(resp.json()[1]["total"], 0)

    def test_limits(self):
        """Limits results to setting"""

        # Set the limit to 10
        homebooru.settings.BOORU_AUTOCOMPLETE_MAX_TAGS = 10

        # Test that the autocomplete endpoint returns the correct number of tags
        resp = self.send_request("tag_")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 10)

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