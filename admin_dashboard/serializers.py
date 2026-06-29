from rest_framework import serializers
from accounts.models import User, AssistantVerification
from orders.models import Order

class AdminUserSerializer(serializers.ModelSerializer):
    total_orders = serializers.IntegerField(source='profile.total_orders', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'user_type', 'is_verified', 'created_at', 'total_orders']

class AdminOrderSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    assistant_name = serializers.CharField(source='assistant.username', read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'

class RiderVerificationSerializer(serializers.ModelSerializer):
    assistant_name = serializers.CharField(source='assistant.username', read_only=True)
    
    class Meta:
        model = AssistantVerification
        fields = '__all__'
