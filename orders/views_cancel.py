from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Order


class CancelOrderView(APIView):
    """
    Cancel a pending or assigned order (client only)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Cancel a pending or assigned order. Only the client who created the order can cancel it.",
        responses={
            200: openapi.Response(
                description="Order cancelled successfully",
                examples={
                    "application/json": {
                        "message": "Order cancelled successfully",
                        "order_id": 9,
                        "status": "cancelled",
                        "cancelled_at": "2026-04-12T22:30:15.123456+03:00"
                    }
                }
            ),
            400: "Order cannot be cancelled (already in progress or completed)",
            404: "Order not found"
        }
    )
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, client=request.user)
        
        # Only allow cancellation if order is pending or assigned
        if order.status not in ['Pending', 'Assigned', 'draft']:
            return Response({
                "error": f"Cannot cancel order with status '{order.status}'. Only pending, assigned, or draft orders can be cancelled."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Cancel the order
        order.status = 'Cancelled'
        order.cancelled_at = timezone.now()
        order.save()
        
        return Response({
            "message": "Order cancelled successfully",
            "order_id": order.id,
            "status": order.status,
            "cancelled_at": order.cancelled_at
        }, status=status.HTTP_200_OK)
