from rest_framework import serializers
from .models import  TableReservations



class TableReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableReservations
        fields = '__all__'
        extra_kwargs = {
            'user_id': {'read_only': True}
        }
