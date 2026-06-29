from django.contrib import admin
from .models import (
    Vendor, Product, ProductReview, VendorReview,
    Cart, CartItem, MarketplaceOrder, MarketplaceOrderItem
)


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'user', 'status', 'is_verified', 'average_rating', 'created_at')
    list_filter = ('status', 'is_verified', 'created_at')
    search_fields = ('shop_name', 'user__username', 'phone_number')
    date_hierarchy = 'created_at'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'category', 'price', 'quantity_available', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('name', 'vendor__shop_name', 'category')
    date_hierarchy = 'created_at'


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'reviewer__username')
    date_hierarchy = 'created_at'


@admin.register(VendorReview)
class VendorReviewAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('vendor__shop_name', 'reviewer__username')
    date_hierarchy = 'created_at'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username',)
    date_hierarchy = 'created_at'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'created_at')
    search_fields = ('cart__user__username', 'product__name')
    date_hierarchy = 'created_at'


@admin.register(MarketplaceOrder)
class MarketplaceOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__username')
    date_hierarchy = 'created_at'


@admin.register(MarketplaceOrderItem)
class MarketplaceOrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'created_at')
    search_fields = ('order__order_number', 'product__name')
    date_hierarchy = 'created_at'
