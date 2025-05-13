from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatMessage

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'user_name', 'is_staff']

class ChatMessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'user', 'content', 'timestamp', 'is_read']

class ChatRoomSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    latest_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'customer', 'created_at', 'updated_at', 'is_active', 'latest_message', 'unread_count']
    
    def get_latest_message(self, obj):
        latest = obj.latest_message
        if latest:
            return {
                'content': latest.content,
                'timestamp': latest.timestamp,
                'is_read': latest.is_read,
                'user_id': latest.user.id if latest.user else None
            }
        return None
    
    def get_unread_count(self, obj):
        return obj.messages.filter(is_read=False).exclude(user=self.context.get('request').user).count()

class ChatRoomDetailSerializer(ChatRoomSerializer):
    messages = ChatMessageSerializer(many=True, source='messages.all')
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'customer', 'created_at', 'updated_at', 'is_active', 'messages', 'unread_count'] 