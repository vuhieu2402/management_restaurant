from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from .models import Category, Dish
from .serializers import CategorySerializer, DishSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from . import services

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    
    def get_queryset(self):
        return services.get_all_categories()
    
    def retrieve(self, request, pk=None):
        category = services.get_category_by_id(pk)
        serializer = self.get_serializer(category)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        category = services.create_category(
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description', '')
        )
        
        result_serializer = self.get_serializer(category)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        category = services.update_category(
            category_id=pk,
            name=serializer.validated_data.get('name'),
            description=serializer.validated_data.get('description')
        )
        
        result_serializer = self.get_serializer(category)
        return Response(result_serializer.data)
    
    def destroy(self, request, pk=None):
        services.delete_category(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

class DishViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = DishSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        queryset = services.get_all_dishes()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = services.search_dishes(search_query)
        return queryset
    
    def retrieve(self, request, pk=None):
        dish = services.get_dish_by_id(pk)
        serializer = self.get_serializer(dish)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        dish = services.create_dish(
            category_id=serializer.validated_data['category'].id,
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description', ''),
            price=serializer.validated_data['price'],
            url_img=serializer.validated_data.get('url_img'),
            in_stock=serializer.validated_data.get('in_stock', True)
        )
        
        result_serializer = self.get_serializer(dish)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        kwargs = {}
        if 'category' in serializer.validated_data:
            kwargs['category_id'] = serializer.validated_data['category'].id
        if 'name' in serializer.validated_data:
            kwargs['name'] = serializer.validated_data['name']
        if 'description' in serializer.validated_data:
            kwargs['description'] = serializer.validated_data['description']
        if 'price' in serializer.validated_data:
            kwargs['price'] = serializer.validated_data['price']
        if 'url_img' in serializer.validated_data:
            kwargs['url_img'] = serializer.validated_data['url_img']
        if 'in_stock' in serializer.validated_data:
            kwargs['in_stock'] = serializer.validated_data['in_stock']
        
        dish = services.update_dish(pk, **kwargs)
        
        result_serializer = self.get_serializer(dish)
        return Response(result_serializer.data)
    
    def destroy(self, request, pk=None):
        services.delete_dish(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
