"""Configuration endpoints for frontend"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from core.utils import calculate_distance, calculate_parcel_price, calculate_cargo_price

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_config(request):
    """Get frontend configuration"""
    return Response({
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_pricing(request):
    """Calculate distance and pricing between two locations"""
    try:
        pickup = request.data.get('pickup')  # "lat,lng"
        delivery = request.data.get('delivery')  # "lat,lng"
        order_type = request.data.get('type', 'parcel')  # parcel or cargo
        
        if not pickup or not delivery:
            return Response({'error': 'pickup and delivery coordinates required'}, status=400)
        
        # Parse coordinates
        pickup_lat, pickup_lng = map(float, pickup.split(','))
        delivery_lat, delivery_lng = map(float, delivery.split(','))
        
        # Calculate distance using existing utility
        distance_km = calculate_distance(pickup_lat, pickup_lng, delivery_lat, delivery_lng)
        
        # Calculate price using existing pricing functions
        if order_type == 'cargo':
            pricing = calculate_cargo_price(distance_km)
        else:
            pricing = calculate_parcel_price(distance_km)
        
        return Response({
            'distance_km': round(distance_km, 2),
            'distance_text': f"{round(distance_km, 2)} km",
            'base_fee': pricing['base_fee'],
            'distance_fee': pricing['distance_fee'],
            'total_price': int(pricing['total']),
            'type': order_type
        })
            
    except Exception as e:
        return Response({'error': str(e)}, status=500)
