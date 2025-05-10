from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, DishViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'dishes', DishViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
