from django.contrib import admin
from .models import (
    Order, OrderType, OrderImage, OrderTracking, OrderRating, Payment,
    Banks, BankingOrder, CargoDeliveryDetails, CargoPhoto, CargoValue,
    OrderReview, ClientFeedback, RiderFeedback, HandymanServiceType,
    HandymanOrder, HandymanOrderImage, OrderPrepayment, Referral,
    ReportIssue, OrderVideo, ShoppingItem, TrackingWaypoint,
    TrackingEvent, TrackingLocationHistory
)


@admin.register(OrderType)
class OrderTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_number', 'user', 'assistant', 'order_type', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'order_type', 'created_at', 'payment_status')
    search_fields = ('order_number', 'title', 'user__username', 'assistant__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'order_number')


@admin.register(OrderImage)
class OrderImageAdmin(admin.ModelAdmin):
    list_display = ('order', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('order__order_number',)
    date_hierarchy = 'uploaded_at'


@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'latitude', 'longitude', 'created_at')
    search_fields = ('order__order_number',)
    date_hierarchy = 'created_at'


@admin.register(OrderRating)
class OrderRatingAdmin(admin.ModelAdmin):
    list_display = ('order', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('order__order_number', 'comment')
    date_hierarchy = 'created_at'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'get_order_number', 'amount', 'phone_number', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('transaction_id', 'phone_number', 'order__order_number')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    
    def get_order_number(self, obj):
        return obj.order.order_number if obj.order else None
    get_order_number.short_description = 'Order #'


@admin.register(Banks)
class BanksAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')


@admin.register(BankingOrder)
class BankingOrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'bank', 'transaction_type', 'amount', 'status', 'scheduled_date', 'created_at')
    list_filter = ('status', 'transaction_type', 'bank', 'created_at')
    search_fields = ('user__username', 'account_number')
    date_hierarchy = 'created_at'


@admin.register(CargoDeliveryDetails)
class CargoDeliveryDetailsAdmin(admin.ModelAdmin):
    list_display = ('order', 'cargo_weight', 'cargo_size', 'need_helpers', 'helpers_count')
    list_filter = ('cargo_size', 'need_helpers')
    search_fields = ('order__order_number',)


@admin.register(CargoPhoto)
class CargoPhotoAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'uploaded_at')
    search_fields = ('order__order_number',)
    date_hierarchy = 'uploaded_at'


@admin.register(CargoValue)
class CargoValueAdmin(admin.ModelAdmin):
    list_display = ('order', 'value', 'visible_to_handler_only')
    list_filter = ('visible_to_handler_only',)
    search_fields = ('order__order_number',)


@admin.register(OrderReview)
class OrderReviewAdmin(admin.ModelAdmin):
    list_display = ('order', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('order__order_number',)
    date_hierarchy = 'created_at'


@admin.register(ClientFeedback)
class ClientFeedbackAdmin(admin.ModelAdmin):
    list_display = ('order', 'delivered_promptly', 'professionalism', 'service_quality', 'created_at')
    list_filter = ('delivered_promptly', 'created_at')
    search_fields = ('order__order_number',)
    date_hierarchy = 'created_at'


@admin.register(RiderFeedback)
class RiderFeedbackAdmin(admin.ModelAdmin):
    list_display = ('order', 'clear_communication', 'payment_timeliness', 'interaction_quality', 'created_at')
    list_filter = ('clear_communication', 'created_at')
    search_fields = ('order__order_number',)
    date_hierarchy = 'created_at'


@admin.register(HandymanServiceType)
class HandymanServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'facilitation_fee', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(HandymanOrder)
class HandymanOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'assistant', 'service_type', 'status', 'facilitation_fee_paid', 'final_payment_complete', 'created_at')
    list_filter = ('status', 'facilitation_fee_paid', 'final_payment_complete', 'created_at')
    search_fields = ('client__username', 'assistant__username')
    date_hierarchy = 'created_at'


@admin.register(HandymanOrderImage)
class HandymanOrderImageAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'uploaded_at')
    search_fields = ('order__id',)
    date_hierarchy = 'uploaded_at'


@admin.register(OrderPrepayment)
class OrderPrepaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_reference', 'client', 'order_type', 'status', 'total_amount', 'deposit_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('transaction_reference', 'client__username')
    date_hierarchy = 'created_at'


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referred_user', 'discount_amount', 'redeemed', 'created_at')
    list_filter = ('redeemed', 'created_at')
    search_fields = ('referrer__username', 'referred_user__username')
    date_hierarchy = 'created_at'


@admin.register(ReportIssue)
class ReportIssueAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'incident_timestamp', 'reported_at')
    search_fields = ('order__order_number', 'user__username')
    date_hierarchy = 'reported_at'


@admin.register(OrderVideo)
class OrderVideoAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'uploaded_at')
    search_fields = ('order__order_number',)
    date_hierarchy = 'uploaded_at'


@admin.register(ShoppingItem)
class ShoppingItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'quantity', 'price', 'created_at')
    search_fields = ('name', 'order__order_number')
    date_hierarchy = 'created_at'


@admin.register(TrackingWaypoint)
class TrackingWaypointAdmin(admin.ModelAdmin):
    list_display = ('tracking', 'waypoint_type', 'name', 'order_index', 'arrival_time')
    list_filter = ('waypoint_type',)
    search_fields = ('name', 'tracking__order__order_number')


@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ('tracking', 'event_type', 'timestamp')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('tracking__order__order_number', 'event_type')
    date_hierarchy = 'timestamp'


@admin.register(TrackingLocationHistory)
class TrackingLocationHistoryAdmin(admin.ModelAdmin):
    list_display = ('tracking', 'latitude', 'longitude', 'timestamp')
    search_fields = ('tracking__order__order_number',)
    date_hierarchy = 'timestamp'
