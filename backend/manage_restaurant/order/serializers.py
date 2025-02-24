from rest_framework import serializers
from .models import Order, OrderDetails


class OrderDetailsSerializer(serializers.ModelSerializer):
    dish_name = serializers.CharField(source="dish_id.name", read_only=True)
    dish_img = serializers.CharField(source="dish_id.url_img", read_only=True)

    class Meta:
        model = OrderDetails
        fields = ['dish_id', 'dish_name', 'dish_img', 'quantity', 'unit_price']

class OrderDetails(serializers.ModelSerializer):
    details = OrderDetailsSerializer(soure="orderdetails_set", many=True, readonly=True)

    class Meta:
        model = Order
        fields = ['id', 'total_price', 'order_date', 'address', 'status', 'details']