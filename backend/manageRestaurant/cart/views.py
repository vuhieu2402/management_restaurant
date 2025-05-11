from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from .serializers import CartSerializer
from .services import (
    get_user_cart,
    add_item_to_cart,
    remove_item_from_cart,
    update_item_quantity
)

class CartViewSet(viewsets.ViewSet):  # Chuyển từ ModelViewSet -> ViewSet
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]  # Đảm bảo Django nhận JWT

    def list(self, request):
        """ Lấy giỏ hàng của user đang đăng nhập """
        # print("🛠️ Authorization Header:", request.headers.get("Authorization"))
        # print("🛠️ User:", request.user)
        # print("🛠️ Authenticated:", request.user.is_authenticated)

        if not request.user or not request.user.is_authenticated:
            return Response({"detail": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        cart = get_user_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_to_cart(self, request):
        """ Thêm món ăn vào giỏ hàng """
        user = request.user
        dish_id = request.data.get('dish_id')
        quantity = request.data.get('quantity', 1)

        result = add_item_to_cart(user, dish_id, quantity)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def remove_from_cart(self, request):
        """ Xóa món ăn khỏi giỏ hàng """
        user = request.user
        dish_id = request.data.get('dish_id')

        result = remove_item_from_cart(user, dish_id)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        """ Cập nhật số lượng món ăn trong giỏ hàng """
        user = request.user
        dish_id = request.data.get('dish_id')
        quantity = request.data.get('quantity')

        result = update_item_quantity(user, dish_id, quantity)
        return Response(result, status=status.HTTP_200_OK)
