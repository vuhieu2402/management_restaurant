from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import  action
from rest_framework_simplejwt.authentication import JWTAuthentication
from.models import Order, OrderDetails
from cart.models import Cart, CartItems
from home.models import Dish
from .serializers import OrderDetailsSerializer


class OrderViewSet(viewsets.ViewSet):
    
