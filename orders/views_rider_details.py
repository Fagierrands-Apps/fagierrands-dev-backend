from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Order

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assigned_rider_details(request, order_id):
    """
    Get assigned rider details for an order.
    Only accessible by the order's client.
    Returns rider info including plate number, phone, bike details, and profile.
    """
    order = get_object_or_404(Order, id=order_id)
    
    # Verify requester is the order's client
    if order.client != request.user:
        return Response(
            {"error": "You don't have permission to view this order's rider details"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if order has an assigned rider
    if not order.assistant:
        return Response(
            {"error": "No rider assigned to this order yet"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check order status - only show rider details if assigned or later
    if order.status not in ['assigned', 'in_progress', 'completed']:
        return Response(
            {"error": "Rider details not available for this order status"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    rider = order.assistant
    profile = getattr(rider, 'profile', None)
    verification = getattr(rider, 'verification', None)
    
    # Calculate rider stats
    completed_orders = Order.objects.filter(
        assistant=rider,
        status='completed'
    ).count()
    
    # Calculate average rating
    from django.db.models import Avg
    avg_rating = Order.objects.filter(
        assistant=rider,
        review__isnull=False
    ).aggregate(Avg('review__rating'))['review__rating__avg'] or 0
    
    rider_data = {
        "rider": {
            "id": rider.id,
            "name": rider.get_full_name() or rider.username,
            "phone_number": rider.phone_number,
            "profile_picture": profile.profile_picture_url if profile else None,
            "rating": round(avg_rating, 1) if avg_rating else 0,
            "completed_orders": completed_orders,
            "bike_details": {
                "plate_number": profile.plate_number if profile else None,
                "bike_type": profile.bike_type if profile else None,
                "bike_color": profile.bike_color if profile else None,
            }
        },
        "order_status": order.status,
        "assigned_at": order.assigned_at
    }
    
    return Response(rider_data, status=status.HTTP_200_OK)
