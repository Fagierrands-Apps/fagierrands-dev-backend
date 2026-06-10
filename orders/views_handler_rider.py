"""
Handler & Rider Views - Complete system from old backend
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from orders.models import Order, OrderTracking
from orders.serializers import OrderSerializer
from accounts.models import User
from accounts.serializers import UserSerializer


class IsHandler(permissions.BasePermission):
    """Check if user is handler"""
    def has_permission(self, request, view):
        return request.user.user_type in ['handler', 'admin']


class IsAssistant(permissions.BasePermission):
    """Check if user is assistant/rider"""
    def has_permission(self, request, view):
        return request.user.user_type == 'assistant'


# HANDLER VIEWS

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def handler_all_orders(request):
    """Handler view - ALL orders without pagination"""
    if request.user.user_type not in ['handler', 'admin']:
        return Response({'error': 'Handler access required'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get query params
    status_filter = request.query_params.get('status')
    search = request.query_params.get('search')
    client_id = request.query_params.get('client_id')
    
    if request.user.user_type == 'handler':
        # Handler sees all orders (no account_manager field exists)
        orders = Order.objects.all()
    else:
        # Admin sees all orders
        orders = Order.objects.all()
    
    orders = orders.select_related('user', 'assistant', 'order_type').prefetch_related('images')
    
    # Filters
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if client_id:
        orders = orders.filter(user_id=client_id)
    
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(title__icontains=search) |
            Q(item_description__icontains=search) |
            Q(user__username__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        )
    
    orders = orders.order_by('-created_at')
    
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def handler_pending_orders(request):
    """Handler view - Pending orders only"""
    if request.user.user_type not in ['handler', 'admin']:
        return Response({'error': 'Handler access required'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.user.user_type == 'handler':
        # Handler sees only their clients' orders
        client_ids = User.objects.filter(account_manager=request.user).values_list('id', flat=True)
        orders = Order.objects.filter(user_id__in=client_ids, status='Pending')
    else:
        # Admin sees all
        orders = Order.objects.filter(status='Pending')
    
    orders = orders.select_related('user', 'assistant', 'order_type').order_by('-created_at')
    
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def handler_assign_order(request, order_id):
    """Handler manually assigns order to rider (NO SMS)"""
    if request.user.user_type not in ['handler', 'admin']:
        return Response({'error': 'Handler access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        order = Order.objects.get(id=order_id)
        assistant_id = request.data.get('assistant_id')
        
        from accounts.models import User
        assistant = User.objects.get(id=assistant_id, user_type='assistant')
        
        order.assistant = assistant
        order.status = 'Assigned'
        order.assigned_at = timezone.now()
        order.save()
        
        OrderTracking.objects.create(
            order=order,
            status='Assigned',
            message=f'Order assigned to {assistant.get_full_name()} by handler'
        )
        
        return Response({
            'message': 'Order assigned successfully',
            'order': OrderSerializer(order).data
        })
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'error': 'Rider not found'}, status=status.HTTP_404_NOT_FOUND)


# RIDER/ASSISTANT VIEWS

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rider_available_orders(request):
    """Rider view - Available orders (Pending, unassigned)"""
    if request.user.user_type != 'assistant':
        return Response({'error': 'Rider access only'}, status=status.HTTP_403_FORBIDDEN)
    
    orders = Order.objects.filter(
        status='Pending',
        assistant__isnull=True
    ).select_related('user', 'order_type').prefetch_related('images').order_by('-created_at')
    
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rider_my_orders(request):
    """Rider view - Orders assigned to this rider"""
    if request.user.user_type != 'assistant':
        return Response({'error': 'Rider access only'}, status=status.HTTP_403_FORBIDDEN)
    
    # Get active orders (not Completed or Cancelled)
    orders = Order.objects.filter(
        assistant=request.user
    ).exclude(
        status__in=['Completed', 'Cancelled']
    ).select_related('user', 'order_type').prefetch_related('images').order_by('-created_at')
    
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rider_order_history(request):
    """Rider view - All orders including Completed"""
    if request.user.user_type != 'assistant':
        return Response({'error': 'Rider access only'}, status=status.HTTP_403_FORBIDDEN)
    
    orders = Order.objects.filter(
        assistant=request.user
    ).select_related('user', 'order_type').order_by('-created_at')
    
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rider_accept_order(request, order_id):
    """Rider accepts available order (NO SMS, status: Pending → Assigned)"""
    if request.user.user_type != 'assistant':
        return Response({'error': 'Rider access only'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        order = Order.objects.get(
            id=order_id,
            status='Pending',
            assistant__isnull=True
        )
        
        # Assign to rider
        order.assistant = request.user
        order.status = 'Assigned'
        order.assigned_at = timezone.now()
        order.save()
        
        OrderTracking.objects.create(
            order=order,
            status='Assigned',
            message=f'Order accepted by {request.user.get_full_name()}'
        )
        
        # NO SMS HERE - polling endpoint will return rider details
        
        return Response({
            'success': True,
            'message': 'Order accepted successfully',
            'order': OrderSerializer(order).data
        })
        
    except Order.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Order not available or already assigned'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rider_update_status(request, order_id):
    """Rider updates order status: Assigned → InTransit → PaymentPending"""
    if request.user.user_type != 'assistant':
        return Response({'error': 'Rider access only'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        order = Order.objects.get(id=order_id, assistant=request.user)
        new_status = request.data.get('status')
        
        # Valid transitions: Assigned → InTransit → PaymentPending
        if new_status not in ['InTransit', 'PaymentPending']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = new_status
        
        if new_status == 'InTransit':
            order.picked_at = timezone.now()
        elif new_status == 'PaymentPending':
            # Rider has arrived at delivery location, waiting for payment
            pass
        
        order.save()
        
        OrderTracking.objects.create(
            order=order,
            status=new_status,
            message=request.data.get('message', f'Order status: {new_status}'),
            latitude=request.data.get('latitude'),
            longitude=request.data.get('longitude')
        )
        
        # NO SMS for status updates
        
        return Response({
            'message': 'Status updated successfully',
            'order': OrderSerializer(order).data
        })
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rider_start_delivery(request, order_id):
    """Rider starts delivery (Assigned → InTransit)"""
    if request.user.user_type != 'assistant':
        return Response({'error': 'Rider access only'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        order = Order.objects.get(id=order_id, assistant=request.user, status='Assigned')
        
        order.status = 'InTransit'
        order.picked_at = timezone.now()
        order.save()
        
        OrderTracking.objects.create(
            order=order,
            status='InTransit',
            message='Rider has picked up the item',
            latitude=request.data.get('latitude'),
            longitude=request.data.get('longitude')
        )
        
        return Response({
            'message': 'Delivery started',
            'order': OrderSerializer(order).data
        })
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found or wrong status'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rider_complete_delivery(request, order_id):
    """Rider completes delivery AFTER payment (PaymentPending → Completed with FINAL SMS)"""
    if request.user.user_type != 'assistant':
        return Response({'error': 'Rider access only'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        order = Order.objects.get(id=order_id, assistant=request.user)
        
        # Can only complete if payment is done (status should be PaymentPending and payment_status paid)
        if order.status != 'PaymentPending' or order.payment_status != 'paid':
            return Response({'error': 'Cannot complete - payment not confirmed'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'Completed'
        order.delivered_at = timezone.now()
        order.save()
        
        # Update profile stats
        order.user.profile.completed_orders += 1
        order.user.profile.save()
        
        OrderTracking.objects.create(
            order=order,
            status='Completed',
            message='Order delivered successfully',
            latitude=request.data.get('latitude'),
            longitude=request.data.get('longitude')
        )
        
        # Send FINAL SMS (SECOND AND LAST SMS IN LIFECYCLE)
        from core.sms_service import send_sms
        message = f"Your order {order.order_number} has been delivered successfully! Thank you for using Fagierrands."
        send_sms(order.user.phone_number, message)
        
        return Response({
            'message': 'Delivery completed successfully',
            'order': OrderSerializer(order).data
        })
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


# ========== SOS ALERTS ENDPOINTS ==========

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sos_alerts_list(request):
    """List all SOS alerts - returns empty for now"""
    return Response([])


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resolve_sos_alert(request, alert_id):
    """Resolve an SOS alert"""
    return Response({'message': 'SOS alert resolved', 'alert_id': alert_id})

