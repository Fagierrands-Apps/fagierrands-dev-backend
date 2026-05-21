from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Order
from accounts.models import Profile


@swagger_auto_schema(
    method='get',
    operation_description="Get assigned rider details for an order. Returns rider name, phone, profile image, and plate number.",
    responses={
        200: openapi.Response(
            description="Rider details retrieved successfully",
            examples={
                "application/json": {
                    "assigned": True,
                    "rider": {
                        "id": 201,
                        "name": "David Omondi",
                        "phone_number": "+254745678901",
                        "profile_image": "https://example.com/image.jpg",
                        "plate_number": "KCA 123D"
                    },
                    "order_status": "assigned",
                    "assigned_at": "2026-05-21T21:10:00Z"
                }
            }
        ),
        403: "Forbidden - Not the order client",
        404: "Order not found"
    },
    tags=['Orders - Client']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assigned_rider_details(request, order_id):
    """
    Get rider details after rider has been assigned to an errand.
    Returns: name, phone number, profile image, and plate number
    """
    try:
        order = Order.objects.select_related('assistant', 'assistant__profile').get(id=order_id)
        
        # Check if user is the client
        if order.client != request.user:
            return Response(
                {"error": "You don't have permission to view this order"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if rider is assigned
        if not order.assistant:
            return Response(
                {"error": "No rider assigned yet", "assigned": False},
                status=status.HTTP_200_OK
            )
        
        rider = order.assistant
        profile = getattr(rider, 'profile', None)
        
        rider_data = {
            "assigned": True,
            "rider": {
                "id": rider.id,
                "name": f"{rider.first_name} {rider.last_name}".strip() or rider.username,
                "phone_number": rider.phone_number,
                "profile_image": profile.profile_picture_url if profile else None,
                "plate_number": profile.plate_number if profile else None,
            },
            "order_status": order.status,
            "assigned_at": order.assigned_at
        }
        
        return Response(rider_data, status=status.HTTP_200_OK)
        
    except Order.DoesNotExist:
        return Response(
            {"error": "Order not found"},
            status=status.HTTP_404_NOT_FOUND
        )
