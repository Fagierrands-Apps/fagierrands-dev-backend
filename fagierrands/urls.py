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
from django.http import HttpResponse
import os

def home_view(request):
    """Clean API landing page with environment indicator"""
    is_dev = os.getenv('DEBUG', 'False') == 'True'
    env_color = '#f59e0b' if is_dev else '#10b981'
    env_label = 'DEVELOPMENT' if is_dev else 'PRODUCTION'
    warning = '⚠️ This is a development server. Data may be unstable and reset periodically.' if is_dev else ''
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FagiErrands API - {env_label}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .container {{
                background: white;
                border-radius: 20px;
                padding: 50px;
                max-width: 600px;
                width: 100%;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }}
            h1 {{
                font-size: 2.5rem;
                color: #1f2937;
                margin-bottom: 10px;
            }}
            .version {{
                color: #6b7280;
                font-size: 0.9rem;
                margin-bottom: 30px;
            }}
            .badge {{
                display: inline-block;
                padding: 8px 16px;
                background: {env_color};
                color: white;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 600;
                margin-bottom: 30px;
            }}
            .status {{
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 30px;
                padding: 15px;
                background: #f3f4f6;
                border-radius: 10px;
            }}
            .status-dot {{
                width: 12px;
                height: 12px;
                background: #10b981;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
            }}
            .endpoints {{
                margin-top: 30px;
            }}
            .endpoint {{
                display: flex;
                justify-content: space-between;
                padding: 12px 0;
                border-bottom: 1px solid #e5e7eb;
            }}
            .endpoint:last-child {{ border-bottom: none; }}
            .endpoint-label {{ color: #6b7280; font-weight: 500; }}
            .endpoint-link {{ color: #667eea; text-decoration: none; }}
            .endpoint-link:hover {{ text-decoration: underline; }}
            .warning {{
                margin-top: 30px;
                padding: 15px;
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                border-radius: 5px;
                color: #92400e;
                font-size: 0.9rem;
            }}
            .footer {{
                margin-top: 40px;
                text-align: center;
                color: #9ca3af;
                font-size: 0.85rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>FagiErrands API</h1>
            <div class="version">Version 1.0</div>
            <div class="badge">{env_label}</div>
            
            <div class="status">
                <div class="status-dot"></div>
                <span>All systems operational</span>
            </div>
            
            <div class="endpoints">
                <div class="endpoint">
                    <span class="endpoint-label">API Documentation</span>
                    <a href="/swagger/" class="endpoint-link">/swagger/</a>
                </div>
                <div class="endpoint">
                    <span class="endpoint-label">API Endpoints</span>
                    <a href="/api/" class="endpoint-link">/api/</a>
                </div>
                <div class="endpoint">
                    <span class="endpoint-label">Admin Panel</span>
                    <a href="/admin/" class="endpoint-link">/admin/</a>
                </div>
            </div>
            
            {f'<div class="warning">{warning}</div>' if is_dev else ''}
            
            <div class="footer">
                © 2026 FagiErrands. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)

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
