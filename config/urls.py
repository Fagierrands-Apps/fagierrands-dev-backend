"""
URL configuration for FagiErrands project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="FagiErrands API",
        default_version='v1',
        description="API documentation for FagiErrands",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    # path('api/orders/', include('orders.urls')),  # Temporarily disabled due to import issues
    path('api/locations/', include('locations.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/marketplace/', include('marketplace.urls')),
    path('api/admin-dashboard/', include('admin_dashboard.urls')),
    path('api/voice/', include('voice.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
