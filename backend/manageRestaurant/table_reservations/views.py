from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TableReservationSerializer
from rest_framework.permissions import IsAuthenticated

# Create your views here.

class TableReservationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TableReservationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_id=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
