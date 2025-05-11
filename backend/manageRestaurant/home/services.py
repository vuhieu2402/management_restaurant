from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from .models import Category, Dish

# Category Services
def get_all_categories():

    return Category.objects.all()

def get_category_by_id(category_id):
 
    return get_object_or_404(Category, id=category_id)

def create_category(name, description=''):

    with transaction.atomic():
        category = Category(
            name=name,
            description=description
        )
        category.full_clean()  # Validate before saving
        category.save()
        return category

def update_category(category_id, name=None, description=None):
 
    with transaction.atomic():
        category = get_object_or_404(Category, id=category_id)
        
        if name is not None:
            category.name = name
        if description is not None:
            category.description = description
            
        category.full_clean()  # Validate before saving
        category.save()
        return category

def delete_category(category_id):

    with transaction.atomic():
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return True

# Dish Services
def get_all_dishes():

    return Dish.objects.all()

def get_dish_by_id(dish_id):
  
    return get_object_or_404(Dish, id=dish_id)

def search_dishes(query):

    return Dish.objects.filter(
        name__icontains=query
    ) | Dish.objects.filter(
        description__icontains=query
    )

def create_dish(category_id, name, description, price, url_img=None, in_stock=True):

    with transaction.atomic():
        category = get_object_or_404(Category, id=category_id)
        
        dish = Dish(
            category=category,
            name=name,
            description=description,
            price=price,
            url_img=url_img,
            in_stock=in_stock
        )
        
        dish.full_clean()  # Validate before saving
        dish.save()
        return dish

def update_dish(dish_id, **kwargs):

    with transaction.atomic():
        dish = get_object_or_404(Dish, id=dish_id)
        
        if 'category_id' in kwargs:
            category = get_object_or_404(Category, id=kwargs['category_id'])
            dish.category = category
            
        if 'name' in kwargs:
            dish.name = kwargs['name']
            
        if 'description' in kwargs:
            dish.description = kwargs['description']
            
        if 'price' in kwargs:
            dish.price = kwargs['price']
            
        if 'url_img' in kwargs:
            dish.url_img = kwargs['url_img']
            
        if 'in_stock' in kwargs:
            dish.in_stock = kwargs['in_stock']
            
        dish.full_clean()  # Validate before saving
        dish.save()
        return dish

def delete_dish(dish_id):

    with transaction.atomic():
        dish = get_object_or_404(Dish, id=dish_id)
        dish.delete()
        return True 