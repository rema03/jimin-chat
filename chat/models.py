from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """accounts 서비스(SSO)에서 동기화되는 로컬 유저 모델"""
    name = models.CharField(max_length=50, verbose_name="이름", default="")

    def __str__(self):
        return self.username


class Friendship(models.Model):
    """유저 간 친구 관계"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friendships')
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')

    def __str__(self):
        return f"{self.user.username} -> {self.friend.username}"


class ChatMessage(models.Model):
    """채팅 메시지"""
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    room_name = models.CharField(max_length=255, db_index=True)
    message = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['room_name', '-timestamp']),
            models.Index(fields=['receiver', 'is_read']),
        ]

    def __str__(self):
        preview = self.message[:20] if self.message else '(이미지)'
        return f"[{self.room_name}] {self.sender.username}: {preview}"