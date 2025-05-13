from django.urls import path, re_path
from . import consumers

# Sử dụng cả re_path và path để thử các pattern khác nhau
websocket_urlpatterns = [
    # Pattern cũ - giữ để so sánh
    re_path(r'^ws/chat/(?P<room_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    
    # Pattern mới - thử phương án khác
    path('ws/chat/<int:room_id>/', consumers.ChatConsumer.as_asgi()),
] 