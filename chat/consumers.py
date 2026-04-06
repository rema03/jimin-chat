import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import ChatMessage
from .services import get_other_user_for_room, is_room_participant


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        if not user.is_authenticated or not is_room_participant(self.room_name, user):
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # 그룹 탈퇴
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = (data.get('message') or '').strip()
        image_url = data.get('image_url') or ''
        user = self.scope['user']

        if not user.is_authenticated or not is_room_participant(self.room_name, user):
            await self.close()
            return

        if message:
            await self.save_message(user, self.room_name, message)
        elif not image_url:
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'image_url': image_url,
                'sender': user.username
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'image_url': event['image_url'],
            'sender': event['sender']
        }))

    @database_sync_to_async
    def save_message(self, user, room_name, message):
        receiver = get_other_user_for_room(room_name, user)
        if not receiver:
            return None

        return ChatMessage.objects.create(
            sender=user,
            receiver=receiver,
            room_name=room_name,
            message=message,
        )
