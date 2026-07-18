"""
Accounts Models - Clean, no duplicates
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Extended User model"""
    USER_TYPE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Rider'),
        ('handler', 'Handler'),
        ('admin', 'Admin'),
        ('vendor', 'Vendor'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='user')
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=10, blank=True, null=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    account_manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_clients')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """Normalize phone number before saving"""
        from core.utils import normalize_phone_number
        if self.phone_number:
            self.phone_number = normalize_phone_number(self.phone_number)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class Profile(models.Model):
    """User profile with additional info"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True)
    wallet_points = models.IntegerField(default=0)
    total_orders = models.IntegerField(default=0)
    completed_orders = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.IntegerField(default=0)
    default_location = models.ForeignKey('locations.Location', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.username}"


class WalletTransaction(models.Model):
    """Wallet points transactions"""
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('redeem', 'Redeem'),
        ('bonus', 'Bonus'),
        ('refund', 'Refund'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_transactions')
    points = models.IntegerField()
    amount_equivalent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    reference = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.points} pts"


class AssistantVerification(models.Model):
    """Rider verification and documents"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    VEHICLE_TYPES = [
        ('motorcycle', 'Motorcycle'),
        ('bicycle', 'Bicycle'),
        ('car', 'Car'),
        ('van', 'Van'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='assistant_verification')
    id_number = models.CharField(max_length=50)
    id_photo = models.URLField(blank=True, null=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    vehicle_registration = models.CharField(max_length=50)
    vehicle_photo = models.URLField(blank=True, null=True)
    drivers_license = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()}"


class EmailVerification(models.Model):
    """Email verification tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verifications')
    token = models.CharField(max_length=100, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.email} - {self.token[:20]}"


class OTPVerification(models.Model):
    """OTP verification for phone numbers"""
    PURPOSE_CHOICES = [
        ('registration', 'Registration'),
        ('password_reset', 'Password Reset'),
        ('phone_verification', 'Phone Verification'),
    ]
    
    phone_number = models.CharField(max_length=17)
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES, default='registration')
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.phone_number} - {self.otp}"
