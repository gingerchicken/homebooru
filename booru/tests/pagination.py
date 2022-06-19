from django.test import TestCase

from booru.pagination import Paginator

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

        paginator = Paginator(46, 50, 1, width=4)
        self.assertEqual(paginator.display_arrows_right, False)

    def test_has_prev(self):
        """Returns expected has prev"""
        paginator = Paginator(1, 50, 10)
        self.assertEqual(paginator.has_prev, False)

        paginator = Paginator(2, 50, 10)
        self.assertEqual(paginator.has_prev, True)
    
    def test_numbers(self):
        """Returns expected numbers"""
        paginator = Paginator(1, 500, 10, width=4)
        self.assertEqual(paginator.numbers, [1, 2, 3, 4, 5])

        paginator = Paginator(6, 500, 10, width=4)
        self.assertEqual(paginator.numbers, [ 2, 3, 4, 5, 6, 7, 8, 9, 10])

        paginator = Paginator(4, 500, 10, width=4)
        self.assertEqual(paginator.numbers, [1, 2, 3, 4, 5, 6, 7, 8])

        paginator = Paginator(45, 500, 10, width=4)
        self.assertEqual(paginator.numbers, [41, 42, 43, 44, 45, 46, 47, 48, 49])

        paginator = Paginator(46, 500, 10, width=4)
        self.assertEqual(paginator.numbers, [42, 43, 44, 45, 46, 47, 48, 49, 50])