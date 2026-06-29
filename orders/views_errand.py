"""
Errand Flow Views - 4 Step Process
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from orders.models import Order, OrderImage, OrderType, OrderTracking
from accounts.serializers import UserSerializer
from core.utils import generate_order_number, calculate_distance, calculate_parcel_price, calculate_cargo_price
from core.sms_service import send_sms


def get_order_serialized(order):
    """Serialize order for response"""
    return {
        'id': order.id,
        'client': UserSerializer(order.user).data,
        'assistant': UserSerializer(order.assistant).data if order.assistant else None,
        'handler': None,
        'order_type': {
            'id': order.order_type.id,
            'name': order.order_type.name,
            'description': order.order_type.description
        } if order.order_type else None,
        'title': order.title,
        'description': order.item_description,
        'pickup_location': None,
        'delivery_location': None,
        'pickup_location_details': None,
        'delivery_location_details': None,
        'pickup_location_display': order.pickup_address,
        'delivery_location_display': order.delivery_address,
        'pickup_address': order.pickup_address,
        'delivery_address': order.delivery_address,
        'pickup_latitude': float(order.pickup_lat),
        'pickup_longitude': float(order.pickup_lng),
        'delivery_latitude': float(order.delivery_lat),
        'delivery_longitude': float(order.delivery_lng),
        'recipient_name': order.receiver_name,
        'contact_number': order.receiver_phone,
        'alternative_contact_name': None,
        'alternative_contact_number': None,
        'scheduled_date': None,
        'scheduled_time': None,
        'price': str(order.total_price),
        'status': order.status,
        'created_at': order.created_at,
        'updated_at': order.updated_at,
        'assigned_at': order.assigned_at,
        'started_at': order.picked_at,
        'completed_at': order.delivered_at,
        'cancelled_at': order.cancelled_at,
        'shopping_items': [],
        'images': [
            {
                'id': img.id,
                'image': img.image_url,
                'image_url': img.image_url,
                'description': 'image',
                'stage': 'before',
                'uploaded_at': img.uploaded_at
            } for img in order.images.all()
        ],
        'review': None,
        'cargo_details': None,
        'price_finalized': order.status != 'Draft'
    }


@swagger_auto_schema(tags=['orders'], 
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['order_type_id', 'pickup_address', 'delivery_address'],
        properties={
            'order_type_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='1=Normal Delivery, 2=Cargo'),
            'title': openapi.Schema(type=openapi.TYPE_STRING),
            'description': openapi.Schema(type=openapi.TYPE_STRING),
            'pickup_address': openapi.Schema(type=openapi.TYPE_STRING),
            'delivery_address': openapi.Schema(type=openapi.TYPE_STRING),
            'pickup_latitude': openapi.Schema(type=openapi.TYPE_NUMBER),
            'pickup_longitude': openapi.Schema(type=openapi.TYPE_NUMBER),
            'delivery_latitude': openapi.Schema(type=openapi.TYPE_NUMBER),
            'delivery_longitude': openapi.Schema(type=openapi.TYPE_NUMBER),
            'distance': openapi.Schema(type=openapi.TYPE_NUMBER),
        }
    ),
    responses={201: openapi.Response('Draft created')}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_draft(request):
    """Step 1: Create draft order with price calculation"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Creating draft order with data: {request.data}")
        
        order_type_id = request.data.get('order_type_id')
        order_type = OrderType.objects.get(id=order_type_id)
        
        # Get coordinates
        pickup_lat = request.data.get('pickup_latitude', 0)
        pickup_lng = request.data.get('pickup_longitude', 0)
        delivery_lat = request.data.get('delivery_latitude', 0)
        delivery_lng = request.data.get('delivery_longitude', 0)
        
        # FALLBACK: If coordinates are 0, try geocoding the addresses
        if not pickup_lat or not pickup_lng or not delivery_lat or not delivery_lng:
            logger.info("Coordinates missing, attempting geocoding...")
            api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
            
            if api_key:
                import requests as req
                geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'
                
                # Geocode pickup address
                if not pickup_lat or not pickup_lng:
                    pickup_response = req.get(geocode_url, params={
                        'address': request.data['pickup_address'],
                        'key': api_key,
                        'components': 'country:KE'
                    }, timeout=5)
                    pickup_data = pickup_response.json()
                    if pickup_data.get('status') == 'OK' and pickup_data.get('results'):
                        location = pickup_data['results'][0]['geometry']['location']
                        pickup_lat = location['lat']
                        pickup_lng = location['lng']
                        logger.info(f"Geocoded pickup: {pickup_lat}, {pickup_lng}")
                
                # Geocode delivery address
                if not delivery_lat or not delivery_lng:
                    delivery_response = req.get(geocode_url, params={
                        'address': request.data['delivery_address'],
                        'key': api_key,
                        'components': 'country:KE'
                    }, timeout=5)
                    delivery_data = delivery_response.json()
                    if delivery_data.get('status') == 'OK' and delivery_data.get('results'):
                        location = delivery_data['results'][0]['geometry']['location']
                        delivery_lat = location['lat']
                        delivery_lng = location['lng']
                        logger.info(f"Geocoded delivery: {delivery_lat}, {delivery_lng}")
        
        # Calculate distance if coordinates provided
        if pickup_lat and pickup_lng and delivery_lat and delivery_lng:
            distance_km = calculate_distance(pickup_lat, pickup_lng, delivery_lat, delivery_lng)
        else:
            distance_km = request.data.get('distance', 0)
        
        logger.info(f"Distance calculated: {distance_km} km")
        
        # Calculate price based on order type
        if order_type.code == 'cargo':
            pricing = calculate_cargo_price(distance_km)
        else:
            pricing = calculate_parcel_price(distance_km)
        
        logger.info(f"Pricing: {pricing}")
        
        # Create draft order
        order = Order.objects.create(
            user=request.user,
            order_type=order_type,
            order_number=generate_order_number(),
            title=request.data.get('title', ''),
            item_description=request.data.get('description', ''),
            pickup_address=request.data['pickup_address'],
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            delivery_address=request.data['delivery_address'],
            delivery_lat=delivery_lat,
            delivery_lng=delivery_lng,
            distance_km=distance_km,
            base_price=pricing['base_fee'],
            total_price=pricing['total'],
            status='Draft'
        )
        
        logger.info(f"Draft order created: {order.id}")
        
        return Response({
            'order_id': order.id,
            'status': 'draft',
            'pricing_breakdown': pricing,
            'order': get_order_serialized(order),
            'next_step': 'Upload images and add receiver contact info'
        }, status=status.HTTP_201_CREATED)
        
    except OrderType.DoesNotExist:
        logger.error(f"Invalid order type: {order_type_id}")
        return Response({'error': 'Invalid order type'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Draft order error: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(tags=['orders'], 
    method='post',
    manual_parameters=[
        openapi.Parameter('order_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER)
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'image': openapi.Schema(type=openapi.TYPE_STRING, description='Image URL or base64'),
        }
    ),
    responses={201: openapi.Response('Image uploaded')}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request, order_id):
    """Step 2: Upload order images (can be called multiple times)"""
    try:
        order = Order.objects.get(id=order_id, user=request.user, status='Draft')
        image_url = request.data.get('image')
        
        order_image = OrderImage.objects.create(
            order=order,
            image_url=image_url
        )
        
        return Response({
            'image_id': order_image.id,
            'image': {
                'id': order_image.id,
                'image': order_image.image_url,
                'image_url': order_image.image_url,
                'description': 'image',
                'stage': 'before',
                'uploaded_at': order_image.uploaded_at
            },
            'total_images': order.images.count()
        }, status=status.HTTP_201_CREATED)
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found or not in draft status'}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(tags=['orders'], 
    method='post',
    manual_parameters=[
        openapi.Parameter('order_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER)
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['recipient_name', 'contact_number'],
        properties={
            'recipient_name': openapi.Schema(type=openapi.TYPE_STRING),
            'contact_number': openapi.Schema(type=openapi.TYPE_STRING),
            'estimated_value': openapi.Schema(type=openapi.TYPE_NUMBER),
        }
    ),
    responses={200: openapi.Response('Receiver info updated')}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_receiver_info(request, order_id):
    """Step 3: Add receiver contact information"""
    try:
        order = Order.objects.get(id=order_id, user=request.user, status='Draft')
        
        order.receiver_name = request.data.get('recipient_name')
        order.receiver_phone = request.data.get('contact_number')
        order.estimated_value = request.data.get('estimated_value')
        order.save()
        
        return Response({
            'message': 'Receiver info updated',
            'order': get_order_serialized(order)
        })
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found or not in draft status'}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(tags=['orders'], 
    method='post',
    manual_parameters=[
        openapi.Parameter('order_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER)
    ],
    responses={200: openapi.Response('Order confirmed')}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_order(request, order_id):
    """Step 4: Confirm order and send SMS"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        order = Order.objects.get(id=order_id, user=request.user, status='Draft')
        logger.info(f"Order {order_id} found with status: {order.status}")
        
        # Update order number if it's still NEW
        if 'NEW' in order.order_number:
            order.order_number = f"ORD-{order.id}"
        
        # Change status to pending
        order.status = 'Pending'
        order.confirmed_at = timezone.now()
        order.save()
        
        # Verify the save worked
        order.refresh_from_db()
        logger.info(f"Order {order_id} status after save: {order.status}")
        
        # Create tracking entry
        OrderTracking.objects.create(
            order=order,
            status='pending',
            message='Order confirmed and waiting for rider assignment'
        )
        
        # Send SMS notification
        phone = order.user.phone_number.replace('+', '')
        # Use only last 6 digits of order ID for SMS
        short_order_id = str(order.id)[-6:].zfill(6)
        client_name = order.user.first_name or "Customer"
        message = (
            f"Hi {client_name}! Order #{short_order_id} confirmed.\n"
            f"From: {order.pickup_address}\n"
            f"To: {order.delivery_address}\n"
            f"Distance: {order.distance_km:.1f} km\n"
            f"Cost: KES {order.total_price}\n"
            f"Your rider is on the way to pick up!"
        )
        send_sms(phone, message)
        
        return Response({
            'message': 'Errand confirmed successfully!',
            'order_id': order.id,
            'status': order.status,
            'order': get_order_serialized(order),
            'notifications_sent': True
        })
        
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found or not in draft status")
        return Response({'error': 'Order not found or not in draft status'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error confirming order {order_id}: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
