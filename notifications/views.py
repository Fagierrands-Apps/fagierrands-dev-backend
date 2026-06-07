from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Notification, PushToken
from .serializers import NotificationSerializer, PushTokenSerializer

@swagger_auto_schema(
    method='get',
    tags=['notifications'],
    responses={200: openapi.Response('Notifications list', NotificationSerializer(many=True))}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    """Get user notifications"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    serializer = NotificationSerializer(notifications, many=True)
    return Response({
        'notifications': serializer.data,
        'unread_count': unread_count
    })

@swagger_auto_schema(
    method='get',
    tags=['notifications'],
    responses={200: openapi.Response('Unread count')}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count(request):
    """Get unread notifications count"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return Response({'unread_count': count})

@swagger_auto_schema(
    method='post',
    tags=['notifications'],
    responses={200: openapi.Response('Marked as read')}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_as_read(request, notification_id):
    """Mark notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({'message': 'Marked as read'})
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='post',
    tags=['notifications'],
    responses={200: openapi.Response('All marked as read')}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response({'message': 'All notifications marked as read'})

@swagger_auto_schema(
    method='delete',
    tags=['notifications'],
    responses={204: openapi.Response('Deleted')}
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, notification_id):
    """Delete a notification"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='delete',
    tags=['notifications'],
    responses={204: openapi.Response('All deleted')}
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_all_notifications(request):
    """Delete all notifications"""
    Notification.objects.filter(user=request.user).delete()
    return Response({'message': 'All notifications deleted'}, status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(
    method='post',
    tags=['notifications'],
    request_body=PushTokenSerializer,
    responses={200: openapi.Response('Token registered')}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_push_token(request):
    """Register FCM/Expo push token"""
    serializer = PushTokenSerializer(data=request.data)
    if serializer.is_valid():
        PushToken.objects.update_or_create(
            user=request.user,
            token=serializer.validated_data['token'],
            defaults={
                'device_type': serializer.validated_data.get('device_type', 'mobile'),
                'is_active': True
            }
        )
        return Response({'message': 'Token registered successfully'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    tags=['notifications'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['token'],
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING, description='Push token'),
        }
    ),
    responses={200: openapi.Response('Token unregistered')}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unregister_push_token(request):
    """Unregister push token"""
    token = request.data.get('token')
    PushToken.objects.filter(user=request.user, token=token).update(is_active=False)
    return Response({'message': 'Token unregistered'})


# Helper function to create notifications
def create_notification(user, notification_type, title, message, data=None):
    """Create in-app notification"""
    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        data=data
    )
