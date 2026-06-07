from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import requests
from math import radians, sin, cos, sqrt, atan2
from .models import Location, UserLocation
from .serializers import LocationSerializer, UserLocationSerializer

@swagger_auto_schema(
    method='get',
    tags=['locations'],
    responses={200: LocationSerializer(many=True)}
)
@swagger_auto_schema(
    method='post',
    tags=['locations'],
    request_body=LocationSerializer,
    responses={201: LocationSerializer}
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def saved_locations(request):
    if request.method == 'GET':
        locations = Location.objects.filter(user=request.user)
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            location = serializer.save(user=request.user)
            
            # Set as default if requested
            if request.data.get('is_default'):
                Location.objects.filter(user=request.user).exclude(id=location.id).update(is_default=False)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    methods=['get', 'put', 'delete'],
    tags=['locations'],
    responses={200: LocationSerializer}
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def location_detail(request, location_id):
    try:
        location = Location.objects.get(id=location_id, user=request.user)
    except Location.DoesNotExist:
        return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response(LocationSerializer(location).data)
    
    elif request.method == 'PUT':
        serializer = LocationSerializer(location, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        location.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(
    method='post',
    tags=['locations'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['latitude', 'longitude'],
        properties={
            'latitude': openapi.Schema(type=openapi.TYPE_NUMBER),
            'longitude': openapi.Schema(type=openapi.TYPE_NUMBER),
        }
    ),
    responses={200: UserLocationSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_current_location(request):
    """Update user's current location (for riders)"""
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    user_location, created = UserLocation.objects.update_or_create(
        user=request.user,
        defaults={'latitude': latitude, 'longitude': longitude}
    )
    
    return Response(UserLocationSerializer(user_location).data)

@swagger_auto_schema(
    method='get',
    tags=['locations'],
    responses={200: UserLocationSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_rider_location(request, rider_id):
    """Get rider's current location for tracking"""
    try:
        location = UserLocation.objects.get(user_id=rider_id)
        return Response(UserLocationSerializer(location).data)
    except UserLocation.DoesNotExist:
        return Response({'error': 'Location not available'}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='get',
    tags=['locations'],
    manual_parameters=[
        openapi.Parameter('q', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Search query'),
        openapi.Parameter('input', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Search query (alias)'),
    ],
    responses={200: openapi.Response('Autocomplete suggestions')}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def autocomplete(request):
    """Google Maps autocomplete for address search with coordinates"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Support both 'q' and 'input' parameters for app compatibility
    query = request.query_params.get('q') or request.query_params.get('input', '')
    
    if not query:
        return Response({'suggestions': [], 'count': 0})
    
    if len(query) < 2:
        return Response({'suggestions': [], 'count': 0})
    
    api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
    if not api_key:
        logger.error("Google Maps API key not configured")
        return Response({'suggestions': [], 'count': 0, 'error': 'API not configured'})
    
    url = 'https://maps.googleapis.com/maps/api/place/autocomplete/json'
    params = {'input': query, 'key': api_key, 'components': 'country:ke'}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        result = response.json()
        
        suggestions = []
        for prediction in result.get('predictions', []):
            place_id = prediction.get('place_id')
            
            # Fetch coordinates for each place
            coords = {'lat': None, 'lng': None}
            try:
                details_url = 'https://maps.googleapis.com/maps/api/place/details/json'
                details_params = {'place_id': place_id, 'key': api_key, 'fields': 'geometry'}
                details_response = requests.get(details_url, params=details_params, timeout=3)
                details_result = details_response.json()
                
                if details_result.get('status') == 'OK':
                    location = details_result.get('result', {}).get('geometry', {}).get('location', {})
                    coords['lat'] = location.get('lat')
                    coords['lng'] = location.get('lng')
            except:
                pass
            
            suggestions.append({
                'place_id': place_id,
                'description': prediction.get('description'),
                'main_text': prediction.get('structured_formatting', {}).get('main_text', ''),
                'secondary_text': prediction.get('structured_formatting', {}).get('secondary_text', ''),
                'lat': coords['lat'],
                'lng': coords['lng'],
                'latitude': coords['lat'],
                'longitude': coords['lng']
            })
        
        return Response({'suggestions': suggestions, 'count': len(suggestions)})
        
    except Exception as e:
        logger.error(f"Autocomplete error: {str(e)}")
        return Response({'suggestions': [], 'count': 0, 'error': str(e)})


@swagger_auto_schema(
    method='post',
    tags=['locations'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['latitude', 'longitude'],
        properties={
            'latitude': openapi.Schema(type=openapi.TYPE_NUMBER),
            'longitude': openapi.Schema(type=openapi.TYPE_NUMBER),
        }
    ),
    responses={200: openapi.Response('Address details')}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def reverse_geocode(request):
    """Convert coordinates to address"""
    lat = request.data.get('latitude')
    lng = request.data.get('longitude')
    
    if not lat or not lng:
        return Response({'error': 'latitude and longitude required'}, status=status.HTTP_400_BAD_REQUEST)
    
    api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
    if not api_key:
        return Response({'error': 'Google Maps API not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'latlng': f'{lat},{lng}', 'key': api_key}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        return Response(response.json())
    except:
        return Response({'error': 'Geocoding service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@swagger_auto_schema(
    method='post',
    tags=['locations'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['origin_lat', 'origin_lng', 'dest_lat', 'dest_lng'],
        properties={
            'origin_lat': openapi.Schema(type=openapi.TYPE_NUMBER),
            'origin_lng': openapi.Schema(type=openapi.TYPE_NUMBER),
            'dest_lat': openapi.Schema(type=openapi.TYPE_NUMBER),
            'dest_lng': openapi.Schema(type=openapi.TYPE_NUMBER),
        }
    ),
    responses={200: openapi.Response('Distance and duration')}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def calculate_distance(request):
    """Calculate distance between two points"""
    origin_lat = request.data.get('origin_lat')
    origin_lng = request.data.get('origin_lng')
    dest_lat = request.data.get('dest_lat')
    dest_lng = request.data.get('dest_lng')
    
    if not all([origin_lat, origin_lng, dest_lat, dest_lng]):
        return Response({'error': 'All coordinates required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Haversine formula
    R = 6371  # Earth radius in km
    
    lat1, lon1, lat2, lon2 = map(radians, [float(origin_lat), float(origin_lng), float(dest_lat), float(dest_lng)])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance_km = R * c
    
    # Estimate duration (assuming 30km/h average in city)
    duration_minutes = int((distance_km / 30) * 60)
    
    return Response({
        'distance_km': round(distance_km, 2),
        'distance_m': round(distance_km * 1000, 0),
        'duration_minutes': duration_minutes
    })


@swagger_auto_schema(
    method='get',
    tags=['locations'],
    responses={200: openapi.Response('Map configuration')}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def map_config(request):
    """Get Google Maps configuration"""
    return Response({
        'api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
        'default_center': {
            'latitude': -1.286389,
            'longitude': 36.817223  # Nairobi
        },
        'default_zoom': 12
    })
