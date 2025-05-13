from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatRoomDetailSerializer, ChatMessageSerializer

class IsStaffOrCustomer(permissions.BasePermission):
    """
    Cho phép quản lý hoặc khách hàng truy cập phòng chat của họ
    """
    def has_object_permission(self, request, view, obj):
        # Quản lý có thể truy cập tất cả
        if request.user.is_staff:
            return True
        # Khách hàng chỉ có thể truy cập phòng của mình
        return obj.customer == request.user

class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # Quản lý thấy tất cả phòng chat
            return ChatRoom.objects.all().order_by('-updated_at')
        else:
            # Khách hàng chỉ thấy phòng của mình
            return ChatRoom.objects.filter(customer=user).order_by('-updated_at')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChatRoomDetailSerializer
        return ChatRoomSerializer
    
    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsStaffOrCustomer]
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        user = request.user
        
        # Kiểm tra xem đã có phòng chat chưa
        existing_room = ChatRoom.get_customer_room(user.id)
        if existing_room:
            serializer = self.get_serializer(existing_room)
            return Response(serializer.data)
        
        # Tạo phòng chat mới
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Gán khách hàng là người dùng hiện tại
        serializer.save(customer=user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Đánh dấu tất cả tin nhắn là đã đọc
        ChatMessage.mark_messages_as_read(instance.id, request.user.id)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        room = self.get_object()
        user = request.user
        content = request.data.get('message')
        
        if not content:
            return Response(
                {'error': 'Message content is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Lưu tin nhắn
        message = ChatMessage.objects.create(
            room=room,
            user=user,
            content=content
        )
        
        # Cập nhật thời gian cập nhật của phòng
        room.save()  # updated_at sẽ tự động cập nhật
        
        serializer = ChatMessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        user = request.user
        if user.is_staff:
            count = ChatMessage.get_unread_count_for_manager()
        else:
            count = ChatMessage.get_unread_count(user.id)
        
        return Response({'unread_count': count})

class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        room_id = self.kwargs.get('room_pk')
        room = get_object_or_404(ChatRoom, id=room_id)
        
        # Kiểm tra quyền truy cập
        if not self.request.user.is_staff and room.customer != self.request.user:
            raise PermissionDenied('You do not have permission to view these messages')
        
        return ChatMessage.objects.filter(room=room)
