from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CustomUserSerializer, ResetPasswordSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from . import services


# Create your views here.

class CustomUserCreate(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format='json'):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Tạo user
                user = services.create_user(
                    email=serializer.validated_data['email'],
                    user_name=serializer.validated_data['user_name'],
                    password=serializer.validated_data['password'],
                    is_active=False  # Chưa kích hoạt
                )
                
                # Tạo token xác thực
                token = services.create_verification_token(user)

                # Tạo link xác thực
                current_site = get_current_site(request).domain
                
                # Gửi email xác thực
                services.send_verification_email(user, current_site, token.token)

                return Response(
                    {"message": "Registration successful. Please check your email to verify your account."},
                    status=status.HTTP_201_CREATED
                )
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            # Xác thực user
            user = services.verify_user(token)
            return Response(
                {"message": "Account verified successfully. You can now log in."}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


User = get_user_model()

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email')
            user = services.get_user_by_email(email)

            # Tạo token reset password
            uid, token = services.generate_password_reset_token(user)
            reset_url = f"http://127.0.0.1:3000/reset-password/{uid}/{token}/"

            # Gửi email reset password
            services.send_password_reset_email(user, reset_url)

            return Response(
                {"message": "Password reset email has been sent."}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, uidb64, token):
        # Xác thực token
        user = services.verify_password_reset_token(uidb64, token, User)
        if not user:
            return Response(
                {"error": "Invalid link"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Đặt lại mật khẩu
                services.reset_user_password(user, serializer.validated_data["password"])
                return Response(
                    {"message": "Password has been reset successfully."}, 
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {"error": str(e)}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlacklistTokenUpdateView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = ()

    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()  # Mark the token as blacklisted
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


# API trả về thông tin user hiện tại
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_me(request):
    # Sử dụng service để lấy thông tin user
    user_info = services.get_user_info(request.user)
    return Response(user_info)


# API doanh thu 12 tháng gần nhất
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_revenue(request):
    # Chỉ cho phép staff hoặc superuser
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'detail': 'Permission denied.'}, status=403)
    
    # Sử dụng service để lấy dữ liệu doanh thu
    data = services.get_monthly_revenue()
    return Response(data)


# API thống kê user theo vai trò
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_user_stats(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'detail': 'Permission denied.'}, status=403)
    
    # Sử dụng service để lấy thống kê users
    data = services.get_user_stats()
    return Response(data)