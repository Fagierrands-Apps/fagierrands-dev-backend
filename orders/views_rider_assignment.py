from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Order


class RiderAssignmentStatusView(APIView):
    """
    Poll this endpoint to check if a rider has been assigned to an order.
    Returns rider details once assigned.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Poll to check if a rider has been assigned to the order. Returns rider details once assigned.",
        responses={
            200: openapi.Response(
                description="Rider assignment status",
                examples={
                    "application/json": {
                        "order_id": 9,
                        "status": "assigned",
                        "rider_assigned": True,
                        "assigned_at": "2026-04-12T22:30:15.123456+03:00",
                        "rider": {
                            "id": 12,
                            "name": "John Kamau",
                            "phone_number": "0712345678",
                            "profile_picture": "http://localhost:8000/media/profiles/john.jpg",
                            "rating": 4.8,
                            "is_online": True
                        }
                    }
                }
            ),
            404: "Order not found"
        }
    )
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
