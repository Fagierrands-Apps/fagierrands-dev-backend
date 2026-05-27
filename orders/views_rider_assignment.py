from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Order


class RiderAssignmentStatusView(APIView):
    """
    Poll this endpoint to check if a rider has been assigned to an order.
    Returns rider details once assigned.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, client=request.user)
        
        # Check if rider is assigned
        if order.assistant and order.status in ['assigned', 'in_progress', 'completed']:
            rider = order.assistant
            profile = getattr(rider, 'profile', None)
            
            return Response({
                "order_id": order.id,
                "status": order.status,
                "rider_assigned": True,
                "assigned_at": order.assigned_at,
                "rider": {
                    "id": rider.id,
                    "name": f"{rider.first_name} {rider.last_name}".strip() or rider.username,
                    "phone_number": rider.phone_number,
                    "profile_picture": profile.profile_picture if profile else None,
                    "rating": profile.rating if profile else None,
                    "is_online": rider.is_online
                }
            }, status=status.HTTP_200_OK)
        
        # No rider assigned yet
        return Response({
            "order_id": order.id,
            "status": order.status,
            "rider_assigned": False,
            "message": "Searching for available rider..."
        }, status=status.HTTP_200_OK)
