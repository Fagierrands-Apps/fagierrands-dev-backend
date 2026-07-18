"""
Admin Dashboard Views - Statistics & Analytics
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta


@swagger_auto_schema(
    method='get',
    tags=['admin-dashboard'],
    responses={200: openapi.Response('Dashboard statistics')}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get comprehensive dashboard statistics"""
    from orders.models import Order
    from accounts.models import User
    
    # Date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        # Order Statistics
        'orders': {
            'total': Order.objects.count(),
            'pending': Order.objects.filter(status='Pending').count(),
            'assigned': Order.objects.filter(status='Assigned').count(),
            'in_progress': Order.objects.filter(status='InTransit').count(),
            'completed': Order.objects.filter(status='Completed').count(),
            'cancelled': Order.objects.filter(status='Cancelled').count(),
            'today': Order.objects.filter(created_at__date=today).count(),
            'this_week': Order.objects.filter(created_at__date__gte=week_ago).count(),
            'this_month': Order.objects.filter(created_at__date__gte=month_ago).count(),
        },
        
        # Revenue Statistics
        'revenue': {
            'total': Order.objects.filter(status='Completed').aggregate(Sum('total_price'))['total_price__sum'] or 0,
            'today': Order.objects.filter(status='Completed', completed_at__date=today).aggregate(Sum('total_price'))['total_price__sum'] or 0,
            'this_week': Order.objects.filter(status='Completed', completed_at__date__gte=week_ago).aggregate(Sum('total_price'))['total_price__sum'] or 0,
            'this_month': Order.objects.filter(status='Completed', completed_at__date__gte=month_ago).aggregate(Sum('total_price'))['total_price__sum'] or 0,
            'average_order': Order.objects.filter(status='Completed').aggregate(Avg('total_price'))['total_price__avg'] or 0,
        },
        
        # Handler Statistics
        'handlers': {
            'total': User.objects.filter(user_type='handler').count(),
            'verified': User.objects.filter(user_type='handler', is_verified=True).count(),
            'active': User.objects.filter(user_type='handler', is_active=True).count(),
            'pending_verification': User.objects.filter(user_type='handler', is_verified=False).count(),
            'with_orders': Order.objects.filter(assistant__isnull=False).values('assistant').distinct().count(),
        },
        
        # Client Statistics
        'clients': {
            'total': User.objects.filter(user_type='client').count(),
            'active': User.objects.filter(user_type='client', is_active=True).count(),
            'new_this_week': User.objects.filter(user_type='client', date_joined__date__gte=week_ago).count(),
            'new_this_month': User.objects.filter(user_type='client', date_joined__date__gte=month_ago).count(),
        },
        
        # System Health
        'system': {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'total_transactions': Order.objects.filter(status='Completed').count(),
            'success_rate': round((Order.objects.filter(status='Completed').count() / max(Order.objects.exclude(status='Draft').count(), 1)) * 100, 2),
        }
    }
    
    return Response(stats)
