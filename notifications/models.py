"""
Notifications Models
"""

from django.db import models
from django.conf import settings


class Notification(models.Model):
    """In-app notifications"""
    NOTIFICATION_TYPES = [
        ('order_update', 'Order Update'),
        ('order_assigned', 'Order Assigned'),
        ('order_completed', 'Order Completed'),
        ('payment', 'Payment'),
        ('promotion', 'Promotion'),
        ('system', 'System'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class PushToken(models.Model):
    """FCM push notification tokens"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='push_tokens')
    token = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(max_length=20)  # android, ios, web
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.device_type}"


class EmailNotification(models.Model):
    """Email notification log"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.subject} - {self.user.email}"
