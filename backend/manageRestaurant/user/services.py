from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from .models import NewUser, VerificationToken
from order.models import Order


def get_user_by_email(email):

    return get_object_or_404(NewUser, email=email)


def get_user_by_id(user_id):

    return get_object_or_404(NewUser, id=user_id)


def get_user_info(user):

    return {
        "id": user.id,
        "email": user.email,
        "user_name": getattr(user, "user_name", ""),
        "first_name": getattr(user, "first_name", ""),
        "is_superuser": user.is_superuser,
        "is_staff": user.is_staff,
        "is_active": user.is_active,
    }


@transaction.atomic
def create_user(email, user_name, password, first_name="", is_active=False):

    # Validate input data
    if not email:
        raise ValidationError("Email is required")
    if not user_name:
        raise ValidationError("Username is required")
    if not password or len(password) < 8:
        raise ValidationError("Password must be at least 8 characters")
    
    # Check if email or username already exists
    if NewUser.objects.filter(email=email).exists():
        raise ValidationError("Email already exists")
    if NewUser.objects.filter(user_name=user_name).exists():
        raise ValidationError("Username already exists")
    
    # Create user
    user = NewUser(
        email=email,
        user_name=user_name,
        first_name=first_name,
        is_active=is_active
    )
    user.set_password(password)
    user.full_clean()
    user.save()
    
    return user


@transaction.atomic
def create_verification_token(user):

    # Delete existing token if any
    VerificationToken.objects.filter(user=user).delete()
    
    # Create new token
    token = VerificationToken.objects.create(user=user)
    return token


@transaction.atomic
def verify_user(token):

    verification_token = get_object_or_404(VerificationToken, token=token)
    user = verification_token.user
    
    # Activate user
    user.is_active = True
    user.save()
    
    # Delete token
    verification_token.delete()
    
    return user


def send_verification_email(user, site_domain, token):

    verification_url = f"http://{site_domain}/api/verify/{token}/"
    
    send_mail(
        "Verify your account",
        f"Click the link to verify your account: {verification_url}",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def generate_password_reset_token(user):

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return uid, token


def send_password_reset_email(user, reset_url):

    send_mail(
        "Password Reset Request",
        f"Click the link to reset your password: {reset_url}",
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )


@transaction.atomic
def reset_user_password(user, password):

    user.set_password(password)
    user.save()
    return user


def verify_password_reset_token(uidb64, token, user_model):

    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64)).decode()
        user = user_model.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        return None
    
    if default_token_generator.check_token(user, token):
        return user
    
    return None


def get_monthly_revenue():

    today = datetime.today()
    months = []
    for i in range(11, -1, -1):
        month = (today.replace(day=1) - timedelta(days=30 * i)).strftime('%Y-%m')
        months.append(month)
    
    data = []
    for m in months:
        year, month = map(int, m.split('-'))
        revenue = Order.objects.filter(
            order_date__year=year,
            order_date__month=month,
            status=True
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        data.append({"month": f"{year}-{month:02d}", "revenue": float(revenue)})
    
    return data


def get_user_stats():

    total = NewUser.objects.count()
    staff = NewUser.objects.filter(is_staff=True).count()
    superuser = NewUser.objects.filter(is_superuser=True).count()
    active = NewUser.objects.filter(is_active=True, is_staff=False, is_superuser=False).count()
    
    data = [
        {"role": "Total", "count": total},
        {"role": "Staff", "count": staff},
        {"role": "Superuser", "count": superuser},
        {"role": "Active User", "count": active},
    ]
    
    return data 