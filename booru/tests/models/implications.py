from django.test import TestCase
from booru.models import Post, Tag, Implication

class ImplicationApplyTest(TestCase):
    def setUp(self):
        Post.objects.all().delete()
        Tag.objects.all().delete()
        Implication.objects.all().delete()

    def test_apply_implication(self):
        """Test applying an implication to a post with the parent tag"""
        parent_tag = Tag(tag='parent')
        parent_tag.save()
        child_tag = Tag(tag='child')
        child_tag.save()

        post = Post(width=420, height=420, folder=1, md5='ca6ffc3babb6f0f58a7e5c0c6b61e7bf')
        post.save()
        post.tags.add(parent_tag)
        post.save()

        implication = Implication(parent='parent', child='child')
        implication.save()

        affected_posts = implication.apply()

        self.assertEqual(affected_posts, 1)
        self.assertIn(child_tag, post.tags.all())

    def test_apply_implication_no_parent_tag(self):
        """Test applying an implication to a post without the parent tag"""
        parent_tag = Tag(tag='parent')
        parent_tag.save()
        child_tag = Tag(tag='child')
        child_tag.save()

        post = Post(width=420, height=420, folder=1, md5='ca6ffc3babb6f0f58a7e5c0c6b61e7bf')
        post.save()

        implication = Implication(parent='parent', child='child')
        implication.save()

        affected_posts = implication.apply()

        self.assertEqual(affected_posts, 0)
        self.assertNotIn(child_tag, post.tags.all())

    def test_apply_implication_existing_child_tag(self):
        """Test applying an implication to a post with both parent and child tags"""
        parent_tag = Tag(tag='parent')
        parent_tag.save()
        child_tag = Tag(tag='child')
        child_tag.save()

        post = Post(width=420, height=420, folder=1, md5='ca6ffc3babb6f0f58a7e5c0c6b61e7bf')
        post.save()
        post.tags.add(parent_tag)
        post.tags.add(child_tag)
        post.save()

        implication = Implication(parent='parent', child='child')
        implication.save()

        affected_posts = implication.apply()

        self.assertEqual(affected_posts, 0)
        self.assertIn(child_tag, post.tags.all())

    def test_apply_implication_no_posts(self):
        """Test applying an implication when there are no posts"""
        parent_tag = Tag(tag='parent')
        parent_tag.save()
        child_tag = Tag(tag='child')
        child_tag.save()

        implication = Implication(parent='parent', child='child')
        implication.save()

        affected_posts = implication.apply()

        self.assertEqual(affected_posts, 0)
    
    def test_apply_when_parent_tag_does_not_exist(self):
        """Test applying an implication when the parent tag does not exist"""
        child_tag = Tag(tag='child')
        child_tag.save()

        post = Post(width=420, height=420, folder=1, md5='ca6ffc3babb6f0f58a7e5c0c6b61e7bf')
        post.save()

        implication = Implication(parent='parent', child='child')
        implication.save()

        affected_posts = implication.apply()

        self.assertEqual(affected_posts, 0)
        self.assertNotIn(child_tag, post.tags.all())
    
    def test_is_usable(self):
        """The is_usable property functions as intended"""
        parent_tag = Tag(tag='parent')
        parent_tag.save()

        implication = Implication(parent='parent', child='child')
        implication.save()

        self.assertTrue(implication.is_usable)

        # Delete the parent tag
        parent_tag.delete()

        self.assertFalse(implication.is_usable)