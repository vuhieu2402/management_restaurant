from user.models import NewUser
from order.models import Order, OrderDetails
from cart.models import Cart, CartItems
from checkout.models import Payment
from table_reservations.models import TableReservations
from django.utils import timezone
from datetime import date, time

# Tạo user mẫu
user1 = NewUser.objects.create_user(email="manager1@example.com", user_name="manager1", first_name="Manager", password="12345678", is_active=True, is_staff=True)
user2 = NewUser.objects.create_user(email="user1@example.com", user_name="user1", first_name="User", password="12345678", is_active=True)
user3 = NewUser.objects.create_user(email="user2@example.com", user_name="user2", first_name="User", password="12345678", is_active=True)

# Tạo cart cho user2
cart2 = Cart.objects.create(user=user2)
# Tạo cart cho user3
cart3 = Cart.objects.create(user=user3)

# Sinh nhiều dữ liệu Order, Payment, TableReservations
from random import randint, choice
from datetime import timedelta

order_objs = []
payment_methods = ['COD', 'ONLINE']
addresses = ["Hà Nội", "HCM", "Đà Nẵng", "Cần Thơ", "Hải Phòng"]
phones = ["0123456789", "0987654321", "0911222333", "0909090909", "0933444555"]

for i in range(50):
    user = user2 if i % 2 == 0 else user3
    price = randint(100000, 500000)
    status = True if i % 3 != 0 else False
    order_date = timezone.now() - timedelta(days=randint(0, 365))
    order = Order.objects.create(
        user_id=user,
        total_price=price,
        phone=choice(phones),
        address=choice(addresses),
        status=status,
        order_date=order_date
    )
    order_objs.append(order)
    # Payment cho order
    method = choice(payment_methods)
    Payment.objects.create(order=order, payment_method=method, status=status, transaction_id=f'TXN{i:04d}' if method=="ONLINE" else None)

# Sinh nhiều dữ liệu đặt bàn
for i in range(50):
    user = user2 if i % 2 == 0 else user3
    name = f"User {2 if user==user2 else 3} - {i}"
    phone = choice(phones)
    table_number = randint(1, 10)
    reservation_date = date.today() - timedelta(days=randint(0, 60))
    reservation_time = time(randint(10, 21), choice([0, 15, 30, 45]))
    TableReservations.objects.create(
        user_id=user,
        name=name,
        phone_number=phone,
        table_number=table_number,
        reservation_date=reservation_date,
        time=reservation_time
    )

print("Đã tạo dữ liệu mẫu cho các bảng (trừ Dish)")
