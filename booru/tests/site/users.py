from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class LoginPageTest(TestCase):
    def setUp(self):
        # Create a user called fred
        self.fred = User.objects.create_user(
            username='fred',
            password='somethingextremelysecure'
        )
        self.fred.save()

        # Create a user called jane
        self.jane = User.objects.create_user(
                username='jane',
                password='somethingelseverysecure'
        )
        self.jane.save()

    def test_login(self):
        """Make sure that the user can login"""

        # Try to login with the wrong password
        response = self.client.post(reverse('login'), {
            'username': 'fred',
            'password': 'wrongpassword'
        })

        # Check that the user is still logged out
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('user').is_authenticated, False)

        # Make sure the context has an error message
        self.assertIn(response.context.get('error'), 'Invalid credentials')

        # Try to login with the correct password
        response = self.client.post(reverse('login'), {
            'username': 'fred',
            'password': 'somethingextremelysecure'
        })

        # Check that the user is now logged in
        self.assertEqual(response.status_code, 302)

        # Follow the redirect to the index page
        response = self.client.get(response.url)

        # Check that the user is now logged in
        self.assertEqual(response.context.get('user').is_authenticated, True)

        # Make sure that it is the correct user
        self.assertEqual(response.context.get('user').username, 'fred')

    def test_login_no_attempt(self):
        """Make sure that the page doesn't show an error by default"""

        # Get the login page
        response = self.client.get(reverse('login'))

        # Check that the user is still logged out
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('user').is_authenticated, False)

        # Make sure the context has no error message
        self.assertEqual(response.context.get('error'), None)