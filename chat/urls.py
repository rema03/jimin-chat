from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('friends/', views.friend_list, name='friend_list'),
    path('room/<str:room_name>/', views.room, name='room'),
    path('start/<int:user_id>/', views.start_chat, name='start_chat'),
    path('add_friend/', views.add_friend, name='add_friend'),
    path('update_nickname/', views.update_nickname, name='update_nickname'),
    path('delete_friend/', views.delete_friend, name='delete_friend'),
    path('upload_image/', views.upload_image, name='upload_image'),
]
