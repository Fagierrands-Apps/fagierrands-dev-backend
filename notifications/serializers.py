from rest_framework import serializers
from .models import Notification, PushToken

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

class PushTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushToken
        fields = ['token', 'device_type']
