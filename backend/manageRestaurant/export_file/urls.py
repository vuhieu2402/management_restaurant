from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExportFileViewSet

router = DefaultRouter()
router.register(r'files', ExportFileViewSet, basename='export-file')

urlpatterns = [
    path('', include(router.urls)),
] 