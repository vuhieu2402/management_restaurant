from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, VnpayPaymentInitView, VnpayReturnView

router = DefaultRouter()
router.register(r'payment', PaymentViewSet, basename='payment')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/vnpay_payment/', VnpayPaymentInitView.as_view(), name='vnpay_payment'),
    path('api/vnpay_return/', VnpayReturnView.as_view(), name='vnpay_return'),
]
