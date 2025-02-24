from django.db import models
from user.models import NewUser
from home.models import Dish

class Cart(models.Model):
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE)

class CartItems(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def total_price(self):
        return self.quantity * self.dish.price

    def __str__(self):
        return f"{self.quantity} x {self.dish.name} in cart"


