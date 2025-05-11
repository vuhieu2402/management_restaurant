from django.urls import path
from .views import TableReservationView, TableReservationDetailView, AdminReservationView

urlpatterns = [
    path('reserve/', TableReservationView.as_view(), name='table_reservation'),
    path('reserve/<int:pk>/', TableReservationDetailView.as_view(), name='table_reservation_detail'),
    path('admin/reserve/', AdminReservationView.as_view(), name='admin_reservations'),
]
