from django.db import models
from order.models import Order

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('COD', 'Cash on delivery'),
        ('ONLINE', 'Online payment'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    payment_method = models.CharField(max_length=8, choices=PAYMENT_METHODS, default='COD')
    status = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order_id} - {self.payment_method}"

