from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import ChatMessage
from .services import build_room_name


class ChatFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='jimin', password='pass1234', name='지민')
        self.other_user = User.objects.create_user(username='friend-user', password='pass1234', name='친구')
        self.third_user = User.objects.create_user(username='min', password='pass1234', name='다른 사용자')

    def test_start_chat_uses_id_based_room_name(self):
        self.client.login(username='jimin', password='pass1234')

        response = self.client.get(reverse('chat:start_chat', args=[self.other_user.id]))

        self.assertRedirects(response, reverse('chat:room', args=[build_room_name(self.user, self.other_user)]))

    def test_start_chat_reuses_existing_room_name(self):
        legacy_room_name = 'friend-user_jimin'
        ChatMessage.objects.create(
            sender=self.user,
            receiver=self.other_user,
            room_name=legacy_room_name,
            message='안녕',
        )
        self.client.login(username='jimin', password='pass1234')

        response = self.client.get(reverse('chat:start_chat', args=[self.other_user.id]))

        self.assertRedirects(response, reverse('chat:room', args=[legacy_room_name]))

    def test_room_blocks_similar_username_not_actual_participant(self):
        room_name = build_room_name(self.user, self.other_user)
        self.client.login(username='min', password='pass1234')

        response = self.client.get(reverse('chat:room', args=[room_name]))

        self.assertEqual(response.status_code, 403)
