"""Configuration endpoints for frontend"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
import googlemaps
from datetime import datetime

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
        pickup = request.data.get('pickup')
        delivery = request.data.get('delivery')
        
        if not pickup or not delivery:
            return Response({'error': 'pickup and delivery coordinates required'}, status=400)
        
        # Initialize Google Maps client
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        
        # Calculate distance
        result = gmaps.distance_matrix(
            origins=[pickup],
            destinations=[delivery],
            mode="driving",
            departure_time=datetime.now()
        )
        
        if result['rows'][0]['elements'][0]['status'] == 'OK':
            distance_m = result['rows'][0]['elements'][0]['distance']['value']
            distance_km = distance_m / 1000
            duration_s = result['rows'][0]['elements'][0]['duration']['value']
            duration_min = duration_s / 60
            
            # Pricing logic (KES 50 per km, minimum 200)
            base_price = 200
            price_per_km = 50
            total_price = max(base_price, distance_km * price_per_km)
            
            return Response({
                'distance_km': round(distance_km, 2),
                'distance_text': result['rows'][0]['elements'][0]['distance']['text'],
                'duration_min': round(duration_min),
                'duration_text': result['rows'][0]['elements'][0]['duration']['text'],
                'total_price': round(total_price),
                'price_breakdown': {
                    'base': base_price,
                    'per_km': price_per_km,
                    'distance_charge': round(distance_km * price_per_km)
                }
            })
        else:
            return Response({'error': 'Could not calculate distance'}, status=400)
            
    except Exception as e:
        return Response({'error': str(e)}, status=500)
