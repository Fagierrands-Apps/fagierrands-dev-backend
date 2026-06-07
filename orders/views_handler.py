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
from orders.models import Order
from orders.serializers import OrderSerializer
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
    """List all orders with optional status filter"""
    status_filter = request.query_params.get('status')
    
    orders = Order.objects.all().select_related('user', 'assistant', 'order_type').order_by('-created_at')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
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
    """Assign order to a rider"""
    try:
        order = Order.objects.get(id=order_id)
        rider_id = request.data.get('rider_id')
        
        if not rider_id:
            return Response({'error': 'rider_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        rider = User.objects.get(id=rider_id, user_type='handler')
        
        order.assistant = rider
        order.status = 'assigned'
        order.assigned_at = timezone.now()
        order.save()
        
        # Send notification to rider (optional)
        from core.sms_service import send_sms
        try:
            phone = rider.phone_number.replace('+', '')
            short_order_id = str(order.id)[-6:].zfill(6)
            message = f"New order #{short_order_id} assigned to you! From: {order.pickup_address}. To: {order.delivery_address}. Amount: KES {order.total_price}"
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
        'pending_orders': Order.objects.filter(status='pending').count(),
        'assigned_orders': Order.objects.filter(status='assigned').count(),
        'in_progress_orders': Order.objects.filter(status='in_progress').count(),
        'completed_orders': Order.objects.filter(status='completed').count(),
        'cancelled_orders': Order.objects.filter(status='cancelled').count(),
        'total_revenue': Order.objects.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0,
    }
    
    return Response(stats)
