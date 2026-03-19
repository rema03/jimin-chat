# chat/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # .as_view()를 삭제하고 .as_asgi()로 변경하거나, 
    # 최신 버전에서는 아래와 같이 작성합니다.
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]