from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile, WalletTransaction, AssistantVerification
from core.utils import normalize_phone_number

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'user_type', 'first_name', 'last_name', 'is_verified', 'email_verified']
        read_only_fields = ['id', 'is_verified', 'email_verified', 'user_type']


class AdminUserTypeSerializer(serializers.ModelSerializer):
    """Admin-only serializer for changing user types"""
    class Meta:
        model = User
        fields = ['id', 'username', 'phone_number', 'user_type']
        read_only_fields = ['id', 'username', 'phone_number']

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    user_type = serializers.CharField(default='user', required=False)  # Accept in request but ignore
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'user_type', 'phone_number', 'referral_code']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8},
            'username': {'validators': []},
            'email': {'validators': []},
        }
    
    def validate_phone_number(self, value):
        """Normalize phone number"""
        normalized = normalize_phone_number(value)
        if not normalized or not normalized.startswith('254') or len(normalized) != 12:
            raise serializers.ValidationError("Invalid Kenyan phone number. Use format: 0796605409 or 254796605409")
        
        # Check if phone number already exists
        if User.objects.filter(phone_number=normalized).exists():
            raise serializers.ValidationError("This phone number is already registered")
        
        return normalized
    
    def validate_password(self, value):
        """Validate password strength"""
        import re
        
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character (!@#$%^&*)")
        
        return value
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "Passwords don't match"})
        return data
    
    def create(self, validated_data):
        from django.db import IntegrityError
        
        validated_data.pop('password2')
        # Force user_type to 'user' for all registrations
        validated_data['user_type'] = 'user'
        
        try:
            user = User.objects.create_user(**validated_data)
            Profile.objects.create(user=user)
            return user
        except IntegrityError as e:
            if 'phone_number' in str(e):
                raise serializers.ValidationError({"phone_number": "This phone number is already registered"})
            elif 'username' in str(e):
                raise serializers.ValidationError({"username": "This username is already taken"})
            elif 'email' in str(e):
                raise serializers.ValidationError({"email": "This email is already registered"})
            else:
                raise serializers.ValidationError({"error": "Registration failed. Please try again"})

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['total_orders', 'completed_orders', 'rating', 'total_ratings']

class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = '__all__'
        read_only_fields = ['user', 'created_at']
