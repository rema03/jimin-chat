from django.test import TestCase
from django.urls import reverse

from .models import User


class AuthFlowTests(TestCase):
    def test_logout_clears_session_and_redirects_to_login(self):
        user = User.objects.create_user(username='logout-user', password='pass1234', name='로그아웃 사용자')
        self.client.login(username='logout-user', password='pass1234')

        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)
