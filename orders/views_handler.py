"""
Handler Dashboard Views - Order Management
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from orders.models import Order, SOSAlert
from orders.serializers import OrderSerializer, SOSAlertSerializer
from accounts.models import User


@swagger_auto_schema(
    method='get',
    tags=['handler-dashboard'],
    manual_parameters=[
        openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_STRING, 
                         description='Filter by status: pending, assigned, in_progress, completed, cancelled')
    ],
    responses={200: OrderSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_orders(request):
    """List all orders with optional status and client_phone filter"""
    status_filter = request.query_params.get('status')
    client_phone = request.query_params.get('client_phone')

    orders = Order.objects.all().select_related('user', 'assistant', 'order_type').order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter)

    if client_phone:
        normalized = client_phone.lstrip('0')
        orders = orders.filter(user__phone_number__endswith=normalized)
    
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    tags=['handler-dashboard'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['rider_id'],
        properties={
            'rider_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Handler/Rider user ID'),
        }
    ),
    responses={200: openapi.Response('Order assigned successfully')}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_order(request, order_id):
    """Assign order to a rider - allows unlimited concurrent orders"""
    try:
        order = Order.objects.get(id=order_id)
        rider_id = request.data.get('rider_id') or request.data.get('assistant_id')
        
        if not rider_id:
            return Response({'error': 'rider_id or assistant_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        rider = User.objects.get(id=rider_id, user_type='assistant')
        
        # Assign order
        order.assistant = rider
        order.status = 'Assigned'
        order.assigned_at = timezone.now()
        order.save()
        
        # Send notification to rider
        from core.sms_service import send_sms
        try:
            phone = rider.phone_number.replace('+', '')
            short_order_id = str(order.id)[-6:].zfill(6)
            message = f"New order #{short_order_id} assigned! From: {order.pickup_address}. KES {order.total_price}"
            send_sms(phone, message)
        except:
            pass
        
        return Response({
            'message': 'Order assigned successfully',
            'order_id': order.id,
            'rider_name': rider.get_full_name(),
            'status': order.status
        })
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'error': 'Rider not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    tags=['handler-dashboard'],
    responses={200: openapi.Response('Order statistics')}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_stats(request):
    """Get order statistics for dashboard"""
    from django.db.models import Count, Sum
    
    stats = {
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='Pending').count(),
        'assigned_orders': Order.objects.filter(status='Assigned').count(),
        'in_progress_orders': Order.objects.filter(status='InTransit').count(),
        'completed_orders': Order.objects.filter(status='Completed').count(),
        'cancelled_orders': Order.objects.filter(status='Cancelled').count(),
        'total_revenue': Order.objects.filter(status='Completed').aggregate(Sum('total_price'))['total_price__sum'] or 0,
    }
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_for_client(request):
    """Handler creates order on behalf of client"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        from core.utils import normalize_phone_number
        
        logger.info(f"Create order request data: {request.data}")
        
        # Get client by phone number
        client_phone = request.data.get('client_phone')
        if not client_phone:
            return Response({'error': 'client_phone is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalize phone number
        client_phone = normalize_phone_number(client_phone)
        
        # Find existing client only - don't create new ones
        try:
            client = User.objects.get(phone_number=client_phone)
            # Accept both 'client' and 'user' types
            if client.user_type not in ['client', 'user']:
                return Response({'error': f'User is type "{client.user_type}". Only clients can place orders.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': f'Client not found with phone {client_phone}. Client must register first.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create order
        order = Order.objects.create(
            user=client,
            title=request.data.get('title', 'Errand'),
            pickup_address=request.data.get('pickup_address'),
            pickup_lat=request.data.get('pickup_lat', 0),
            pickup_lng=request.data.get('pickup_lng', 0),
            delivery_address=request.data.get('delivery_address'),
            delivery_lat=request.data.get('delivery_lat', 0),
            delivery_lng=request.data.get('delivery_lng', 0),
            receiver_name=request.data.get('receiver_name', ''),
            receiver_phone=request.data.get('receiver_phone', ''),
            distance_km=request.data.get('distance_km', 0),
            base_price=request.data.get('base_price', 200),
            total_price=request.data.get('total_price', 200),
            payment_method=request.data.get('payment_method', 'cash'),
            payment_status='pending',
            item_description=request.data.get('item_description', '')
        )
        
        # Explicitly set status to Pending (overrides model default)
        order.status = 'Pending'
        # Fix order_number now that we have the DB id
        if 'NEW' in order.order_number:
            order.order_number = generate_order_number()
        order.save()
        
        # Refresh from DB to check what was actually saved
        order.refresh_from_db()
        logger.info(f"Order created: {order.order_number}, Status in DB: '{order.status}'")
        
        if not order.status or order.status == '':
            logger.error(f"ORDER STATUS IS EMPTY! Expected 'Pending', got: '{order.status}'")
        
        # Send SMS to client
        from core.sms_service import send_sms
        try:
            message = f"Your errand #{order.order_number} has been created. From: {order.pickup_address}. To: {order.delivery_address}. Amount: KES {order.total_price}"
            send_sms(client.phone_number, message)
        except Exception as sms_error:
            logger.warning(f"SMS send failed: {sms_error}")
        
        return Response({
            'message': 'Order created successfully',
            'order_id': order.id,
            'order_number': order.order_number,
            'client_name': client.get_full_name(),
            'total_price': str(order.total_price)
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Create order error: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
