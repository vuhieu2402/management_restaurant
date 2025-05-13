from django.db import models
from django.conf import settings
from django.db.models import Q

class ChatRoom(models.Model):
    name = models.CharField(max_length=100, blank=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f'Chat with {self.customer.email}'
    
    @property
    def latest_message(self):
        return self.messages.order_by('-timestamp').first()
    
    @classmethod
    def get_customer_room(cls, user_id):
        """Lấy phòng chat của khách hàng"""
        return cls.objects.filter(customer_id=user_id).first()
    
    @classmethod
    def get_rooms_for_manager(cls):
        """Lấy tất cả phòng chat cho người quản lý"""
        return cls.objects.filter(is_active=True).order_by('-updated_at')

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='chat_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.user.email}: {self.content[:20]}'
    
    class Meta:
        ordering = ['timestamp']
    
    @classmethod
    def mark_messages_as_read(cls, room_id, user_id):
        """Đánh dấu tin nhắn đã đọc"""
        cls.objects.filter(
            room_id=room_id,
            is_read=False
        ).exclude(
            user_id=user_id
        ).update(is_read=True)
    
    @classmethod
    def get_unread_count(cls, user_id):
        """Đếm số tin nhắn chưa đọc"""
        # Với khách hàng: Đếm tin nhắn chưa đọc trong phòng của họ
        rooms = ChatRoom.objects.filter(customer_id=user_id)
        return cls.objects.filter(room__in=rooms, is_read=False).exclude(user_id=user_id).count()
    
    @classmethod 
    def get_unread_count_for_manager(cls):
        """Đếm số tin nhắn chưa đọc cho quản lý"""
        from user.models import NewUser
        # Lấy ID của tất cả quản lý
        manager_ids = NewUser.objects.filter(is_staff=True).values_list('id', flat=True)
        # Đếm tin nhắn chưa đọc từ khách hàng (không phải từ quản lý)
        return cls.objects.filter(is_read=False).exclude(user_id__in=manager_ids).count()
