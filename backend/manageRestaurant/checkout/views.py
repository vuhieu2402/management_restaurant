from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, status
from .models import Payment
from .serializers import PaymentSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.conf import settings
from rest_framework.views import APIView
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import hashlib
import hmac
import urllib.parse
from order.models import Order

class PaymentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        payment = Payment.objects.get(order_id=pk)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)

class VnpayPaymentInitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        amount = request.data.get('amount')
        if not order_id or not amount:
            return Response({'error': 'order_id and amount required'}, status=400)
        try:
            order = Order.objects.get(id=order_id, user_id=request.user.id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)
        # Tạo Payment nếu chưa có
        payment, created = Payment.objects.get_or_create(order=order)
        payment.payment_method = 'ONLINE'
        payment.status = True  # Đánh dấu đã thanh toán thành công khi trả về link VNPay
        payment.save()

        vnp_TmnCode = settings.VNPAY_TMN_CODE
        vnp_HashSecret = settings.VNPAY_HASH_SECRET_KEY
        vnp_Url = settings.VNPAY_PAYMENT_URL
        vnp_Returnurl = settings.VNPAY_RETURN_URL
        print(f"VNPAY RETURN URL: '{vnp_Returnurl}'")
        vnp_Params = {
            'vnp_Version': '2.1.0',
            'vnp_Command': 'pay',
            'vnp_TmnCode': vnp_TmnCode,
            'vnp_Amount': str(int(round(float(amount) * 100))),
            'vnp_CurrCode': 'VND',
            'vnp_TxnRef': str(order_id),
            'vnp_OrderInfo': f'Thanh toan don hang {order_id}',
            'vnp_OrderType': 'other',
            'vnp_Locale': 'vn',
            'vnp_ReturnUrl': vnp_Returnurl,
            'vnp_IpAddr': request.META.get('REMOTE_ADDR'),
            'vnp_CreateDate': timezone.now().strftime('%Y%m%d%H%M%S'),
        }
        # Sắp xếp tham số theo key, KHÔNG encode value khi tạo hashdata
        sorted_params = sorted(vnp_Params.items())
        hashdata = '&'.join([f"{k}={v}" for k, v in sorted_params])
        secure_hash = hmac.new(vnp_HashSecret.encode(), hashdata.encode(), hashlib.sha512).hexdigest()
        # Tạo query string (có encode value)
        queryString = urllib.parse.urlencode(sorted_params)
        print(f"VNPay DEBUG | amount: {amount}")
        print(f"VNPay DEBUG | hashdata: {hashdata}")
        print(f"VNPay DEBUG | secure_hash: {secure_hash}")
        print(f"VNPay DEBUG | queryString: {queryString}")
        payment_url = f"{vnp_Url}?{queryString}&vnp_SecureHash={secure_hash}"
        print(f"VNPay DEBUG | payment_url: {payment_url}")
        return Response({'payment_url': payment_url})

@method_decorator(csrf_exempt, name='dispatch')
class VnpayReturnView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        inputData = request.GET.dict()
        vnp_HashSecret = settings.VNPAY_HASH_SECRET_KEY
        vnp_SecureHash = inputData.pop('vnp_SecureHash', None)
        inputData.pop('vnp_SecureHashType', None)
        inputData = dict(sorted(inputData.items()))
        hashdata = '&'.join([f"{k}={v}" for k, v in inputData.items()])
        secure_hash = hmac.new(vnp_HashSecret.encode(), hashdata.encode(), hashlib.sha512).hexdigest()
        if secure_hash == vnp_SecureHash:
            # Thành công
            order_id = inputData.get('vnp_TxnRef')
            transaction_id = inputData.get('vnp_TransactionNo')
            try:
                order = Order.objects.get(id=order_id)
                payment = Payment.objects.get(order=order)
                payment.status = True
                payment.transaction_id = transaction_id
                payment.save()
            except (Order.DoesNotExist, Payment.DoesNotExist):
                return Response({'error': 'Order or Payment not found'}, status=404)
            # Có thể redirect về trang thành công
            return Response({'message': 'Thanh toán thành công'})
        else:
            return Response({'error': 'Xác thực VNPay thất bại'}, status=400)
