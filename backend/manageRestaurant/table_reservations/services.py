from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from .models import TableReservations
from django.utils import timezone


def get_all_reservations():

    return TableReservations.objects.all().order_by('reservation_date', 'time')


def get_user_reservations(user):

    return TableReservations.objects.filter(user_id=user).order_by('reservation_date', 'time')


def get_reservation_by_id(reservation_id):

    return get_object_or_404(TableReservations, id=reservation_id)


def filter_reservations_by_date(date):

    return TableReservations.objects.filter(reservation_date=date).order_by('time')


@transaction.atomic
def create_reservation(user, name, phone_number, table_number, reservation_date, time):

    # Validate inputs
    if not reservation_date or not time:
        raise ValidationError("Reservation date and time are required")
    
    # Check if the date is not in the past
    today = timezone.now().date()
    if reservation_date < today:
        raise ValidationError("Reservation date cannot be in the past")
    
    # Check if requested table is already reserved for this time slot
    existing_reservations = TableReservations.objects.filter(
        reservation_date=reservation_date,
        time=time,
        table_number=table_number
    )
    
    if existing_reservations.exists():
        raise ValidationError(f"Table {table_number} is already reserved for this time slot")
    
    # Create the reservation
    reservation = TableReservations(
        user_id=user,
        name=name,
        phone_number=phone_number,
        table_number=table_number,
        reservation_date=reservation_date,
        time=time
    )
    
    reservation.full_clean()  # Validate before saving
    reservation.save()
    
    return reservation


@transaction.atomic
def update_reservation(reservation_id, **kwargs):

    reservation = get_object_or_404(TableReservations, id=reservation_id)
    
    # Check if changing table, date or time conflicts with existing reservations
    if ('table_number' in kwargs or 'reservation_date' in kwargs or 'time' in kwargs):
        new_table = kwargs.get('table_number', reservation.table_number)
        new_date = kwargs.get('reservation_date', reservation.reservation_date)
        new_time = kwargs.get('time', reservation.time)
        
        # Check for conflicts with other reservations
        conflicts = TableReservations.objects.filter(
            reservation_date=new_date,
            time=new_time,
            table_number=new_table
        ).exclude(id=reservation_id)
        
        if conflicts.exists():
            raise ValidationError(f"Table {new_table} is already reserved for this time slot")
    
    # Update fields
    for field, value in kwargs.items():
        setattr(reservation, field, value)
    
    reservation.full_clean()  # Validate before saving
    reservation.save()
    
    return reservation


@transaction.atomic
def delete_reservation(reservation_id):

    reservation = get_object_or_404(TableReservations, id=reservation_id)
    reservation.delete()
    
    return True 