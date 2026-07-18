"""
Accounts URLs - Authentication endpoints
"""

from django.urls import path
from . import views
from .views_handler import (
    handler_get_clients, handler_assign_client, handler_create_order_for_client,
    handler_confirm_order_for_client, handler_get_client_orders,
    handler_cancel_order, handler_dashboard_stats,
    list_handlers, handler_detail, verify_handler, available_handlers, handler_stats,
    handler_get_clients as handler_get_all_clients
)

urlpatterns = [
    # Handler Dashboard Endpoints (NEW)
    path('handlers/', list_handlers, name='list-handlers'),  # GET /api/accounts/handlers/
    path('handlers/<int:handler_id>/', handler_detail, name='handler-detail'),  # GET /api/accounts/handlers/{id}/
    path('handlers/<int:handler_id>/verify/', verify_handler, name='verify-handler'),  # PATCH /api/accounts/handlers/{id}/verify/
    path('handlers/available/', available_handlers, name='available-handlers'),  # GET /api/accounts/handlers/available/
    path('handlers/stats/', handler_stats, name='handlers-stats'),  # GET /api/accounts/handlers/stats/
    
    # Authentication
    path('register/', views.register, name='register'),
    path('verify-phone/', views.verify_phone, name='verify-phone'),
    path('resend-otp/', views.resend_otp, name='resend-otp'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('logout', views.logout, name='logout-no-slash'),  # Mobile app compatibility
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token'),
    path('token/refresh/', views.CustomTokenRefreshView.as_view(), name='token-refresh'),
    
    # Password Management
    path('v1/password-reset/request/', views.password_reset_request, name='password-reset-request'),
    path('password-reset/request/', views.password_reset_request, name='password-reset-request-alias'),  # App compatibility
    path('v1/password-reset/reset/', views.password_reset, name='password-reset'),
    path('password-reset/reset/', views.password_reset, name='password-reset-alias'),  # App compatibility
    path('change-password/', views.change_password, name='change-password'),
    
    # User Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('user/', views.user_detail, name='user-detail'),
    path('user/list/', views.user_list, name='user-list'),
    
    # Rider/Assistant Endpoints
    path('assistants/', views.list_assistants, name='list-assistants'),
    path('assistant/verify/', views.submit_verification, name='submit-verification'),
    path('assistant/verification-status/', views.assistant_verification_status, name='verification-status'),
    path('assistant/dashboard-stats/', views.assistant_dashboard_stats, name='assistant-stats'),
    path('assistant/availability/', views.assistant_availability, name='assistant-availability'),
    path('assistants/stats/', views.assistants_stats, name='assistants-stats'),
    
    # Admin - Verification Management
    path('admin/verifications/', views.admin_verifications_list, name='admin-verifications'),
    path('admin/verifications/<int:id>/', views.admin_verification_detail, name='admin-verification-detail'),
    path('admin/verifications/<int:id>/update/', views.admin_verification_update, name='admin-verification-update'),
    
    # Handler Endpoints - Client Management
    path('handler/clients/', handler_get_clients, name='handler-clients'),
    path('handler/clients/all/', handler_get_all_clients, name='handler-all-clients'),
    path('handler/dashboard-stats/', handler_dashboard_stats, name='handler-dashboard-stats'),
    path('user/<int:user_id>/assign-account-manager/', handler_assign_client, name='assign-account-manager'),
    
    # Handler Endpoints - Order Management
    path('handler/orders/create-for-client/', handler_create_order_for_client, name='handler-create-order'),
    path('handler/orders/<int:order_id>/confirm/', handler_confirm_order_for_client, name='handler-confirm-order'),
    path('handler/orders/<int:order_id>/cancel/', handler_cancel_order, name='handler-cancel-order'),
    path('handler/clients/<int:client_id>/orders/', handler_get_client_orders, name='handler-client-orders'),
    
    # Admin Only
    path('admin/users/<int:user_id>/change-type/', views.admin_change_user_type, name='admin-change-user-type'),
]
