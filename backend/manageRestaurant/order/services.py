from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from .models import Order, OrderDetails
from cart.models import Cart, CartItems
from home.models import Dish
from checkout.models import Payment
from django.db.models import Sum, F, Q
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination


def get_user_orders(user):

    return Order.objects.filter(user_id=user).order_by("-order_date")


def get_order_details(order_id):
 
    return get_object_or_404(Order, id=order_id)


def filter_orders(year=None, month=None):

    orders = Order.objects.all().order_by('-order_date')
    
    if year:
        orders = orders.filter(order_date__year=year)
    if month:
        orders = orders.filter(order_date__month=month)
    
    return orders


def paginate_orders(orders, request):

    paginator = PageNumberPagination()
    paginator.page_size = int(request.query_params.get('page_size', 10))
    result_page = paginator.paginate_queryset(orders, request)
    
    return result_page, paginator


@transaction.atomic
def place_order(user, address, phone, payment_method):
 
    # Validate inputs
    if not address or not phone:
        raise ValidationError("Address and phone number are required")
    
    # Get cart items
    cart = get_object_or_404(Cart, user=user)
    cart_items = CartItems.objects.filter(cart=cart)
    
    if not cart_items.exists():
        raise ValidationError("No items in cart")
    
    # Calculate total price
    total_price = sum(item.quantity * item.dish.price for item in cart_items)
    
    # Create order
    order = Order.objects.create(
        user_id=user,
        total_price=total_price,
        address=address,
        phone=phone,
        status=False
    )
    
    # Create order details
    for item in cart_items:
        OrderDetails.objects.create(
            order_id=order,
            dish_id=item.dish,
            quantity=item.quantity,
            unit_price=item.dish.price
        )
    
    # Create payment record
    Payment.objects.create(
        order=order,
        payment_method=payment_method,
        status=True if payment_method == "COD" else False
    )
    
    # Clear cart
    cart_items.delete()
    
    return order, "Order placed successfully"


@transaction.atomic
def update_order_status(order_id, status):
  
    order = get_object_or_404(Order, id=order_id)
    order.status = status
    order.save()
    
    return order 