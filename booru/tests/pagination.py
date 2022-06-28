from django.test import TestCase

import math

from booru.pagination import Paginator
from booru.models import Post
import booru.boorutils as boorutils

class PaginatorTest(TestCase):
    def test_total_pages(self):
        """Returns expected total pages"""
        paginator = Paginator(1, 50, 10)
        self.assertEqual(paginator.total_pages, 5)
    
        paginator = Paginator(1, 50, 25)
        self.assertEqual(paginator.total_pages, 2)

    def test_total_pages_edge_case(self):
        """When there is just a bit over a page, the total pages should be rounded up"""
        paginator = Paginator(1, 51, 10)
        self.assertEqual(paginator.total_pages, 6)
    
        paginator = Paginator(1, 50, 20)
        self.assertEqual(paginator.total_pages, 3)
    
        paginator = Paginator(1, 49, 20)
        self.assertEqual(paginator.total_pages, 3)
    
    def test_display_arrows_left(self):
        """Returns expected display arrows left"""
        paginator = Paginator(1, 50, 1, width=4)
        self.assertEqual(paginator.display_arrows_left, False)

        paginator = Paginator(6, 50, 1, width=4)
        self.assertEqual(paginator.display_arrows_left, True)
        
        paginator = Paginator(5, 50, 1, width=4)
        self.assertEqual(paginator.display_arrows_left, False)
    
    def test_display_arrows_right(self):
        """Returns expected display arrows right"""
        paginator = Paginator(1, 50, 1, width=4)
        self.assertEqual(paginator.display_arrows_right, True)

        paginator = Paginator(45, 50, 1, width=4)
        self.assertEqual(paginator.display_arrows_right, True)

        # Cases where the end is in site of the current page
        paginator = Paginator(46, 50, 1, width=4)
        self.assertEqual(paginator.display_arrows_right, False)
        
        paginator = Paginator(1, 50, 25, width=4)
        self.assertEqual(paginator.display_arrows_right, False)

    def test_has_prev(self):
        """Returns expected has prev"""
        paginator = Paginator(1, 50, 10)
        self.assertEqual(paginator.has_prev, False)

        paginator = Paginator(2, 50, 10)
        self.assertEqual(paginator.has_prev, True)
    
    def test_prev(self):
        """Returns expected prev"""
        paginator = Paginator(2, 50, 40)
        self.assertEqual(paginator.prev, 1)
    
    def test_numbers(self):
        """Returns expected numbers"""

        # Just general cases here
        paginator = Paginator(1, 500, 10, width=4)
        self.assertEqual(paginator.numbers, [1, 2, 3, 4, 5])

        # Test if the numbers shift to the right
        paginator = Paginator(6, 500, 10, width=4)
        self.assertEqual(paginator.numbers, [ 2, 3, 4, 5, 6, 7, 8, 9, 10])

        paginator = Paginator(4, 500, 10, width=4)
        self.assertEqual(paginator.numbers, [1, 2, 3, 4, 5, 6, 7, 8])

        # Check if it handles the end correctly
        paginator = Paginator(45, 500, 10, width=4)
        self.assertEqual(paginator.numbers, [41, 42, 43, 44, 45, 46, 47, 48, 49])

        paginator = Paginator(46, 500, 10, width=4)
        self.assertEqual(paginator.numbers, [42, 43, 44, 45, 46, 47, 48, 49, 50])
    
        # Check if it handles going past the end correctly
        paginator = Paginator(1, 500, 100, width=8)
        self.assertEqual(paginator.numbers, [1, 2, 3, 4, 5])

    def test_has_next(self):
        """Returns expected has next"""
        paginator = Paginator(1, 50, 40)
        self.assertEqual(paginator.has_next, True)

        paginator = Paginator(2, 50, 40)
        self.assertEqual(paginator.has_next, False)
    
    def test_next(self):
        """Returns expected next"""
        paginator = Paginator(1, 50, 40)
        self.assertEqual(paginator.next, 2)

class PaginatorPaginate(TestCase):
    def example_search(self):
        return Post.objects.all().order_by('-id')

    def setUp(self):
        super().setUp()

        Post.objects.all().delete()

        # Create a bunch of posts for generating a query set
        for i in range(0, 100):
            post = Post(width=420, height=420, folder=0, md5=boorutils.hash_str(str(i)))
            post.save()
    
    def tearDown(self):
        super().tearDown()

    def assertPaginated(self, per_page = 10):
        # Search for all posts
        all_posts = self.example_search()
        max_pages = math.ceil(len(all_posts) / per_page)
        
        for page in range(1, max_pages + 1):
            results, p = Paginator.paginate(all_posts, page, per_page)
            
            self.assertIsInstance(p, Paginator)
            self.assertEqual(p.total_pages, max_pages)
            self.assertEqual(p.page, page)
            self.assertEqual(p.total_count, len(all_posts))

            total = len(all_posts) % per_page if page == max_pages else per_page
            if len(all_posts) % per_page == 0 and page == max_pages:
                total = per_page

            # There should be 10 results
            self.assertEqual(len(results), total)

            # Results should be the last 90-80 posts
            for i in range(0, total):
                j = per_page * (page - 1) + i

                actual = results[i]
                expected = all_posts[j]

                self.assertEqual(actual, expected, "Expected %s, got %s (in page %s)" % (expected, actual, page))


    def test_pagination_with_even(self):
        """Pagination with even number of results"""
        self.assertPaginated()
    
    def test_pagination_with_odd(self):
        """Pagination with odd number of results"""
        self.assertPaginated(per_page=11)