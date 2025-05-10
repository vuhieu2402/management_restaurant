from django.urls import path
from .views import TableReservationView

urlpatterns = [
    path('reserve/', TableReservationView.as_view(), name='table_reservation'),
]
