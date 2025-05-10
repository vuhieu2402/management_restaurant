from rest_framework import  serializers
from .models import  Cart, CartItems
from home.serializers import DishSerializer


class CartItemsSerializer(serializers.ModelSerializer):

    dish = DishSerializer(read_only=True)

    class Meta:
        model = CartItems
        fields = ['id', 'dish', 'quantity', 'total_price']

class CartSerializer(serializers.ModelSerializer):

    items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']

    def get_items(self, obj):
        """ Lấy danh sách món ăn trong giỏ hàng """
        cart_items = CartItems.objects.filter(cart=obj)
        return CartItemsSerializer(cart_items, many=True).data