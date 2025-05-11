from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Cart, CartItems
from home.models import Dish


def get_user_cart(user):

    with transaction.atomic():
        cart, created = Cart.objects.get_or_create(user=user)
        return cart


def add_item_to_cart(user, dish_id, quantity=1):

    with transaction.atomic():
        cart, created = Cart.objects.get_or_create(user=user)
        dish = get_object_or_404(Dish, id=dish_id)
        
        cart_item, created = CartItems.objects.get_or_create(
            cart=cart, dish=dish
        )
        cart_item.quantity += int(quantity)
        cart_item.save()
        
        return {"message": "Item added to cart"}


def remove_item_from_cart(user, dish_id):

    with transaction.atomic():
        cart = get_object_or_404(Cart, user=user)
        cart_item = get_object_or_404(CartItems, cart=cart, dish_id=dish_id)
        cart_item.delete()
        
        return {"message": "Item removed from cart"}


def update_item_quantity(user, dish_id, quantity):

    with transaction.atomic():
        cart = get_object_or_404(Cart, user=user)
        cart_item = get_object_or_404(CartItems, cart=cart, dish_id=dish_id)
        
        if int(quantity) > 0:
            cart_item.quantity = int(quantity)
            cart_item.save()
            return {"message": "Quantity updated"}
        else:
            cart_item.delete()  # Remove item if quantity is 0
            return {"message": "Item removed from cart"} 