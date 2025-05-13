from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from .serializers import (
    ChatInputSerializer, 
    ChatResponseSerializer, 
    ConversationSerializer, 
    MessageSerializer, 
    RecommendedDishSerializer
)
from .services import process_chat_message, mark_recommendation_feedback
from .models import Conversation, RecommendedDish

class ChatBotView(APIView):
    """
    API cho tương tác với chatbot
    """
    permission_classes = [AllowAny]  # Cho phép cả người dùng đăng nhập và chưa đăng nhập
    
    def post(self, request):
        """
        Xử lý tin nhắn gửi đến chatbot
        """
        serializer = ChatInputSerializer(data=request.data)
        if serializer.is_valid():
            # Lấy thông tin từ request
            user_message = serializer.validated_data['message']
            session_id = serializer.validated_data.get('session_id', None)
            user = request.user if request.user.is_authenticated else None
            
            # Xử lý tin nhắn
            result = process_chat_message(user_message, session_id, user)
            
            # Trả về phản hồi
            response_serializer = ChatResponseSerializer({
                'message': result['message'],
                'session_id': result['session_id'],
                'recommendations': result['recommendations']
            })
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConversationHistoryView(APIView):
    """
    API để lấy lịch sử cuộc trò chuyện
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, session_id=None):
        """
        Lấy lịch sử cuộc trò chuyện theo session_id
        """
        user = request.user
        
        if session_id:
            # Lấy cuộc trò chuyện cụ thể
            try:
                conversation = Conversation.objects.get(session_id=session_id)
                # Kiểm tra quyền truy cập
                if conversation.user and conversation.user != user:
                    return Response(
                        {"error": "You don't have permission to access this conversation"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                serializer = ConversationSerializer(conversation)
                return Response(serializer.data)
            except Conversation.DoesNotExist:
                return Response(
                    {"error": "Conversation not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Lấy tất cả cuộc trò chuyện của người dùng
            conversations = Conversation.objects.filter(user=user).order_by('-updated_at')
            serializer = ConversationSerializer(conversations, many=True)
            return Response(serializer.data)


class RecommendationFeedbackView(APIView):
    """
    API để cung cấp phản hồi về đề xuất món ăn
    """
    permission_classes = [AllowAny]  # Cho phép cả người dùng đăng nhập và chưa đăng nhập
    
    def post(self, request, recommendation_id):
        """
        Đánh dấu đề xuất món ăn là được chấp nhận hoặc từ chối
        """
        accepted = request.data.get('accepted')
        if accepted is None:
            return Response(
                {"error": "Missing 'accepted' parameter"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = mark_recommendation_feedback(recommendation_id, accepted)
        
        if success:
            return Response({"status": "success"})
        else:
            return Response(
                {"error": "Recommendation not found"},
                status=status.HTTP_404_NOT_FOUND
            )
