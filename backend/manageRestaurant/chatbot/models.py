from django.db import models
from user.models import NewUser
from home.models import Dish

class Conversation(models.Model):
    """Lưu trữ cuộc hội thoại giữa người dùng và chatbot"""
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)  # Cho cả người dùng đăng nhập và chưa đăng nhập
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Conversation {self.id} - {self.user.email if self.user else 'Guest'}"

class Message(models.Model):
    """Lưu trữ các tin nhắn trong cuộc trò chuyện"""
    SENDER_CHOICES = (
        ('user', 'User'),
        ('bot', 'Bot'),
    )
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender}: {self.content[:30]}..."

class RecommendedDish(models.Model):
    """Lưu trữ món ăn được đề xuất trong cuộc trò chuyện"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='recommendations')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    reasoning = models.TextField(blank=True, null=True)  # Lý do đề xuất
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(null=True)  # Người dùng chấp nhận đề xuất chưa
    
    def __str__(self):
        return f"Recommendation: {self.dish.name} for {self.conversation}"

class UserPreference(models.Model):
    """Lưu trữ thông tin về sở thích người dùng được phát hiện qua hội thoại"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='preferences')
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE, null=True, blank=True)
    preference_type = models.CharField(max_length=50)  # food_type, taste, allergy, etc.
    preference_value = models.CharField(max_length=100)
    confidence = models.FloatField(default=0.7)  # Độ tin cậy của thông tin (0-1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.preference_type}: {self.preference_value}"
