from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('friends/', views.friend_list, name='friend_list'),
    path('room/<str:room_name>/', views.room, name='room'),
    path('add/', views.add_friend, name='add_friend'),
    path('add_ajax/', views.add_friend_ajax, name='add_friend_ajax'),
    path('nickname/', views.update_nickname, name='update_nickname'),
    path('delete/', views.delete_friend, name='delete_friend'),
    
    # [핵심 추가] 이미지 업로드를 위한 URL 경로
    path('upload_image/', views.upload_image, name='upload_image'),
]