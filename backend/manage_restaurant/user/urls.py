from django.urls import path
from .views import CustomUserCreate, BlacklistTokenUpdateView, VerifyEmailView, ForgotPasswordView, ResetPasswordView



app_name = 'user'

urlpatterns = [
    path('register/', CustomUserCreate.as_view(), name='register'),
    path('logout/blacklist/', BlacklistTokenUpdateView.as_view(), name='blacklist'),
    path("verify/<uuid:token>/", VerifyEmailView.as_view(), name="verify_email"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password/<uidb64>/<token>/", ResetPasswordView.as_view(), name="reset_password"),
]