import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import ChatRoom, ChatMessage
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            self.room_group_name = f'chat_{self.room_id}'
            
            # Lấy user từ token nếu có
            self.user = self.scope.get('user', None)
            if not self.user or not self.user.is_authenticated:
                # Thử xác thực qua token trong query params
                query_string = self.scope.get('query_string', b'').decode()
                query_params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
                token = query_params.get('token', None)
                
                if token:
                    self.user = await self.get_user_from_token(token)
                    if not self.user:
                        logger.error(f"WebSocket connection rejected: Invalid token for room {self.room_id}")
                        await self.close()
                        return
            
            # Log để debug
            if self.user and self.user.is_authenticated:
                logger.info(f"WebSocket connected: User {self.user.email} (ID: {self.user.id}, Staff: {self.user.is_staff})")
            else:
                logger.warning("WebSocket connected: Anonymous user")
                await self.close()
                return
            
            # Kiểm tra quyền truy cập
            can_access = await self.can_access_room(self.room_id, self.user)
            if not can_access:
                logger.warning(f"Access denied to room {self.room_id} for user {self.user.id}")
                await self.close()
                return
            
            # Tham gia vào room
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            logger.info(f"WebSocket accepted for user {self.user.id} in room {self.room_id}")
            
            # Đánh dấu tin nhắn là đã đọc khi người dùng tham gia room
            if self.user and self.user.is_authenticated:
                await self.mark_messages_as_read(self.room_id, self.user.id)
        except Exception as e:
            logger.error(f"Error connecting to WebSocket: {str(e)}")
            await self.close()
    
    async def disconnect(self, close_code):
        # Log khi disconnect
        logger.info(f"WebSocket disconnected: code {close_code}")
        
        # Rời khỏi room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            # Xử lý heartbeat để giữ kết nối
            if message_type == 'heartbeat':
                # Chỉ cần phản hồi để giữ kết nối
                await self.send(text_data=json.dumps({
                    'type': 'system',
                    'message': 'heartbeat_ack'
                }))
                return
                
            # Xử lý các loại message khác nhau
            if message_type == 'connect':
                # Phản hồi xác nhận kết nối
                await self.send(text_data=json.dumps({
                    'type': 'system',
                    'message': 'connected',
                    'room_id': self.room_id
                }))
                logger.info(f"Connect message sent to user {self.user.id} in room {self.room_id}")
                return
                
            message = data.get('message', '')
            if not message or not self.user or not self.user.is_authenticated:
                logger.warning(f"Invalid message or unauthenticated user: {self.user.id if self.user else 'unknown'}")
                return
            
            # Lưu tin nhắn vào cơ sở dữ liệu
            chat_message = await self.save_message(self.room_id, self.user.id, message)
            logger.info(f"Message saved to database: {chat_message['id']} in room {self.room_id}")
            
            # Cập nhật thời gian cập nhật của phòng chat
            await self.update_room_timestamp(self.room_id)
            
            # Gửi tin nhắn đến group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'id': chat_message['id'],
                    'message': message,
                    'user_id': self.user.id,
                    'user_email': self.user.email,
                    'timestamp': chat_message['timestamp'].isoformat(),
                    'is_staff': self.user.is_staff
                }
            )
            logger.info(f"Message broadcast to room {self.room_id}")
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON: {text_data}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
    
    async def chat_message(self, event):
        # Gửi tin nhắn đến WebSocket
        await self.send(text_data=json.dumps({
            'id': event['id'],
            'message': event['message'],
            'user_id': event['user_id'],
            'user_email': event['user_email'],
            'timestamp': event['timestamp'],
            'is_staff': event['is_staff']
        }))
    
    @database_sync_to_async
    def get_user_from_token(self, token):
        """Lấy user từ token"""
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = User.objects.get(id=user_id)
            logger.info(f"User authenticated from token: {user.email} (ID: {user.id}, Staff: {user.is_staff})")
            return user
        except (TokenError, User.DoesNotExist) as e:
            logger.error(f"Token authentication failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in token authentication: {str(e)}")
            return None
    
    @database_sync_to_async
    def can_access_room(self, room_id, user):
        """Kiểm tra xem người dùng có quyền truy cập phòng chat không"""
        try:
            room = ChatRoom.objects.get(id=room_id)
            # Quản lý có thể truy cập tất cả phòng
            if user and user.is_authenticated and user.is_staff:
                logger.info(f"Staff access granted to room {room_id} for user {user.id}")
                return True
            # Khách hàng chỉ có thể truy cập phòng của mình
            if user and user.is_authenticated and room.customer_id == user.id:
                logger.info(f"Customer access granted to room {room_id} for user {user.id}")
                return True
            logger.warning(f"Access denied to room {room_id} for user {user.id if user else 'anonymous'}")
            return False
        except ChatRoom.DoesNotExist:
            logger.error(f"Room {room_id} does not exist")
            return False
        except Exception as e:
            logger.error(f"Error checking room access: {str(e)}")
            return False
    
    @database_sync_to_async
    def save_message(self, room_id, user_id, message):
        """Lưu tin nhắn vào cơ sở dữ liệu"""
        user = User.objects.get(id=user_id)
        room = ChatRoom.objects.get(id=room_id)
        message = ChatMessage.objects.create(
            room=room,
            user=user,
            content=message
        )
        return {
            'id': message.id,
            'content': message.content,
            'timestamp': message.timestamp
        }
    
    @database_sync_to_async
    def mark_messages_as_read(self, room_id, user_id):
        """Đánh dấu các tin nhắn trong phòng là đã đọc"""
        ChatMessage.mark_messages_as_read(room_id, user_id)
    
    @database_sync_to_async
    def update_room_timestamp(self, room_id):
        """Cập nhật thời gian cập nhật của phòng chat"""
        room = ChatRoom.objects.get(id=room_id)
        room.updated_at = timezone.now()
        room.save() 