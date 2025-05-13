from django.urls import path
from .views import ChatBotView, ConversationHistoryView, RecommendationFeedbackView

app_name = 'chatbot'

urlpatterns = [
    path('chat/', ChatBotView.as_view(), name='chat'),
    path('conversations/', ConversationHistoryView.as_view(), name='conversation_list'),
    path('conversations/<str:session_id>/', ConversationHistoryView.as_view(), name='conversation_detail'),
    path('recommendations/<int:recommendation_id>/feedback/', RecommendationFeedbackView.as_view(), name='recommendation_feedback'),
] 