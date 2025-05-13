"""
ASGI config for manage_restaurant project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path, re_path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manage_restaurant.settings')

# Khởi tạo Django ASGI application trước
django_asgi_app = get_asgi_application()

# Import các routing sau khi đã thiết lập Django settings
import live_chat.routing
import live_chat.consumers

# Cấu hình Channels routing
application = ProtocolTypeRouter({
    # Django's ASGI application để xử lý HTTP requests
    "http": django_asgi_app,
    
    # WebSocket handler với xác thực
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                # Thêm trực tiếp pattern ở đây để debug - thử nhiều pattern khác nhau
                [
                    # Thêm nhiều mẫu URL để đảm bảo kết nối thành công
                    path('ws/chat/<int:room_id>', live_chat.consumers.ChatConsumer.as_asgi()),
                    path('ws/chat/<int:room_id>/', live_chat.consumers.ChatConsumer.as_asgi()),
                    re_path(r'^ws/chat/(?P<room_id>\d+)$', live_chat.consumers.ChatConsumer.as_asgi()),
                    re_path(r'^ws/chat/(?P<room_id>\d+)/$', live_chat.consumers.ChatConsumer.as_asgi()),
                ] + live_chat.routing.websocket_urlpatterns
            )
        )
    ),
})
