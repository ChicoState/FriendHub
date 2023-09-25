from django.test import TestCase
from .models import FriendHubUser  # Import your model here

class CreateUserTestCase(TestCase):
    def test_user_creation(self):
        instance = FriendHubUser.objects.create(username='example_username', email='example_email')
        self.assertIsInstance(instance, FriendHubUser)
        self.assertEqual(instance.username, 'example_username')
