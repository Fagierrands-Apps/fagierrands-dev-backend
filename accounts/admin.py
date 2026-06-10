from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Profile, OTPVerification, AssistantVerification, EmailVerification, WalletTransaction


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        (_('Status'), {'fields': ('user_type', 'is_verified')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone_number', 'email', 'password1', 'password2', 'user_type'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_verified', 'is_staff')
    list_filter = ('user_type', 'is_verified', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    
    def delete_queryset(self, request, queryset):
        """Override to handle cascading deletes properly"""
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
        for obj in queryset:
            OutstandingToken.objects.filter(user=obj).delete()
            obj.delete()
    
    def delete_model(self, request, obj):
        """Override to handle cascading deletes properly"""
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
        OutstandingToken.objects.filter(user=obj).delete()
        obj.delete()


@admin.register(AssistantVerification)
class AssistantVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle_type', 'status', 'created_at', 'verified_at')
    list_filter = ('status', 'vehicle_type', 'created_at')
    search_fields = ('user__username', 'vehicle_registration', 'id_number')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'is_used', 'created_at', 'expires_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'user__email', 'token')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)


class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'otp', 'purpose', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'purpose', 'created_at')
    search_fields = ('phone_number', 'otp')
    readonly_fields = ('created_at',)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'wallet_points', 'rating', 'total_orders')
    search_fields = ('user__username', 'user__email', 'bio')


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'transaction_type', 'reference', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user__username', 'reference')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(OTPVerification, OTPVerificationAdmin)
