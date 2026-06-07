"""
Push Notification Service - FCM Integration
"""

import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_push_notification(user, title, message, data=None):
    """
    Send push notification via Firebase Cloud Messaging (FCM)
    """
    try:
        from notifications.models import PushToken
        
        # Get user's active push tokens
        tokens = PushToken.objects.filter(user=user, is_active=True).values_list('token', flat=True)
        
        if not tokens:
            logger.info(f"No push tokens for user {user.username}")
            return False
        
        if settings.DEBUG:
            print(f"\n{'='*60}")
            print(f"PUSH NOTIFICATION DEBUG")
            print(f"To: {user.username}")
            print(f"Title: {title}")
            print(f"Message: {message}")
            print(f"Data: {data}")
            print(f"{'='*60}\n")
            return True
        
        # FCM API call
        fcm_url = "https://fcm.googleapis.com/fcm/send"
        headers = {
            "Authorization": f"key={settings.FCM_SERVER_KEY}",
            "Content-Type": "application/json",
        }
        
        for token in tokens:
            payload = {
                "to": token,
                "notification": {
                    "title": title,
                    "body": message,
                    "sound": "default",
                },
                "data": data or {},
                "priority": "high",
            }
            
            response = requests.post(fcm_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"Push sent to {user.username}")
            else:
                logger.error(f"Push failed: {response.text}")
        
        return True
        
    except Exception as e:
        logger.error(f"Push notification error: {str(e)}")
        return False


def notify_order_update(order, title, message):
    """Send notification for order updates"""
    from notifications.views import create_notification
    
    # Create in-app notification
    create_notification(
        user=order.user,
        notification_type='order_update',
        title=title,
        message=message,
        data={'order_id': order.id, 'order_number': order.order_number}
    )
    
    # Send push notification
    send_push_notification(order.user, title, message, {'order_id': order.id})


def notify_rider_new_order(rider, order):
    """Notify rider of new order assignment"""
    from notifications.views import create_notification
    
    title = "New Order Assigned"
    message = f"Order {order.order_number} has been assigned to you"
    
    create_notification(
        user=rider,
        notification_type='order_assigned',
        title=title,
        message=message,
        data={'order_id': order.id}
    )
    
    send_push_notification(rider, title, message, {'order_id': order.id})
