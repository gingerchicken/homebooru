from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from booru.models.profile import Profile
from booru.models.posts import Post
import booru.tests.testutils as testutils

class LoginPageTest(TestCase):
    def setUp(self):
        # Create a user called fred
        self.fred = User.objects.create_user(
            username='fred',
            password='SomethingExtrem31ySecure!'
        )
        self.fred.save()

        # Create a user called jane
        self.jane = User.objects.create_user(
                username='jane',
                password='SomethingV3rySecure!'
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
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.context.get('user').is_authenticated, False)

        # Check that the username persists
        self.assertEqual(response.context.get('username'), 'fred')

        # Make sure the context has an error message
        self.assertIn(response.context.get('error'), 'Invalid credentials')

        # Try to login with the correct password
        response = self.client.post(reverse('login'), {
            'username': 'fred',
            'password': 'SomethingExtrem31ySecure!'
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

class RegisterTest(TestCase):
    def register(self, username, password, conf_password, email):
        return self.client.post(reverse('register'), {
            'username': username,
            'password': password,
            'conf_password': conf_password,
            'email': email
        })

    def test_register(self):
        """Test that the register creates a new user"""

        # Make sure that a user by the name fred doesn't already exist
        self.assertFalse(User.objects.filter(username='fred').exists())

        # Try to register a user with a valid username
        response = self.register('fred', 'SomethingExtrem31ySecure!', 'SomethingExtrem31ySecure!', 'test@gmail.com')

        # Check that the user now exists
        self.assertTrue(User.objects.filter(username='fred').exists())

        # Check that they get redirected to the homepage
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))

        # Get the new user
        user = User.objects.get(username='fred')

        # Check that the user has the correct email
        self.assertEqual(user.email, 'test@gmail.com')

        # Of course, we cannot confirm the reset since the password should be hashed!

    def test_register_no_username(self):
        """Test that the register doesn't create a user if no username is given"""
        # Try to register a user with no username
        response = self.register('', 'SomethingExtrem31ySecure!', 'SomethingExtrem31ySecure!', 'test@gmail.com')

        # Check that the user doesn't exist
        self.assertFalse(User.objects.filter(username='').exists())

        # Check that an error message is shown
        self.assertIn(response.context.get('error'), 'Invalid username')
    
    def test_register_no_password(self):
        """Test that the register doesn't create a user if no password is given"""
        # Try to register a user with no password
        response = self.register('fred', '', '', 'test@gmail.com')

        # Check that the user doesn't exist
        self.assertFalse(User.objects.filter(username='fred').exists())

        # Check that an error message is shown
        self.assertIn('Password is not valid', response.context.get('error'))

        # Check that the username persists
        self.assertEqual(response.context.get('username'), 'fred')

        # Check that the email persists
        self.assertEqual(response.context.get('email'), 'test@gmail.com')

    def test_register_no_conf_password(self):
        """Test that the register doesn't create a user if no confirmation password is given"""
        # Try to register a user with no confirmation password
        response = self.register('fred', 'SomethingExtrem31ySecure!', '', 'test@gmail.com')

        # Check that the user doesn't exist
        self.assertFalse(User.objects.filter(username='fred').exists())

        # Check that an error message is shown
        self.assertIn(response.context.get('error'), 'Passwords do not match')

        # Check the case where they don't match but one is given
        response = self.register('fred', 'SomethingExtrem31ySecure!', 'SomethingV3rySecure!', '')

        # Check that an error message is shown
        self.assertIn(response.context.get('error'), 'Passwords do not match')
    
        # email and username persisted
        self.assertEqual(response.context.get('username'), 'fred')

    def test_register_no_email(self):
        """Test that no email is acceptable"""

        # Try to register a user with no email
        response = self.register('fred', 'SomethingExtrem31ySecure!', 'SomethingExtrem31ySecure!', '')

        # Check that the user is created
        self.assertTrue(User.objects.filter(username='fred').exists())

        # Make sure that the user has no email
        self.assertEqual(User.objects.get(username='fred').email, '')

        # Check that they get redirected to the homepage
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))
    
    def test_duplicate_username(self):
        """Test that a user cannot register with a username that already exists"""

        # Create a user called fred
        self.fred = User.objects.create_user(
            username='fred',
            password='SomethingExtrem31ySecure!'
        )
        self.fred.save()

        # Try to register a user with the same username
        response = self.register('fred', 'SomethingV3rySecure!', 'SomethingV3rySecure!', 'test@gmail.com')

        # Check that an error message is shown
        self.assertIn(response.context.get('error'), 'Username already exists')

        # Check that the user is still there
        self.assertTrue(User.objects.filter(username='fred').exists())

        # Make sure that the newly given information doesn't change the user
        self.assertEqual(User.objects.get(username='fred').email, '')

        # Email persists
        self.assertEqual(response.context.get('email'), 'test@gmail.com')

    def test_reject_invalid_usernames(self):
        invalid_usernames = [
            'a', 'aa', 'a' * 5000, 'b@ss', 'noob!'
        ]

        for username in invalid_usernames:
            response = self.register(username, 'SomethingExtrem31ySecure!', 'SomethingExtrem31ySecure!', 'test@gmail.com')

            # Check that an error message is shown
            self.assertIn(response.context.get('error'), 'Invalid username')

            # Check that no user is created
            self.assertFalse(User.objects.filter(username=username).exists())
    
    def test_reject_invalid_passwords(self):
        invalid_passwords = [
            'a', 'aa', 'a' * 5000, 'b@ss', 'noob!'
        ]

        for password in invalid_passwords:
            response = self.register('fred', password, password, 'test@gmail.com')

            # Check that an error message is shown
            self.assertIn('Password is not valid', response.context.get('error'))

            # Check that the username and email persist
            self.assertEqual(response.context.get('username'), 'fred')
            self.assertEqual(response.context.get('email'), 'test@gmail.com')

    def test_reject_duplicate_email(self):
        """Test that a user cannot register with an email that already exists"""

        # Create a user called fred
        self.fred = User.objects.create_user(
            username='fred',
            password='SomethingExtrem31ySecure!',
            email='test@gmail.com'
        )
        self.fred.save()

        # Try to register a user with the same email
        response = self.register('fred2', 'SomethingExtrem31ySecure!', 'SomethingExtrem31ySecure!', 'test@gmail.com')

        # Check that an error message is shown
        self.assertIn(response.context.get('error'), 'Email already exists')

        # Check that the username persists
        self.assertEqual(response.context.get('username'), 'fred2')
    
    def test_reject_invalid_email(self):
        """Test rejects invalid emails"""

        invalid_emails = [
            'a', 'aa', 'a' * 5000, 'b@ss', 'noob!', 'gaming@gaming@gamin.com', 'whoasked', 'example.com'
        ]

        for email in invalid_emails:
            response = self.register('fred', 'SomethingExtrem31ySecure!', 'SomethingExtrem31ySecure!', email)

            # Make sure that the error is 400
            self.assertEqual(response.status_code, 400, 'Didn\'t reject: ' + email)

            # Check that the error context is correct
            self.assertIn(response.context.get('error'), 'Email is not valid')

            # Check that the username persists
            self.assertEqual(response.context.get('username'), 'fred')

class ProfileTest(TestCase):
    def test_user_not_found(self):
        """Returns 404 with correct error when not found"""

        # Try to get a profile for a user that doesn't exist
        response = self.client.get(reverse('profile', kwargs={'user_id': 4300}))

        # Check that the user is not found
        self.assertEqual(response.status_code, 404)
        self.assertIn(response.context.get('error'), 'User does not exist')

        # Make sure that no owner or profile is given
        self.assertIsNone(response.context.get('owner'))
        self.assertIsNone(response.context.get('profile'))

    def test_user_found(self):
        """Returns 200 with correct profile when found"""

        # Create a user called fred
        self.fred = User.objects.create_user(
            username='fred',
            password='SomethingExtrem31ySecure!'
        )
        self.fred.save()

        # Try to get a profile for the user
        response = self.client.get(reverse('profile', kwargs={'user_id': self.fred.id}))

        # Check that the user is found
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('owner'), self.fred)

        # Returns correct profile
        profile = Profile.create_or_get(self.fred)
        self.assertEqual(response.context.get('profile'), profile)


class LogoutTest(TestCase):
    """Tests for the logout view"""

    def test_logout(self):
        """Test that the logout view works"""

        # Create a user
        self.fred = User.objects.create_user(
            username='fred',
            password='SomethingExtrem31ySecure!'
        )
        self.fred.save()

        # Log the user in
        self.client.login(username='fred', password='SomethingExtrem31ySecure!')

        # Try to log the user out
        response = self.client.get(reverse('logout'))

        # Check that the user is logged out
        self.assertFalse(self.client.session.get('_auth_user_id'))

        # Check that they get redirected to the homepage
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))
    
    def test_logout_no_user(self):
        """Test that the logout view works when no user is logged in"""

        # Try to log the user out
        response = self.client.get(reverse('logout'))

        # Check that they get redirected to the homepage
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))

class PostFavouritesTest(TestCase):
    """Tests for the add post to favourites view"""

    temp_storage = testutils.TempStorage()

    def setUp(self):
        # Use the temp storage
        self.temp_storage.setUp()

        # Create a user
        self.fred = User.objects.create_user(
            username='fred',
            password='SomethingExtrem31ySecure!'
        )
        self.fred.save()

        # Create a post
        self.post = Post.create_from_file(testutils.FELIX_PATH)
        self.post.save()

        # Log the user in
        self.client.login(username='fred', password='SomethingExtrem31ySecure!')

    def tearDown(self):
        self.temp_storage.tearDown()
    
    def send_request(self, user_id = None, post_id = None):
        """Send a request to the add post to favourites view"""

        # Defaults to the current user and post
        user_id = user_id or self.fred.id
        post_id = post_id or self.post.id

        return self.client.post(reverse('favourites', kwargs={'user_id': user_id}), {'post_id': post_id})

    def get_favs(self):
        """Get the favourites for the user"""

        # Get the profile
        profile = Profile.create_or_get(self.fred)

        # Get the favourites
        return profile.favourites.all()

    def test_add_favourite(self):
        """Test that a user can add a post to their favourites"""

        # Send a request to add the post to favourites
        response = self.send_request()

        # Check that the post is added to the favourites
        self.assertTrue(self.get_favs().filter(id=self.post.id).exists())

        # Check that the response is a 200
        self.assertEqual(response.status_code, 200)

    def test_rejects_invalid_post_id(self):
        """Rejects posts with invalid ids"""

        invalid_ids = [
            432894327
        ]

        for id in invalid_ids:
            response = self.send_request(post_id=id)

            # Check that the response is a 404
            self.assertEqual(response.status_code, 404, 'Didn\'t reject: ' + str(id))

            # Check that the favourite is not added
            self.assertFalse(self.get_favs().filter(id=id).exists())
        
    def test_rejects_invalid_user_id(self):
        """Rejects users with invalid ids"""

        invalid_ids = [
            432894327
        ]

        for id in invalid_ids:
            response = self.send_request(user_id=id)

            # Check that the response is a 404
            self.assertEqual(response.status_code, 404, 'Didn\'t reject: ' + str(id))

            # Check that the favourite is not added
            self.assertFalse(self.get_favs().filter(id=id).exists())
    
    def test_rejects_non_logged_in_user(self):
        """Rejects non logged in users"""

        # Log the user out
        self.client.logout()

        # Send a request to add the post to favourites
        response = self.send_request()

        # Check that it is a 403
        self.assertEqual(response.status_code, 403)

        # Check that the favourite is not added
        self.assertFalse(self.get_favs().filter(id=self.post.id).exists())
    
    def test_rejects_non_owner(self):
        """Rejects non-owner users"""

        # Create a user called fred
        self.fred2 = User.objects.create_user(
            username='fred2',
            password='SomethingExtrem31ySecure!'
        )
        self.fred2.save()

        # Log the user in
        self.client.login(username='fred2', password='SomethingExtrem31ySecure!')

        # Send a request to add the post to favourites
        response = self.send_request()

        # Check that it is a 403
        self.assertEqual(response.status_code, 403)

        # Check that the favourite is not added
        self.assertFalse(self.get_favs().filter(id=self.post.id).exists())
    
    def test_rejects_duplicate_favourite(self):
        """Rejects duplicate favourites"""

        # Add the post to favourites
        self.send_request()

        # Send a request to add the post to favourites again
        response = self.send_request()

        # Check that it is a 409
        self.assertEqual(response.status_code, 409)

        # Check that the favourite is not added
        self.assertEqual(self.get_favs().filter(id=self.post.id).count(), 1)