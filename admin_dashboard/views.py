from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, AssistantVerification
from orders.models import Order
from .serializers import AdminUserSerializer, AdminOrderSerializer, RiderVerificationSerializer


def is_admin(user):
    return user.user_type in ['admin', 'handler']


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics"""
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    today = timezone.now().date()
    
    stats = {
        'total_users': User.objects.filter(user_type='user').count(),
        'total_riders': User.objects.filter(user_type='assistant').count(),
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='Pending').count(),
        'active_orders': Order.objects.filter(status__in=['Assigned', 'InTransit']).count(),
        'completed_today': Order.objects.filter(status='Completed', delivered_at__date=today).count(),
        'revenue_today': Order.objects.filter(status='Completed', delivered_at__date=today).aggregate(
            total=Sum('total_price'))['total'] or 0,
        'pending_verifications': AssistantVerification.objects.filter(status='pending').count(),
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_users(request):
    """Get all users with filters"""
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    users = User.objects.filter(user_type='user')
    
    # Filters
    search = request.query_params.get('search')
    if search:
        users = users.filter(Q(username__icontains=search) | Q(email__icontains=search) | Q(phone_number__icontains=search))
    
    serializer = AdminUserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_riders(request):
    """Get all riders"""
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    riders = User.objects.filter(user_type='assistant')
    serializer = AdminUserSerializer(riders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_orders(request):
    """Get all orders with filters"""
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    orders = Order.objects.all()
    
    # Filters
    status_filter = request.query_params.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    serializer = AdminOrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_verifications(request):
    """Get pending rider verifications"""
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    verifications = AssistantVerification.objects.filter(status='pending')
    serializer = RiderVerificationSerializer(verifications, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_rider(request, verification_id):
    """Approve rider verification"""
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        verification = AssistantVerification.objects.get(id=verification_id)
        verification.status = 'approved'
        verification.verified_by = request.user
        verification.admin_notes = request.data.get('notes', '')
        verification.save()
        
        # Log action
        AdminAction.objects.create(
            admin=request.user,
            action_type='rider_approved',
            description=f"Approved rider {verification.user.username}",
            target_model='AssistantVerification',
            target_id=verification_id
        )
        
        return Response({'message': 'Rider approved successfully'})
    except AssistantVerification.DoesNotExist:
        return Response({'error': 'Verification not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_rider(request, verification_id):
    """Reject rider verification"""
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        verification = AssistantVerification.objects.get(id=verification_id)
        verification.status = 'rejected'
        verification.verified_by = request.user
        verification.admin_notes = request.data.get('notes', '')
        verification.save()
        
        AdminAction.objects.create(
            admin=request.user,
            action_type='rider_rejected',
            description=f"Rejected rider {verification.user.username}",
            target_model='AssistantVerification',
            target_id=verification_id
        )
        
        return Response({'message': 'Rider rejected'})
    except AssistantVerification.DoesNotExist:
        return Response({'error': 'Verification not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def suspend_user(request, user_id):
    """Suspend a user"""
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
        user.is_active = False
        user.save()
        
        AdminAction.objects.create(
            admin=request.user,
            action_type='user_suspended',
            description=f"Suspended user {user.username}",
            target_model='User',
            target_id=user_id
        )
        
        return Response({'message': 'User suspended'})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activate_user(request, user_id):
    """Activate a user"""
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()
        
        AdminAction.objects.create(
            admin=request.user,
            action_type='user_activated',
            description=f"Activated user {user.username}",
            target_model='User',
            target_id=user_id
        )
        
        return Response({'message': 'User activated'})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    """Dashboard overview with key metrics"""
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    from orders.models import Order
    today = timezone.now().date()
    
    return Response({
        'total_users': User.objects.count(),
        'total_orders': Order.objects.count(),
        'active_riders': User.objects.filter(user_type='assistant', is_active=True).count(),
        'today_orders': Order.objects.filter(created_at__date=today).count(),
        'pending_verifications': AssistantVerification.objects.filter(status='pending').count()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def live_metrics(request):
    """Real-time metrics"""
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    from orders.models import Order
    from django.db.models import Count
    
    now = timezone.now()
    last_hour = now - timedelta(hours=1)
    
    return Response({
        'orders_last_hour': Order.objects.filter(created_at__gte=last_hour).count(),
        'active_riders': User.objects.filter(user_type='assistant', is_active=True).count(),
        'online_users': User.objects.filter(is_active=True).count(),
        'timestamp': now.isoformat()
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_metrics(request):
    """Calculate and update metrics"""
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    from orders.models import Order
    today = timezone.now().date()
    
    # Calculate daily metrics
    from admin_dashboard.models import DailyMetrics
    metrics, created = DailyMetrics.objects.get_or_create(
        date=today,
        defaults={
            'total_orders': Order.objects.filter(created_at__date=today).count(),
            'completed_orders': Order.objects.filter(created_at__date=today, status='Completed').count(),
            'new_users': User.objects.filter(date_joined__date=today).count(),
        }
    )
    
    return Response({'message': 'Metrics calculated', 'date': today})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_data(request):
    """Export dashboard data"""
    if not is_admin(request.user):
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    
    export_type = request.query_params.get('type', 'users')
    
    if export_type == 'users':
        users = User.objects.all().values('id', 'username', 'email', 'user_type', 'created_at')
        return Response({'data': list(users), 'type': 'users'})
    
    return Response({'message': 'Export prepared', 'type': export_type})
