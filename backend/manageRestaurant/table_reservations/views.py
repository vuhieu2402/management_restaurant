from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from .serializers import TableReservationSerializer
from . import services

# Create your views here.

class TableReservationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get all reservations for the current user
        """
        reservations = services.get_user_reservations(request.user)
        serializer = TableReservationSerializer(reservations, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new table reservation
        """
        serializer = TableReservationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Extract data from serializer
                name = serializer.validated_data.get('name')
                phone_number = serializer.validated_data.get('phone_number')
                table_number = serializer.validated_data.get('table_number')
                reservation_date = serializer.validated_data.get('reservation_date')
                time = serializer.validated_data.get('time')
                
                # Create reservation using service
                reservation = services.create_reservation(
                    user=request.user,
                    name=name,
                    phone_number=phone_number,
                    table_number=table_number,
                    reservation_date=reservation_date,
                    time=time
                )
                
                result_serializer = TableReservationSerializer(reservation)
                return Response(result_serializer.data, status=status.HTTP_201_CREATED)
                
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(
                    {"error": f"Error creating reservation: {str(e)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TableReservationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """
        Get a specific reservation
        """
        try:
            reservation = services.get_reservation_by_id(pk)
            # Check if the reservation belongs to the user or user is staff
            if reservation.user_id != request.user and not request.user.is_staff:
                return Response(
                    {"error": "You don't have permission to access this reservation"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
                
            serializer = TableReservationSerializer(reservation)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def put(self, request, pk):
        """
        Update a specific reservation
        """
        try:
            # Check if reservation exists and belongs to user
            reservation = services.get_reservation_by_id(pk)
            if reservation.user_id != request.user and not request.user.is_staff:
                return Response(
                    {"error": "You don't have permission to modify this reservation"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Validate input data
            serializer = TableReservationSerializer(data=request.data)
            if serializer.is_valid():
                # Update reservation
                updated_reservation = services.update_reservation(
                    reservation_id=pk,
                    name=serializer.validated_data.get('name'),
                    phone_number=serializer.validated_data.get('phone_number'),
                    table_number=serializer.validated_data.get('table_number'),
                    reservation_date=serializer.validated_data.get('reservation_date'),
                    time=serializer.validated_data.get('time')
                )
                
                result_serializer = TableReservationSerializer(updated_reservation)
                return Response(result_serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, pk):
        """
        Delete a specific reservation
        """
        try:
            # Check if reservation exists and belongs to user
            reservation = services.get_reservation_by_id(pk)
            if reservation.user_id != request.user and not request.user.is_staff:
                return Response(
                    {"error": "You don't have permission to delete this reservation"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Delete reservation
            services.delete_reservation(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminReservationView(APIView):
    """
    View for admin/staff to manage all reservations
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get all reservations (admin only)
        """
        if not request.user.is_staff:
            return Response(
                {"error": "Admin access required"}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Get date filter if provided
        date = request.query_params.get('date')
        
        if date:
            reservations = services.filter_reservations_by_date(date)
        else:
            reservations = services.get_all_reservations()
            
        serializer = TableReservationSerializer(reservations, many=True)
        return Response(serializer.data)
