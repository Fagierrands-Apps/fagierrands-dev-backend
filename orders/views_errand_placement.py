from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderType
from locations.models import Location
from geopy.distance import geodesic
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_errand_price(request):
    """Calculate price for errand"""
    pickup_lat = request.data.get('pickup_latitude')
    pickup_lng = request.data.get('pickup_longitude')
    dropoff_lat = request.data.get('dropoff_latitude')
    dropoff_lng = request.data.get('dropoff_longitude')
    errand_type = request.data.get('errand_type', 'parcel')
    shopping_amount = float(request.data.get('shopping_amount', 0))
    is_emergency = request.data.get('is_emergency', False)
    
    if not all([pickup_lat, pickup_lng, dropoff_lat, dropoff_lng]):
        return Response({'error': 'Missing coordinates'}, status=400)
    
    # Calculate distance
    distance = geodesic((pickup_lat, pickup_lng), (dropoff_lat, dropoff_lng)).km
    
    # Calculate price based on type
    if errand_type == 'parcel':
        base = 200
        if distance > 7.5:
            distance_fee = (distance - 7.5) * 23
        else:
            distance_fee = 0
        total = base + distance_fee
    elif errand_type == 'cargo':
        base = 500
        if distance > 7:
            distance_fee = (distance - 7) * 28
        else:
            distance_fee = 0
        total = base + distance_fee
    else:  # shopping
        base = 200
        if distance > 7.5:
            distance_fee = (distance - 7.5) * 23
        else:
            distance_fee = 0
        service_fee = 200 + max(0, (shopping_amount - 5000) / 5000) * 50
        total = base + distance_fee + service_fee
    
    if is_emergency:
        total += 50
    
    return Response({
        'distance_km': round(distance, 2),
        'total_price': round(total, 2),
        'upfront_payment': round(total if errand_type != 'shopping' else shopping_amount * 0.3, 2)
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_price_with_route(request):
    """Calculate price with route details"""
    return calculate_errand_price(request)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_draft_errand(request):
    """Create draft errand order"""
    user = request.user
    
    try:
        # Get or create locations
        pickup_loc, _ = Location.objects.get_or_create(
            latitude=request.data['pickup_latitude'],
            longitude=request.data['pickup_longitude'],
            user=user,
            defaults={'name': request.data.get('pickup_location_name', 'Pickup')}
        )
        
        delivery_loc, _ = Location.objects.get_or_create(
            latitude=request.data['delivery_latitude'],
            longitude=request.data['delivery_longitude'],
            user=user,
            defaults={'name': request.data.get('delivery_location_name', 'Delivery')}
        )
        
        # Get order type
        errand_type = request.data.get('errand_type', 'parcel')
        type_map = {'parcel': 1, 'cargo': 2, 'shopping': 3}
        order_type = OrderType.objects.get(id=type_map.get(errand_type, 1))
        
        # Create order
        order = Order.objects.create(
            user=user,
            order_type=order_type,
            pickup_location=pickup_loc,
            delivery_location=delivery_loc,
            receiver_name=request.data.get('receiver_name', ''),
            receiver_phone=request.data.get('receiver_phone', ''),
            description=request.data.get('description', ''),
            price=request.data.get('price', 0),
            status='draft'
        )
        
        return Response({
            'order_id': order.id,
            'status': 'draft',
            'message': 'Draft order created'
        }, status=201)
    except Exception as e:
        logger.error(f"Error creating draft errand: {str(e)}")
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_errand_image(request, order_id):
    """Upload image for errand"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        # Image upload logic here
        return Response({'message': 'Image uploaded'})
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_errand_receiver_info(request, order_id):
    """Update receiver info"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        order.receiver_name = request.data.get('receiver_name', order.receiver_name)
        order.receiver_phone = request.data.get('receiver_phone', order.receiver_phone)
        order.save()
        return Response({'message': 'Receiver info updated'})
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_errand(request, order_id):
    """Confirm and submit errand"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        order.status = 'pending'
        order.save()
        return Response({
            'order_id': order.id,
            'status': 'pending',
            'message': 'Order confirmed and submitted'
        })
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_draft_errand(request, order_id):
    """Get draft errand details"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        return Response({
            'order_id': order.id,
            'status': order.status,
            'pickup_location': order.pickup_location.name if order.pickup_location else '',
            'delivery_location': order.delivery_location.name if order.delivery_location else '',
            'receiver_name': order.receiver_name,
            'receiver_phone': order.receiver_phone,
            'description': order.description,
            'price': float(order.price)
        })
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_draft_errand(request, order_id):
    """Delete draft errand"""
    try:
        order = Order.objects.get(id=order_id, user=request.user, status='draft')
        order.delete()
        return Response({'message': 'Draft deleted'}, status=204)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)
