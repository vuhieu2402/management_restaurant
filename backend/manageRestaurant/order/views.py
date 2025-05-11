from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ValidationError
from .serializers import OrderDetailsSerializer, OrderSerializer
from . import services


class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @action(detail=False, methods=['post'])
    def place_order(self, request):
        """
        Place a new order using cart items
        """
        if not request.user.is_authenticated:
            return Response({"error": "Bạn chưa đăng nhập!"}, status=401)

        user = request.user
        address = request.data.get('address')
        phone = request.data.get('phone')
        payment_method = request.data.get('payment_method')

        try:
            order, message = services.place_order(
                user=user,
                address=address,
                phone=phone,
                payment_method=payment_method
            )
            return Response(
                {"message": message, "order_id": order.id}, 
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Error placing order: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='history')
    def order_history(self, request):
        """
        Get order history for current user
        """
        user = request.user
        orders = services.get_user_orders(user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='manager-list')
    def manager_list_orders(self, request):
        """
        Get filtered and paginated list of orders (manager only)
        """
        user = request.user
        if not (user.is_staff or user.is_superuser):
            return Response({'detail': 'Permission denied.'}, status=403)

        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        # Get filtered orders
        orders = services.filter_orders(year=year, month=month)
        
        # Paginate results
        result_page, paginator = services.paginate_orders(orders, request)
        
        # Serialize and return
        serializer = OrderSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
        
    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        """
        Update order status (manager only)
        """
        user = request.user
        if not (user.is_staff or user.is_superuser):
            return Response({'detail': 'Permission denied.'}, status=403)
            
        status_value = request.data.get('status')
        if status_value is None:
            return Response(
                {"error": "Status value is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            order = services.update_order_status(pk, status_value)
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Error updating order: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
