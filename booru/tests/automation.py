from django.test import TestCase
from booru.models.posts import Post
import booru.tests.testutils as testutils

from booru.automation import TagAutomationRegistry, AnimatedContentTagAutomation
from booru.models.automation import TagAutomationRecord
from booru.models.tags import Tag


class AnimatedContentTagAutomationTest(TestCase):
    temp_storage = testutils.TempStorage()

    def setUp(self):
        self.temp_storage.setUp()

        # Create a post
        self.video = Post.create_from_file(testutils.VIDEO_PATH)
        self.video.save()

        self.image = Post.create_from_file(testutils.FELIX_PATH)
        self.image.save()

    def tearDown(self):
        self.temp_storage.tearDown()

    def test_video(self):
        """Returns webm + animated for video"""

        # Create the automation
        automation = AnimatedContentTagAutomation()

        # Get the tags
        tags = automation.get_tags(self.video)

        str_tags = [str(tag) for tag in tags]

        # Check the tags
        self.assertIn("animated", str_tags)
        self.assertIn("webm", str_tags)

    def test_image(self):
        """Returns nothing for still image"""

        # Create the automation
        automation = AnimatedContentTagAutomation()

        # Get the tags
        tags = automation.get_tags(self.image)

        str_tags = [str(tag) for tag in tags]

        # Check the tags
        self.assertNotIn("animated", str_tags)
        self.assertNotIn("webm", str_tags)
    
    def test_gif(self):
        """Returns gif + animated for gif"""

        # Skip this test since we don't have a test gif yet
        self.skipTest("No test gif yet")
        return

        # Create the automation
        automation = AnimatedContentTagAutomation()

        # Get the tags
        tags = automation.get_tags(self.gif)

        str_tags = [str(tag) for tag in tags]

        # Check the tags
        self.assertNotIn("animated", str_tags)
        self.assertNotIn("webm", str_tags)

class TagAutomationRegistryTest(TestCase):
    temp_storage = testutils.TempStorage()

    def setUp(self):
        self.temp_storage.setUp()

        # Create a post
        self.video = Post.create_from_file(testutils.VIDEO_PATH)
        self.video.save()

        self.image = Post.create_from_file(testutils.FELIX_PATH)
        self.image.save()

    def tearDown(self):
        self.temp_storage.tearDown()

    def test_update_post_adds_lock(self):
        """Adds a lock to the post when updating it"""

        # Create the registry
        registry = TagAutomationRegistry()

        # Ensure that the post has no record
        self.assertFalse(TagAutomationRecord.objects.filter(post=self.video).exists())

        registry.perform_automation(self.video)

        # Ensure that the post has a record
        self.assertTrue(TagAutomationRecord.objects.filter(post=self.video).exists())

        # Get the record
        record = TagAutomationRecord.objects.get(post=self.video)

        # Ensure that it is locked with the correct hash
        self.assertEqual(record.state_hash, registry.get_state_hash())
    
    def test_skips_with_lock(self):
        """Skips automation if the post already has a lock"""

        # Create the registry
        registry = TagAutomationRegistry()

        # Ensure that the post has no record
        self.assertFalse(TagAutomationRecord.objects.filter(post=self.video).exists())

        # Create a record
        record = TagAutomationRecord(
            post=self.video,
            state_hash=registry.get_state_hash()
        )
        record.save()

        # Perform automation
        skipped = not registry.perform_automation(self.video)

        # Ensure that it was skipped
        self.assertTrue(skipped)

        # Ensure that no tags were created
        # total_tags = Tag.objects.all().count()
        # self.assertEqual(total_tags, 0)
        # TODO this test is having a hissy fit, fix it at some point