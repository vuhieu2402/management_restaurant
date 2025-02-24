from django.shortcuts import render
from rest_framework import  viewsets
from .models import Category, Dish
from .serializers import CategorySerializer, DishSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class DishViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
