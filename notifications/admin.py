from django.contrib import admin
from django.utils.html import format_html
from .models import Notification, PushToken


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)


@admin.register(PushToken)
class PushTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_type', 'token_preview', 'created_at', 'updated_at')
    list_filter = ('device_type', 'created_at')
    search_fields = ('user__username', 'token')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    
    def token_preview(self, obj):
        """Show first 50 characters of token"""
        return obj.token[:50] + '...' if len(obj.token) > 50 else obj.token
    token_preview.short_description = 'Token'

