from xml.etree.ElementInclude import include

from django.urls import path, include
from .views import CartViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')


urlpatterns = [
    path('api/', include(router.urls)),
]