from django.contrib import admin
from django.urls import path, include
from rest_framework import  permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from user.views import VerifyEmailView

schema_view = get_schema_view(
    openapi.Info(
        title="Manage Restaurant API",
        default_version='v1',
        description="API for managing restaurant operations",
        terms_of_service="https://example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/verify/<uuid:token>/', VerifyEmailView.as_view(), name='direct_verify_email'),
    path('api/user/',include('user.urls', namespace='user')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('',include('home.urls')),
    path('',include('cart.urls')),
    path('',include('order.urls')),
    path('',include('checkout.urls')),
    path('',include('table_reservations.urls')),
]
