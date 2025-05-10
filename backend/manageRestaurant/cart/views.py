from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action
from .models import Cart, CartItems
from .serializers import CartSerializer, CartItemsSerializer
from home.models import Dish

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

        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_to_cart(self, request):
        """ Thêm món ăn vào giỏ hàng """
        user = request.user
        dish_id = request.data.get('dish_id')
        quantity = request.data.get('quantity', 1)

        cart, created = Cart.objects.get_or_create(user=user)
        dish = get_object_or_404(Dish, id=dish_id)

        cart_item, created = CartItems.objects.get_or_create(
            cart=cart, dish=dish
        )
        cart_item.quantity += int(quantity)
        cart_item.save()

        return Response({"message": "Item added to cart"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def remove_from_cart(self, request):
        """ Xóa món ăn khỏi giỏ hàng """
        user = request.user
        dish_id = request.data.get('dish_id')

        cart = get_object_or_404(Cart, user=user)
        cart_item = get_object_or_404(CartItems, cart=cart, dish_id=dish_id)

        cart_item.delete()

        return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)


    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        """ Cập nhật số lượng món ăn trong giỏ hàng """
        user = request.user
        dish_id = request.data.get('dish_id')
        quantity = request.data.get('quantity')

        cart = get_object_or_404(Cart, user=user)
        cart_item = get_object_or_404(CartItems, cart=cart, dish_id=dish_id)


        if int(quantity) > 0 :
            cart_item.quantity = int(quantity)
            cart_item.save()
            return Response({"message": "Quantity updated"}, status=status.HTTP_200_OK)

        else:
            cart_item.delete()  # Xóa món nếu số lượng = 0
            return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)
