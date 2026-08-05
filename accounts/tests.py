from django.test import TestCase
from .models import User


class UserModelTests(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(username='testuser', email='test@jimindev.com', name='테스트')
        self.assertEqual(user.name, '테스트')
        self.assertEqual(str(user), 'testuser')
