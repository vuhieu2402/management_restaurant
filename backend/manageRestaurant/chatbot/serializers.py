from rest_framework import serializers
from .models import Conversation, Message, RecommendedDish, UserPreference
from home.serializers import DishSerializer

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['id', 'preference_type', 'preference_value', 'confidence']
        read_only_fields = ['id']

class RecommendedDishSerializer(serializers.ModelSerializer):
    dish = DishSerializer(read_only=True)
    
    class Meta:
        model = RecommendedDish
        fields = ['id', 'dish', 'reasoning', 'created_at', 'is_accepted']
        read_only_fields = ['id', 'created_at']

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    recommendations = RecommendedDishSerializer(many=True, read_only=True)
    preferences = UserPreferenceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'session_id', 'created_at', 'updated_at', 'messages', 'recommendations', 'preferences']
        read_only_fields = ['id', 'created_at', 'updated_at']

class ChatInputSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
    session_id = serializers.CharField(required=False, allow_blank=True)

class ChatResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    session_id = serializers.CharField()
    recommendations = RecommendedDishSerializer(many=True, required=False) 