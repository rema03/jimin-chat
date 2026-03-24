from django.contrib import admin
from .models import Friendship, ChatMessage

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend', 'nickname', 'created_at')
    search_fields = ('user__username', 'friend__username')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('room_name', 'sender', 'receiver', 'is_read', 'timestamp')
    list_filter = ('is_read',)