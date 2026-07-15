"""
Handler-specific views - Complete migration from old backend
Handlers can place orders on behalf of clients, view all orders, manage clients
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from orders.models import Order, OrderTracking, OrderType, OrderImage
from accounts.models import User
from orders.serializers import OrderSerializer
from accounts.serializers import UserSerializer
from core.utils import generate_order_number, calculate_distance, calculate_parcel_price, calculate_cargo_price
from core.sms_service import send_sms


class IsHandler(permissions.BasePermission):
    """Check if user is handler or admin"""
    def has_permission(self, request, view):
        return request.user.user_type in ['handler', 'admin']


# HANDLER CLIENT MANAGEMENT

@swagger_auto_schema(method='get', tags=['Handler'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def handler_get_clients(request):
    """Handler gets list of their assigned clients"""
    if request.user.user_type not in ['handler', 'admin']:
        return Response({'error': 'Handler access required'}, status=status.HTTP_403_FORBIDDEN)
    
    clients = User.objects.filter(
        account_manager=request.user,
        user_type='user'
    ).order_by('first_name', 'last_name')
    
    serializer = UserSerializer(clients, many=True)
    return Response(serializer.data)


@swagger_auto_schema(method='get', tags=['Handler'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def handler_get_all_clients(request):
    """Handler gets ALL clients in the system"""
    if request.user.user_type not in ['handler', 'admin']:
        return Response({'error': 'Handler access required'}, status=status.HTTP_403_FORBIDDEN)
    
    clients = User.objects.filter(
        user_type__in=['user', 'client']
    ).select_related('account_manager').order_by('-date_joined')
    
    serializer = UserSerializer(clients, many=True)
    return Response(serializer.data)


@swagger_auto_schema(method='post', tags=['Handler'])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def handler_assign_client(request, user_id):
    """Admin/Handler assigns account manager to a client"""
    if request.user.user_type not in ['handler', 'admin']:
        return Response({'error': 'Handler/Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        client = User.objects.get(id=user_id, user_type='user')
        account_manager_id = request.data.get('account_manager_id')
        
        if account_manager_id:
            account_manager = User.objects.get(id=account_manager_id, user_type='handler')
            client.account_manager = account_manager
        else:
            client.account_manager = None
        
        client.save()
        
        return Response({
            'success': True,
            'message': 'Account manager updated',
            'user': UserSerializer(client).data
        })
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# HANDLER ORDER MANAGEMENT

@swagger_auto_schema(method='post', tags=['Handler'])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def handler_create_order_for_client(request):
    """Handler creates order on behalf of client (4-step errand flow)"""
    if request.user.user_type not in ['handler', 'admin']:
        return Response({'error': 'Handler access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get client_id from request
        client_id = request.data.get('client_id')
        if not client_id:
            return Response({'error': 'client_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        client = User.objects.get(id=client_id, user_type='user')
        
        # Get order type
        order_type_id = request.data.get('order_type_id')
        order_type = OrderType.objects.get(id=order_type_id)
        
        # Get coordinates
        pickup_lat = request.data.get('pickup_latitude', 0)
        pickup_lng = request.data.get('pickup_longitude', 0)
        delivery_lat = request.data.get('delivery_latitude', 0)
        delivery_lng = request.data.get('delivery_longitude', 0)
        
        # Calculate distance
        if pickup_lat and pickup_lng and delivery_lat and delivery_lng:
            distance_km = calculate_distance(pickup_lat, pickup_lng, delivery_lat, delivery_lng)
        else:
            distance_km = request.data.get('distance', 0)
        
        # Calculate price
        if order_type.code == 'cargo':
            pricing = calculate_cargo_price(distance_km)
        else:
            pricing = calculate_parcel_price(distance_km)
        
        # Create order for client
        order = Order.objects.create(
            user=client,  # Order belongs to client, not handler
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
        
        return Response({
            'order_id': order.id,
            'status': 'Draft',
            'pricing_breakdown': pricing,
            'message': 'Order created for client',
            'client': {
                'id': client.id,
                'name': client.get_full_name(),
                'phone': client.phone_number
            }
        }, status=status.HTTP_201_CREATED)
        
    except User.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
    except OrderType.DoesNotExist:
        return Response({'error': 'Invalid order type'}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='post', tags=['Handler'])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def handler_confirm_order_for_client(request, order_id):
    """Handler confirms order on behalf of client"""
    if request.user.user_type not in ['handler', 'admin']:
        return Response({'error': 'Handler access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        order = Order.objects.get(id=order_id, status='Draft')
        
        # Confirm order
        order.status = 'Pending'
        order.confirmed_at = timezone.now()
        order.save()
        
        OrderTracking.objects.create(
            order=order,
            status='Pending',
            message='Order confirmed by handler'
        )
        
        # Send SMS to client
        message = f"Your order {order.order_number} has been confirmed by your account manager. Total: KES {order.total_price}. We're finding you a rider."
        send_sms(order.user.phone_number, message)
        
        return Response({
            'message': 'Order confirmed for client',
            'order_id': order.id,
            'status': 'Pending'
        })
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found or wrong status'}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(method='get', tags=['Handler'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def handler_get_client_orders(request, client_id):
    """Handler gets all orders for a specific client"""
    if request.user.user_type not in ['handler', 'admin']:
        return Response({'error': 'Handler access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        client = User.objects.get(id=client_id, user_type='user')
        
        orders = Order.objects.filter(user=client).select_related(
            'user', 'assistant', 'order_type'
        ).prefetch_related('images').order_by('-created_at')
        
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
        
    except User.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(method='post', tags=['Handler'])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def handler_cancel_order(request, order_id):
    """Handler cancels order on behalf of client"""
    if request.user.user_type not in ['handler', 'admin']:
        return Response({'error': 'Handler access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        order = Order.objects.get(id=order_id)
        
        # Cannot cancel completed orders
        if order.status == 'Completed':
            return Response({'error': 'Cannot cancel completed order'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'Cancelled'
        order.cancelled_at = timezone.now()
        order.save()
        
        OrderTracking.objects.create(
            order=order,
            status='Cancelled',
            message='Order cancelled by handler'
        )
        
        return Response({
            'message': 'Order cancelled',
            'order_id': order.id
        })
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(method='get', tags=['Handler'])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def handler_dashboard_stats(request):
    """Handler dashboard statistics"""
    if request.user.user_type not in ['handler', 'admin']:
        return Response({'error': 'Handler access required'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.user.user_type == 'handler':
        # Get stats for handler's clients only
        client_ids = User.objects.filter(account_manager=request.user).values_list('id', flat=True)
        orders = Order.objects.filter(user_id__in=client_ids)
    else:
        # Admin sees all
        orders = Order.objects.all()
        client_ids = User.objects.filter(user_type='user').values_list('id', flat=True)
    
    stats = {
        'total_clients': len(client_ids),
        'total_orders': orders.count(),
        'pending_orders': orders.filter(status='Pending').count(),
        'assigned_orders': orders.filter(status='Assigned').count(),
        'in_transit': orders.filter(status='InTransit').count(),
        'completed_orders': orders.filter(status='Completed').count(),
        'cancelled_orders': orders.filter(status='Cancelled').count(),
        'payment_pending': orders.filter(status='PaymentPending').count(),
    }
    
    return Response(stats)


# ========== NEW HANDLER DASHBOARD ENDPOINTS ==========

@swagger_auto_schema(
    method='get',
    tags=['handler-dashboard'],
    manual_parameters=[
        openapi.Parameter('is_verified', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, 
                         description='Filter by verification status'),
        openapi.Parameter('is_active', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, 
                         description='Filter by active status')
    ],
    responses={200: UserSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_handlers(request):
    """List all handlers/riders"""
    handlers = User.objects.filter(user_type='handler').order_by('-date_joined')
    
    is_verified = request.query_params.get('is_verified')
    if is_verified is not None:
        is_verified_bool = is_verified.lower() == 'true'
        handlers = handlers.filter(is_verified=is_verified_bool)
    
    is_active = request.query_params.get('is_active')
    if is_active is not None:
        is_active_bool = is_active.lower() == 'true'
        handlers = handlers.filter(is_active=is_active_bool)
    
    serializer = UserSerializer(handlers, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    tags=['handler-dashboard'],
    responses={200: UserSerializer()}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def handler_detail(request, handler_id):
    """Get handler details"""
    try:
        handler = User.objects.get(id=handler_id, user_type='handler')
        serializer = UserSerializer(handler)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'Handler not found'}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='patch',
    tags=['handler-dashboard'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'is_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Verification status'),
            'notes': openapi.Schema(type=openapi.TYPE_STRING, description='Verification notes'),
        }
    ),
    responses={200: openapi.Response('Handler verified successfully')}
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def verify_handler(request, handler_id):
    """Verify or reject handler"""
    try:
        handler = User.objects.get(id=handler_id, user_type='handler')
        
        is_verified = request.data.get('is_verified')
        if is_verified is not None:
            handler.is_verified = is_verified
            handler.verified_at = timezone.now() if is_verified else None
            handler.save()
        
        try:
            phone = handler.phone_number.replace('+', '')
            if is_verified:
                message = f"Congratulations! Your FagiErrands handler account has been verified. You can now start accepting orders."
            else:
                message = f"Your FagiErrands handler verification was not approved. Please contact support for more information."
            send_sms(phone, message)
        except:
            pass
        
        return Response({
            'message': 'Handler verification updated',
            'handler_id': handler.id,
            'is_verified': handler.is_verified,
            'name': handler.get_full_name()
        })
        
    except User.DoesNotExist:
        return Response({'error': 'Handler not found'}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='get',
    tags=['handler-dashboard'],
    responses={200: UserSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_handlers(request):
    """Get list of available/active handlers"""
    handlers = User.objects.filter(
        user_type='handler',
        is_verified=True,
        is_active=True
    ).order_by('-date_joined')
    
    serializer = UserSerializer(handlers, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    tags=['handler-dashboard'],
    responses={200: openapi.Response('Handler statistics')}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def handler_stats(request):
    """Get handler statistics"""
    from django.db.models import Count
    from orders.models import Order
    
    stats = {
        'total_handlers': User.objects.filter(user_type='handler').count(),
        'verified_handlers': User.objects.filter(user_type='handler', is_verified=True).count(),
        'active_handlers': User.objects.filter(user_type='handler', is_active=True).count(),
        'pending_verification': User.objects.filter(user_type='handler', is_verified=False).count(),
        'handlers_with_orders': Order.objects.filter(assistant__isnull=False).values('assistant').distinct().count(),
    }
    
    return Response(stats)
