from django.contrib import admin
from .models import (
    DailyMetrics, UserRetention, ServicePerformance,
    CustomerSatisfaction, AdvertisementMetrics
)


@admin.register(DailyMetrics)
class DailyMetricsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_orders', 'completed_orders', 'total_revenue', 'new_users', 'active_users')
    list_filter = ('date',)
    search_fields = ('date',)
    date_hierarchy = 'date'
    readonly_fields = ('created_at',)


@admin.register(UserRetention)
class UserRetentionAdmin(admin.ModelAdmin):
    list_display = ('date', 'cohort_month', 'users_count', 'retention_rate')
    list_filter = ('date', 'cohort_month')
    date_hierarchy = 'date'
    readonly_fields = ('created_at',)


@admin.register(ServicePerformance)
class ServicePerformanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'service_type', 'total_orders', 'avg_rating', 'revenue')
    list_filter = ('date', 'service_type')
    search_fields = ('service_type',)
    date_hierarchy = 'date'
    readonly_fields = ('created_at',)


@admin.register(CustomerSatisfaction)
class CustomerSatisfactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'avg_rating', 'total_reviews', 'positive_reviews', 'negative_reviews')
    list_filter = ('date',)
    date_hierarchy = 'date'
    readonly_fields = ('created_at',)


@admin.register(AdvertisementMetrics)
class AdvertisementMetricsAdmin(admin.ModelAdmin):
    list_display = ('date', 'platform', 'impressions', 'clicks', 'conversions', 'cost', 'revenue')
    list_filter = ('date', 'platform')
    search_fields = ('platform',)
    date_hierarchy = 'date'
    readonly_fields = ('created_at',)
