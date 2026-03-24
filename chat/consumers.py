import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatMessage
from accounts.models import User


def get_other_username(room_name, current_username):
    participants = room_name.split('_')
    if len(participants) != 2 or current_username not in participants:
        return None
    return participants[1] if participants[0] == current_username else participants[0]


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        other_username = get_other_username(self.room_name, getattr(user, 'username', ''))

        if not user.is_authenticated or not other_username:
            await self.close()
            return

        # 그룹 참여
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
        message = data.get('message', '')
        image_url = data.get('image_url', '')
        user = self.scope['user']

        if not user.is_authenticated:
            return

        # 이미지는 upload_image 뷰에서 저장하므로 여기서는 텍스트 메시지만 저장
        if message:
            await self.save_message(user, self.room_name, message)

        # 그룹에 메시지 전송
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
        # WebSocket으로 메시지 전송
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'image_url': event['image_url'],
            'sender': event['sender']
        }))

    @database_sync_to_async
    def save_message(self, user, room_name, message):
        other_username = get_other_username(room_name, user.username)
        if not other_username:
            return None

        try:
            receiver = User.objects.get(username=other_username)
            return ChatMessage.objects.create(
                sender=user,
                receiver=receiver,
                room_name=room_name,
                message=message,
            )
        except User.DoesNotExist:
            return None
