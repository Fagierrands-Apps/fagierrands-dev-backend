from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.db import transaction
from decimal import Decimal
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Order, OrderType, OrderImage
from .serializers import OrderSerializer, OrderImageSerializer
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)
from locations.google_maps_service import GoogleMapsService
import requests
import logging

logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['order_type_id', 'pickup_lat', 'pickup_lng', 'dropoff_lat', 'dropoff_lng'],
        properties={
            'order_type_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'pickup_lat': openapi.Schema(type=openapi.TYPE_NUMBER),
            'pickup_lng': openapi.Schema(type=openapi.TYPE_NUMBER),
            'dropoff_lat': openapi.Schema(type=openapi.TYPE_NUMBER),
            'dropoff_lng': openapi.Schema(type=openapi.TYPE_NUMBER),
        }
    )
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_price_with_route(request):
    """
    Calculate price based on pickup and dropoff coordinates
    Returns: price breakdown, distance, duration, and route polyline
    """
    order_type_id = request.data.get('order_type_id')
    pickup_lat = request.data.get('pickup_lat')
    pickup_lng = request.data.get('pickup_lng')
    dropoff_lat = request.data.get('dropoff_lat')
    dropoff_lng = request.data.get('dropoff_lng')
    
    if not all([order_type_id, pickup_lat, pickup_lng, dropoff_lat, dropoff_lng]):
        return Response({
            'error': 'order_type_id, pickup_lat, pickup_lng, dropoff_lat, dropoff_lng are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order_type = OrderType.objects.get(id=order_type_id)
        
        # Get route from Google Maps Directions API
        api_key = settings.GOOGLE_MAPS_API_KEY
        directions_url = "https://maps.googleapis.com/maps/api/directions/json"
        
        params = {
            'origin': f"{pickup_lat},{pickup_lng}",
            'destination': f"{dropoff_lat},{dropoff_lng}",
            'key': api_key,
            'mode': 'driving'
        }
        
        response = requests.get(directions_url, params=params, timeout=10)
        data = response.json()
        
        if data.get('status') != 'OK':
            return Response({
                'error': f"Google Maps API error: {data.get('status')}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        route = data['routes'][0]
        leg = route['legs'][0]
        
        # Extract distance and duration
        distance_meters = leg['distance']['value']
        distance_km = Decimal(str(distance_meters / 1000))
        duration_seconds = leg['duration']['value']
        duration_minutes = duration_seconds / 60
        
        # Get polyline for route visualization
        polyline = route['overview_polyline']['points']
        
        # Calculate price
        calculated_price = order_type.calculate_price(distance_km)
        
        # Price breakdown
        if distance_km <= 7:
            distance_fee = Decimal('0.00')
        else:
            extra_km = distance_km - 7
            distance_fee = extra_km * order_type.price_per_km
        
        return Response({
            'order_type': order_type.name,
            'distance': {
                'km': float(distance_km),
                'text': leg['distance']['text']
            },
            'duration': {
                'minutes': int(duration_minutes),
                'text': leg['duration']['text']
            },
            'pricing': {
                'base_fee': float(order_type.base_price),
                'distance_fee': float(distance_fee),
                'total': float(calculated_price),
                'currency': 'KSH'
            },
            'route': {
                'polyline': polyline,
                'start_address': leg['start_address'],
                'end_address': leg['end_address']
            },
            'pricing_note': f'KSh {order_type.base_price} for first 7km, KSh {order_type.price_per_km}/km thereafter'
        })
        
    except OrderType.DoesNotExist:
        return Response({
            'error': 'Order type not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except requests.exceptions.RequestException as e:
        logger.error(f"Google Maps API error: {str(e)}")
        return Response({
            'error': 'Failed to calculate route'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Price calculation error: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['order_type_id', 'distance'],
        properties={
            'order_type_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'distance': openapi.Schema(type=openapi.TYPE_NUMBER),
        }
    )
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_errand_price(request):
    """
    Step 0: Calculate price based on pickup/delivery locations and distance
    No order created yet - just price calculation
    """
    order_type_id = request.data.get('order_type_id')
    distance = request.data.get('distance')
    
    if not order_type_id or distance is None:
        return Response({
            'error': 'order_type_id and distance are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order_type = OrderType.objects.get(id=order_type_id)
        distance_decimal = Decimal(str(distance))
        
        # Calculate price breakdown
        base_fee = order_type.base_price
        
        if distance_decimal <= 7:
            distance_fee = Decimal('0.00')
            total = base_fee
        else:
            extra_km = distance_decimal - 7
            distance_fee = extra_km * order_type.price_per_km
            total = base_fee + distance_fee
        
        return Response({
            'order_type': order_type.name,
            'pricing_breakdown': {
                'base_fee': float(base_fee),
                'distance_fee': float(distance_fee),
                'total': float(total),
                'distance_km': float(distance_decimal)
            },
            'calculation_note': f'Base fee KSh {base_fee} for first 7km, KSh {order_type.price_per_km}/km thereafter'
        })
        
    except OrderType.DoesNotExist:
        return Response({
            'error': 'Order type not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['order_type_id', 'pickup_address', 'delivery_address'],
        properties={
            'order_type_id': openapi.Schema(type=openapi.TYPE_INTEGER),
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
    )
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_draft_errand(request):
    """
    Step 1: Create errand with DRAFT status
    User has filled: pickup, delivery, order type, description, title
    Price is calculated and saved
    No notifications sent yet
    """
    try:
        with transaction.atomic():
            order_type_id = request.data.get('order_type_id')
            distance = request.data.get('distance')
            
            if not order_type_id:
                return Response({
                    'error': 'order_type_id is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            order_type = OrderType.objects.get(id=order_type_id)
            
            # Calculate price
            if distance:
                distance_decimal = Decimal(str(distance))
                calculated_price = order_type.calculate_price(distance_decimal)
            else:
                calculated_price = order_type.base_price
            
            # Create order with DRAFT status
            order = Order.objects.create(
                client=request.user,
                order_type=order_type,
                title=request.data.get('title', ''),
                description=request.data.get('description', ''),
                pickup_address=request.data.get('pickup_address', ''),
                delivery_address=request.data.get('delivery_address', ''),
                pickup_latitude=request.data.get('pickup_latitude'),
                pickup_longitude=request.data.get('pickup_longitude'),
                delivery_latitude=request.data.get('delivery_latitude'),
                delivery_longitude=request.data.get('delivery_longitude'),
                distance=distance,
                price=calculated_price,
                status='Draft'  # DRAFT status
            )
            
            serializer = OrderSerializer(order, context={'request': request})
            
            return Response({
                'order_id': order.id,
                'status': 'Draft',
                'pricing_breakdown': {
                    'base_fee': float(order_type.base_price),
                    'distance_fee': float(calculated_price - order_type.base_price) if calculated_price > order_type.base_price else 0.0,
                    'total': float(calculated_price),
                    'distance_km': float(distance) if distance else 0.0
                },
                'order': serializer.data,
                'next_step': 'Upload images and add receiver contact info'
            }, status=status.HTTP_201_CREATED)
            
    except OrderType.DoesNotExist:
        return Response({
            'error': 'Order type not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE, required=True, description='Image file'),
        openapi.Parameter('caption', openapi.IN_FORM, type=openapi.TYPE_STRING, required=False, description='Image caption'),
    ],
    consumes=['multipart/form-data'],
    responses={201: 'Image uploaded successfully'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_errand_image(request, order_id):
    """
    Step 2a: Upload images to draft errand
    Can be called multiple times
    """
    try:
        order = Order.objects.get(id=order_id, client=request.user)
        
        if order.status not in ['Draft', 'Pending']:
            return Response({
                'error': 'Can only upload images to draft or pending orders'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        image = request.FILES.get('image')
        caption = request.data.get('caption', '')
        
        if not image:
            return Response({
                'error': 'Image file is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order_image = OrderImage.objects.create(
            order=order,
            image=image,
            description=caption,
            stage='before'
        )
        
        serializer = OrderImageSerializer(order_image, context={'request': request})
        
        return Response({
            'image_id': order_image.id,
            'image': serializer.data,
            'total_images': order.images.count()
        }, status=status.HTTP_201_CREATED)
        
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found or you do not have permission'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'recipient_name': openapi.Schema(type=openapi.TYPE_STRING),
            'contact_number': openapi.Schema(type=openapi.TYPE_STRING),
            'estimated_value': openapi.Schema(type=openapi.TYPE_NUMBER),
        }
    )
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_errand_receiver_info(request, order_id):
    """
    Step 2b: Update receiver contact info and estimated value
    """
    try:
        order = Order.objects.get(id=order_id, client=request.user)
        
        if order.status not in ['Draft', 'Pending']:
            return Response({
                'error': 'Can only update draft or pending orders'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update receiver info
        if 'recipient_name' in request.data:
            order.recipient_name = request.data['recipient_name']
        if 'contact_number' in request.data:
            order.contact_number = request.data['contact_number']
        if 'estimated_value' in request.data:
            order.estimated_value = request.data['estimated_value']
        
        order.save()
        
        serializer = OrderSerializer(order, context={'request': request})
        
        return Response({
            'message': 'Receiver info updated',
            'order': serializer.data
        })
        
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found or you do not have permission'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    responses={
        200: openapi.Response(
            description='Errand confirmed successfully',
            examples={
                'application/json': {
                    'message': 'Errand confirmed successfully!',
                    'order_id': 13,
                    'status': 'Pending',
                    'order': {
                        'id': 13,
                        'title': 'Package Delivery',
                        'status': 'Pending',
                        'pickup_address': 'Westlands Mall',
                        'delivery_address': 'Yaya Centre'
                    },
                    'notifications_sent': True
                }
            }
        ),
        400: 'Validation error or order not in draft status',
        404: 'Order not found'
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_errand(request, order_id):
    """
    Step 3: Confirm errand - changes status from DRAFT to PENDING
    This is when the errand becomes official and can be assigned to riders
    Notifications and SMS sent here
    Working hours: 6 AM - 8 PM
    """
    try:
        with transaction.atomic():
            order = Order.objects.get(id=order_id, client=request.user)
            
            # Check working hours (6 AM - 8 PM)
            from datetime import datetime
            import pytz
            
            nairobi_tz = pytz.timezone('Africa/Nairobi')
            current_time = datetime.now(nairobi_tz)
            current_hour = current_time.hour
            
            if current_hour < 6 or current_hour >= 20:
                return Response({
                    'error': 'Errands can only be placed between 6:00 AM and 8:00 PM'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if order.status != 'Draft':
                return Response({
                    'error': 'Can only confirm draft orders'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate required fields
            if not order.pickup_address or not order.delivery_address:
                return Response({
                    'error': 'Pickup and delivery addresses are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not order.contact_number:
                return Response({
                    'error': 'Receiver contact number is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Change status to PENDING
            order.status = 'Pending'
            order.save()
            
            # Send SMS notification to client
            try:
                from accounts.services.sms_service import SMSService
                sms_message = f"""Hello! Your errand has been confirmed.

Order: #{order.id}
Pickup: {order.pickup_address}
Delivery: {order.delivery_address}
Amount: KES {order.price}

A rider is on the way to pick up your item.

Thank you for choosing FagiErrands!"""
                SMSService.send_sms(request.user.phone_number, sms_message)
            except Exception as sms_error:
                print(f"SMS sending failed: {sms_error}")
            
            # TODO: Send push notification
            # TODO: Notify available riders
            
            serializer = OrderSerializer(order, context={'request': request})
            
            return Response({
                'message': 'Errand confirmed successfully!',
                'order_id': order.id,
                'status': 'Pending',
                'order': serializer.data,
                'notifications_sent': True
            })
            
    except Order.DoesNotExist:
        return Response({
            'error': 'Order not found or you do not have permission'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    operation_description="Get draft errand details",
    responses={
        200: openapi.Response(
            description="Draft errand details",
            examples={
                "application/json": {
                    "order": {
                        "id": 9,
                        "status": "draft",
                        "title": "tea leaves",
                        "pickup_address": "next gen mall",
                        "delivery_address": "kilimani"
                    },
                    "images_count": 1,
                    "has_receiver_info": False
                }
            }
        ),
        404: "Draft order not found"
    }
)
def get_draft_errand(request, order_id):
    """
    Get draft errand details
    """
    try:
        order = Order.objects.get(id=order_id, client=request.user, status='Draft')
        serializer = OrderSerializer(order, context={'request': request})
        
        return Response({
            'order': serializer.data,
            'images_count': order.images.count(),
            'can_confirm': bool(order.pickup_address and order.delivery_address and order.contact_number)
        })
        
    except Order.DoesNotExist:
        return Response({
            'error': 'Draft order not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    operation_description="Delete a draft errand",
    responses={
        200: openapi.Response(
            description="Draft deleted successfully",
            examples={
                "application/json": {
                    "message": "Draft errand deleted successfully"
                }
            }
        ),
        404: "Draft order not found"
    }
)
def delete_draft_errand(request, order_id):
    """
    Delete a draft errand
    """
    try:
        order = Order.objects.get(id=order_id, client=request.user, status='Draft')
        order.delete()
        
        return Response({
            'message': 'Draft errand deleted successfully'
        })
        
    except Order.DoesNotExist:
        return Response({
            'error': 'Draft order not found'
        }, status=status.HTTP_404_NOT_FOUND)
