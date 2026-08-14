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
from django.http import HttpResponseNotFound, HttpResponse, JsonResponse

def robots_txt(request):
    return HttpResponse("User-agent: *\nDisallow: /api/\nDisallow: /admin/\nAllow: /\n", content_type="text/plain")

def favicon(request):
    return HttpResponse(status=204)  # No content — stops 404 noise
import os

def health_view(request):
    """Public health check endpoint for uptime monitors"""
    from django.db import connection
    try:
        connection.ensure_connection()
        db_status = "ok"
    except Exception:
        db_status = "error"

    status = "ok" if db_status == "ok" else "degraded"
    code = 200 if status == "ok" else 503
    return JsonResponse({
        "status": status,
        "db": db_status,
        "env": "production" if not os.getenv('DEBUG', 'False') == 'True' else "development",
    }, status=code)


def home_view(request):
    is_dev = os.getenv('DEBUG', 'False') == 'True'
    env_label = 'DEVELOPMENT' if is_dev else 'PRODUCTION'
    env_color = '#f59e0b' if is_dev else '#22c55e'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FagiErrands API</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg: #0a0a0f;
    --surface: #111118;
    --border: rgba(255,255,255,0.07);
    --text: #e2e8f0;
    --muted: #64748b;
    --accent: #6366f1;
    --accent-glow: rgba(99,102,241,0.25);
    --green: #22c55e;
    --env: {env_color};
  }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    min-height: 100vh;
    display: grid;
    place-items: center;
    padding: 24px;
  }}

  /* subtle grid background */
  body::before {{
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(99,102,241,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(99,102,241,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
  }}

  .card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 48px;
    width: 100%;
    max-width: 520px;
    position: relative;
    overflow: hidden;
  }}

  /* top accent line */
  .card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
  }}

  /* glow blob */
  .card::after {{
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 220px; height: 220px;
    background: var(--accent-glow);
    border-radius: 50%;
    filter: blur(60px);
    pointer-events: none;
  }}

  .logo-row {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 32px;
  }}

  .logo-icon {{
    width: 44px; height: 44px;
    background: linear-gradient(135deg, var(--accent), #818cf8);
    border-radius: 12px;
    display: grid;
    place-items: center;
    font-size: 20px;
    flex-shrink: 0;
  }}

  .logo-text {{
    font-size: 1.25rem;
    font-weight: 700;
    letter-spacing: -0.02em;
  }}

  .logo-text span {{ color: var(--accent); }}

  .env-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    background: color-mix(in srgb, var(--env) 12%, transparent);
    border: 1px solid color-mix(in srgb, var(--env) 30%, transparent);
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--env);
    letter-spacing: 0.08em;
    margin-left: auto;
  }}

  .env-badge::before {{
    content: '';
    width: 6px; height: 6px;
    background: var(--env);
    border-radius: 50%;
  }}

  .headline {{
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1.15;
    margin-bottom: 10px;
  }}

  .headline span {{
    background: linear-gradient(90deg, var(--accent), #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }}

  .sub {{
    color: var(--muted);
    font-size: 0.9rem;
    line-height: 1.6;
    margin-bottom: 32px;
  }}

  .status-row {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    background: rgba(34,197,94,0.06);
    border: 1px solid rgba(34,197,94,0.15);
    border-radius: 10px;
    margin-bottom: 28px;
    font-size: 0.85rem;
    color: var(--green);
    font-weight: 500;
  }}

  .pulse {{
    width: 8px; height: 8px;
    background: var(--green);
    border-radius: 50%;
    flex-shrink: 0;
    box-shadow: 0 0 0 0 rgba(34,197,94,0.4);
    animation: ping 1.8s ease-in-out infinite;
  }}

  @keyframes ping {{
    0%, 100% {{ box-shadow: 0 0 0 0 rgba(34,197,94,0.4); }}
    50% {{ box-shadow: 0 0 0 6px rgba(34,197,94,0); }}
  }}

  .links {{
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}

  .link-item {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 16px;
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    border-radius: 12px;
    text-decoration: none;
    color: var(--text);
    font-size: 0.875rem;
    font-weight: 500;
    transition: border-color 0.2s, background 0.2s;
  }}

  .link-item:hover {{
    border-color: rgba(99,102,241,0.4);
    background: rgba(99,102,241,0.05);
  }}

  .link-left {{ display: flex; align-items: center; gap: 10px; }}

  .link-icon {{
    width: 30px; height: 30px;
    background: rgba(99,102,241,0.1);
    border-radius: 8px;
    display: grid;
    place-items: center;
    font-size: 14px;
  }}

  .link-arrow {{
    color: var(--muted);
    font-size: 0.75rem;
    transition: color 0.2s, transform 0.2s;
  }}

  .link-item:hover .link-arrow {{
    color: var(--accent);
    transform: translateX(2px);
  }}

  .footer {{
    margin-top: 32px;
    padding-top: 20px;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.75rem;
    color: var(--muted);
  }}

  .dev-warning {{
    margin-bottom: 20px;
    padding: 12px 16px;
    background: rgba(245,158,11,0.07);
    border: 1px solid rgba(245,158,11,0.2);
    border-radius: 10px;
    font-size: 0.8rem;
    color: #fbbf24;
    line-height: 1.5;
  }}
</style>
</head>
<body>
<div class="card">
  <div class="logo-row">
    <div class="logo-icon">🚀</div>
    <div class="logo-text">Fagi<span>Errands</span></div>
    <div class="env-badge">{env_label}</div>
  </div>

  <div class="headline">Errand Delivery<br><span>API Server</span></div>
  <p class="sub">Backend infrastructure powering the FagiErrands platform — orders, payments, locations, and notifications.</p>

  {'<div class="dev-warning">⚠️ Development server — data may be reset periodically.</div>' if is_dev else ''}

  <div class="status-row">
    <div class="pulse"></div>
    All systems operational
  </div>

  <div class="links">
    <a href="/swagger/" class="link-item">
      <div class="link-left">
        <div class="link-icon">📄</div>
        API Documentation
      </div>
      <span class="link-arrow">→</span>
    </a>
    <a href="/redoc/" class="link-item">
      <div class="link-left">
        <div class="link-icon">📚</div>
        ReDoc Reference
      </div>
      <span class="link-arrow">→</span>
    </a>
    <a href="/health/" class="link-item">
      <div class="link-left">
        <div class="link-icon">💓</div>
        Health Check
      </div>
      <span class="link-arrow">→</span>
    </a>
    <a href="/admin/" class="link-item">
      <div class="link-left">
        <div class="link-icon">🔐</div>
        Admin Panel
      </div>
      <span class="link-arrow">→</span>
    </a>
  </div>

  <div class="footer">
    <span>© 2026 FagiErrands</span>
    <span>v1.0</span>
  </div>
</div>
</body>
</html>"""
    return HttpResponse(html)

from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

# API Documentation — restricted to authenticated users only.
# Accepts both Django admin session AND JWT Bearer tokens.
# To access: log into /admin/ first, then open /swagger/ — session carries over.
# Logging out of /admin/ immediately revokes access to /swagger/ too.
schema_view = get_schema_view(
    openapi.Info(
        title="Fagierrands API",
        default_version='v1',
        description="Clean API for Fagierrands - Errand delivery platform",
        terms_of_service="https://fagierrands.com/terms/",
        contact=openapi.Contact(email="support@fagierrands.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=False,
    permission_classes=[permissions.IsAuthenticated],
    authentication_classes=[SessionAuthentication, JWTAuthentication],
)

urlpatterns = [
    # Homepage
    path('', home_view, name='home'),

    # Noise suppressors
    path('robots.txt', robots_txt),
    path('favicon.ico', favicon),
    
    # Health check (public, no auth)
    path('health/', health_view, name='health'),
    
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
