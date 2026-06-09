"""
Main URL Configuration for Fagierrands API
Clean structure - organized by feature
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import JsonResponse

def home_view(request):
    return JsonResponse({'message': 'Fagierrands API', 'version': 'v1'})

# API Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Fagierrands API",
        default_version='v1',
        description="Clean API for Fagierrands - Errand delivery platform",
        terms_of_service="https://fagierrands.com/terms/",
        contact=openapi.Contact(email="support@fagierrands.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[],
)

urlpatterns = [
    # Homepage
    path('', home_view, name='home'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API Endpoints
    path('api/accounts/', include('accounts.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/locations/', include('locations.urls')),
    path('api/notifications/', include('notifications.urls')),
    
    # Dashboard (without api prefix to match old backend)
    path('dashboard/', include('admin_dashboard.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
