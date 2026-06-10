"""
Orders Models - Clean, no duplicates
"""

from django.db import models
from django.conf import settings
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class OrderType(models.Model):
    """Order type: Normal Delivery (parcel) or Cargo"""
    name = models.CharField(max_length=50)
    description = models.TextField()
    code = models.CharField(max_length=20, unique=True)  # 'parcel' or 'cargo'
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class Order(models.Model):
    """Order model"""
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Pending', 'Pending'),
        ('Assigned', 'Assigned'),
        ('Queued', 'Queued'),
        ('InTransit', 'In Transit'),
        ('PaymentPending', 'Payment Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('wallet', 'Wallet Points'),
        ('card', 'Card'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('initiated', 'Initiated'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    assistant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders')
    order_type = models.ForeignKey(OrderType, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Order details
    title = models.CharField(max_length=200, blank=True)
    item_description = models.TextField(blank=True)
    item_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    delivery_notes = models.TextField(blank=True)
    
    # Locations
    pickup_address = models.TextField(blank=True)
    pickup_lat = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    pickup_lng = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    delivery_address = models.TextField(blank=True)
    delivery_lat = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    delivery_lng = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    
    # Receiver info
    receiver_name = models.CharField(max_length=100, blank=True)
    receiver_phone = models.CharField(max_length=17, blank=True)
    estimated_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Pricing
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=200)
    extra_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=200)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='mpesa')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    # queue_position = models.IntegerField(null=True, blank=True)  # 0=active, 1-2=queued  # TODO: Run migration first
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    picked_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Auto-generate simple order_number if not provided
        if not self.order_number:
            self.order_number = f"ORD-{self.id if self.id else 'NEW'}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.order_number} - {self.status}"


class OrderImage(models.Model):
    """Order item images"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.order.order_number}"


class OrderTracking(models.Model):
    """Order tracking history"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=50)
    message = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class OrderRating(models.Model):
    """Order rating by user"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='rating')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assistant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_ratings')
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.order.order_number} - {self.rating}★"


class Payment(models.Model):
    """Payment transactions"""
    PAYMENT_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Cancelled', 'Cancelled'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('ncba', 'NCBA Till'),
        ('mpesa', 'M-Pesa'),
        ('card', 'Card'),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    client = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    points_used = models.IntegerField(default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='ncba')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    transaction_reference = models.CharField(max_length=255, blank=True, null=True)
    mpesa_checkout_request_id = models.CharField(max_length=255, blank=True, null=True)
    mpesa_merchant_request_id = models.CharField(max_length=255, blank=True, null=True)
    mpesa_receipt_number = models.CharField(max_length=255, blank=True, null=True)
    mpesa_transaction_date = models.CharField(max_length=50, blank=True, null=True)
    mpesa_phone_number = models.CharField(max_length=20, blank=True, null=True)
    mpesa_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        order_id = self.order.id if hasattr(self, 'order') and self.order else 'N/A'
        ref = self.transaction_reference or 'N/A'
        return f"Payment {ref} for Order {order_id}"



# Additional Order Models

class Banks(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Banks"

    def __str__(self):
        return self.name


class BankingOrder(models.Model):
    TRANSACTION_TYPES = (('deposit', 'Deposit'), ('withdrawal', 'Withdrawal'), ('transfer', 'Transfer'))
    STATUS_CHOICES = (('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed'))
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='banking_orders')
    bank = models.ForeignKey(Banks, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    account_number = models.CharField(max_length=50)
    transaction_details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"


class CargoDeliveryDetails(models.Model):
    SIZE_CHOICES = (('small', 'Small'), ('medium', 'Medium'), ('large', 'Large'), ('extra_large', 'Extra Large'))
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='cargo_details')
    cargo_weight = models.DecimalField(max_digits=8, decimal_places=2)
    cargo_size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    need_helpers = models.BooleanField(default=False)
    helpers_count = models.IntegerField(default=0)
    special_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Cargo Delivery Details"

    def __str__(self):
        return f"Cargo for Order #{self.order.order_number}"


class CargoPhoto(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='cargo_photos')
    image_url = models.URLField()
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for Order #{self.order.order_number}"


class CargoValue(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='cargo_value')
    value = models.DecimalField(max_digits=12, decimal_places=2)
    visible_to_handler_only = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Value for Order #{self.order.order_number}"


class OrderReview(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for Order #{self.order.order_number}"


class ClientFeedback(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='client_feedback')
    delivered_promptly = models.BooleanField(default=True)
    professionalism = models.IntegerField()
    service_quality = models.IntegerField()
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Client Feedback - Order #{self.order.order_number}"


class RiderFeedback(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='rider_feedback')
    clear_communication = models.BooleanField(default=True)
    payment_timeliness = models.IntegerField()
    interaction_quality = models.IntegerField()
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rider Feedback - Order #{self.order.order_number}"


class HandymanServiceType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    facilitation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=500)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class HandymanOrder(models.Model):
    STATUS_CHOICES = (('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled'))
    
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='handyman_orders_as_client')
    assistant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='handyman_orders_as_assistant')
    service_type = models.ForeignKey(HandymanServiceType, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    scheduled_date = models.DateField()
    scheduled_time_slot = models.CharField(max_length=50)
    facilitation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=500)
    facilitation_fee_paid = models.BooleanField(default=False)
    service_quote = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    approved_service_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_payment_complete = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Handyman #{self.id} - {self.service_type}"


class HandymanOrderImage(models.Model):
    order = models.ForeignKey(HandymanOrder, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for Handyman Order #{self.order.id}"


class OrderPrepayment(models.Model):
    STATUS_CHOICES = (('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled'))
    
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='order_prepayments')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='prepayments')
    order_type = models.ForeignKey(OrderType, on_delete=models.CASCADE)
    transaction_reference = models.CharField(max_length=100, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prepayment {self.transaction_reference}"


class Referral(models.Model):
    referrer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referrals_made')
    referred_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referred_by_users')
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    redeemed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.referrer.username} referred {self.referred_user.username}"


class ReportIssue(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reported_issues')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField()
    incident_timestamp = models.DateTimeField()
    reported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Issue for Order #{self.order.order_number}"


class OrderVideo(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='videos')
    video_url = models.URLField()
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Video for Order #{self.order.order_number}"


class ShoppingItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shopping_items')
    name = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.order.order_number}"


class TrackingWaypoint(models.Model):
    tracking = models.ForeignKey(OrderTracking, on_delete=models.CASCADE, related_name='waypoints')
    waypoint_type = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    order_index = models.IntegerField(default=0)
    arrival_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order_index']

    def __str__(self):
        return f"Waypoint: {self.name}"


class TrackingEvent(models.Model):
    tracking = models.ForeignKey(OrderTracking, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.event_type} at {self.timestamp}"


class TrackingLocationHistory(models.Model):
    tracking = models.ForeignKey(OrderTracking, on_delete=models.CASCADE, related_name='location_history')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Tracking Location Histories"

    def __str__(self):
        return f"Location at {self.timestamp}"
