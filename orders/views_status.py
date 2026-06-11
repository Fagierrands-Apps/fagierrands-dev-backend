from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from orders.models import Order
import logging

logger = logging.getLogger(__name__)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """Update order status"""
    try:
        order = Order.objects.get(id=order_id)
        new_status = request.data.get('status')
        
        if not new_status:
            return Response({'error': 'status is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate status
        valid_statuses = ['Draft', 'Pending', 'Assigned', 'Queued', 'InTransit', 'Completed', 'Cancelled']
        if new_status not in valid_statuses:
            return Response({'error': f'Invalid status. Must be one of: {valid_statuses}'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = order.status
        order.status = new_status
        order.save()
        
        logger.info(f"Order {order.order_number} status changed: {old_status} -> {new_status}")
        
        return Response({
            'message': 'Status updated successfully',
            'order_id': order.id,
            'order_number': order.order_number,
            'old_status': old_status,
            'new_status': new_status
        })
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error updating order status: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
