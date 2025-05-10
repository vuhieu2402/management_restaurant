from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import  action
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from.models import Order, OrderDetails
from cart.models import Cart, CartItems
from home.models import Dish
from .serializers import OrderDetailsSerializer, OrderSerializer
from checkout.models import Payment


class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @action(detail=False, methods=['post'])
    def place_order(self, request):

        print("User gửi request:", request.user)  

        if not request.user.is_authenticated:
            return Response({"error": "Bạn chưa đăng nhập!"}, status=401)

        user = request.user
        address = request.data.get('address')
        phone = request.data.get('phone')
        payment_method = request.data.get('payment_method')

        print("📩 Dữ liệu nhận từ frontend:", request.data)

        if not address or not phone:
            return Response({"error": "Address and phone number are required"}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_object_or_404(Cart, user=user)
        cart_items = CartItems.objects.filter(cart=cart)

        if not cart_items.exists():
            return Response({"error": "No items in cart"}, status=status.HTTP_400_BAD_REQUEST)

        total_price = sum(item.quantity * item.dish.price for item in cart_items)

        # Tạo đơn hàng
        order = Order.objects.create(
            user_id=user,
            total_price=total_price,
            address=address,
            phone=phone,
            status=False
        )

        # Lưu từng món vào OrderDetails
        for item in cart_items:
            OrderDetails.objects.create(
                order_id=order,
                dish_id=item.dish,
                quantity=item.quantity,
                unit_price=item.dish.price
            )

        # Tạo thanh toán
        Payment.objects.create(
            order=order,
            payment_method=payment_method,
            status=True if payment_method == "COD" else False  # Nếu COD, thanh toán ngay
        )

        cart_items.delete()

        return Response({"message": "Order placed successfully", "order_id": order.id}, status=status.HTTP_201_CREATED)



    @action(detail=False, methods=['get'], url_path='history')
    def order_history(self, request):
        user = request.user
        orders = Order.objects.filter(user_id=user).order_by("-order_date")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='manager-list')
    def manager_list_orders(self, request):
        user = request.user
        if not (user.is_staff or user.is_superuser):
            return Response({'detail': 'Permission denied.'}, status=403)

        year = request.query_params.get('year')
        month = request.query_params.get('month')
        orders = Order.objects.all().order_by('-order_date')
        if year:
            orders = orders.filter(order_date__year=year)
        if month:
            orders = orders.filter(order_date__month=month)

        # Phân trang
        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get('page_size', 10))  # Mặc định 10 đơn/trang
        result_page = paginator.paginate_queryset(orders, request)
        serializer = OrderSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
