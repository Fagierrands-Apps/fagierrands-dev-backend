from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views_stats import dashboard_stats as handler_dashboard_stats
from .viewsets import (
    DailyMetricsViewSet, UserRetentionViewSet, ServicePerformanceViewSet,
    CustomerSatisfactionViewSet, AdvertisementMetricsViewSet
)

router = DefaultRouter()
router.register('daily-metrics', DailyMetricsViewSet, basename='daily-metrics')
router.register('user-retention', UserRetentionViewSet, basename='user-retention')
router.register('service-performance', ServicePerformanceViewSet, basename='service-performance')
router.register('customer-satisfaction', CustomerSatisfactionViewSet, basename='customer-satisfaction')
router.register('advertisement-metrics', AdvertisementMetricsViewSet, basename='advertisement-metrics')

urlpatterns = [
    # Handler Dashboard Stats (NEW)
    path('handler-stats/', handler_dashboard_stats, name='handler-dashboard-stats'),  # GET /api/admin_dashboard/handler-stats/
    
    # Legacy endpoints
    path('stats/', views.dashboard_stats, name='dashboard-stats'),
    path('users/', views.all_users, name='all-users'),
    path('riders/', views.all_riders, name='all-riders'),
    path('orders/', views.all_orders, name='all-orders'),
    path('verifications/', views.pending_verifications, name='pending-verifications'),
    path('verifications/<int:verification_id>/approve/', views.approve_rider, name='approve-rider'),
    path('verifications/<int:verification_id>/reject/', views.reject_rider, name='reject-rider'),
    path('users/<int:user_id>/suspend/', views.suspend_user, name='suspend-user'),
    path('users/<int:user_id>/activate/', views.activate_user, name='activate-user'),
    
    # Dashboard overview
    path('overview/', views.dashboard_overview, name='dashboard-overview'),
    path('live-metrics/', views.live_metrics, name='live-metrics'),
    path('calculate-metrics/', views.calculate_metrics, name='calculate-metrics'),
    path('export/', views.export_data, name='export-data'),
    
    # Router URLs
    path('', include(router.urls)),
]
