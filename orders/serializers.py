from rest_framework import serializers
from .models import Order, OrderTracking, OrderRating, Payment
from accounts.serializers import UserSerializer

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    assistant = UserSerializer(read_only=True)
    client_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['order_number', 'user', 'created_at', 'updated_at']
    
    def get_client_status(self, obj):
        """Return client-friendly status - Queued orders appear as Assigned"""
        if obj.status == 'Queued':
            return 'Assigned'
        return obj.status

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['pickup_address', 'pickup_lat', 'pickup_lng', 'delivery_address', 
                  'delivery_lat', 'delivery_lng', 'item_description', 'item_weight', 
                  'delivery_notes', 'payment_method']

class OrderTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTracking
        fields = '__all__'
        read_only_fields = ['order', 'created_at']

class OrderRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderRating
        fields = '__all__'
        read_only_fields = ['user', 'assistant', 'order', 'created_at']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount', 'final_amount', 'payment_method', 'status',
            'transaction_id', 'transaction_reference',
            'mpesa_checkout_request_id', 'mpesa_merchant_request_id',
            'mpesa_receipt_number', 'mpesa_transaction_date',
            'mpesa_phone_number', 'mpesa_transaction_id',
            'created_at', 'phone_number', 'email'
        ]
        read_only_fields = [
            'transaction_id', 'mpesa_checkout_request_id', 'mpesa_merchant_request_id',
            'mpesa_receipt_number', 'mpesa_transaction_date',
            'mpesa_phone_number', 'mpesa_transaction_id', 'created_at', 'status'
        ]

class InitiatePaymentSerializer(serializers.ModelSerializer):
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)
    phone_number = serializers.CharField(max_length=20, required=False)
    email = serializers.EmailField(required=False)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    redeem_points = serializers.IntegerField(required=False, default=0, min_value=0)
    
    class Meta:
        model = Payment
        fields = ['order', 'amount', 'payment_method', 'phone_number', 'email', 'redeem_points']
    
    def validate(self, data):
        if data['payment_method'] in ['ncba', 'mpesa'] and not data.get('phone_number'):
            raise serializers.ValidationError({"phone_number": "Phone number is required for NCBA payments"})
        
        # Check order status - only PaymentPending orders can initiate payment
        order = data['order']
        if order.status != 'PaymentPending':
            raise serializers.ValidationError({
                "order": f"Payment can only be initiated for orders with status 'PaymentPending'. Current status: {order.status}"
            })
        
        return data
    
    def create(self, validated_data):
        redeem_points = validated_data.pop('redeem_points', 0)
        
        # Generate unique transaction reference
        import uuid
        validated_data['transaction_reference'] = f"PAY-{uuid.uuid4().hex[:12].upper()}"
        
        # Calculate discount and final amount
        discount = redeem_points
        validated_data['points_used'] = redeem_points
        validated_data['discount_amount'] = discount
        validated_data['final_amount'] = max(0, validated_data['amount'] - discount)
        
        return super().create(validated_data)
