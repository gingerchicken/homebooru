from django.test import TestCase
import booru.views.filters as filters

class TagViewTest(TestCase):
    def test_removes_underscores(self):
        """Removes underscores from a string"""

        result = filters.tag_view('tag_name')

        self.assertEqual(result, 'tag name')

class RemoveTest(TestCase):
    def test_removes_string(self):
        """Removes a string from another string"""

        result = filters.remove('string', 'string')

        self.assertEqual(result, '')
    
    def test_removes_substring(self):
        """Removes a substring from another string"""

        result = filters.remove('string', 'ing')

        self.assertEqual(result, 'str')
    
class GetItemTest(TestCase):
    data_dict = {
        'key': 'value',
        'key2': 'value2',
        'foo': 'bar'
    }

    def test_returns_value(self):
        """Returns expected value"""

        result = filters.get_item(self.data_dict, 'key')

        self.assertEqual(result, 'value')
    
    def test_returns_none(self):
        """Returns None if key not found"""

        result = filters.get_item(self.data_dict, 'key3')

        self.assertEqual(result, None)

class ConcatTest(TestCase):
    def test_concats_strings(self):
        """Concats two strings"""

        result = filters.concat('string', 'cat')

        self.assertEqual(result, 'stringcat')

    def test_concats_none(self):
        """Concats two None values"""

        result = filters.concat(None, None)

        self.assertEqual(result, 'NoneNone')

    def test_concats_string_and_none(self):
        """Concats a string and None"""

        result = filters.concat('string', None)

        self.assertEqual(result, 'stringNone')