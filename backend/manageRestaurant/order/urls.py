from xml.etree.ElementInclude import include

from django.urls import path, include
from .views import OrderViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'order',OrderViewSet, basename='order')


urlpatterns = [
    path('api/', include(router.urls)),
]