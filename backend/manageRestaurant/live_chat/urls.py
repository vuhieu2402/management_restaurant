from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from . import views

router = DefaultRouter()
router.register(r'rooms', views.ChatRoomViewSet, basename='chatroom')

# Nested router cho messages trong room
rooms_router = NestedDefaultRouter(router, r'rooms', lookup='room')
rooms_router.register(r'messages', views.ChatMessageViewSet, basename='chatmessage')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(rooms_router.urls)),
] 