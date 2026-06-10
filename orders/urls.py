from django.urls import path
from . import views
from .views_errand import create_draft, upload_image, add_receiver_info, confirm_order
from .views_handler import list_orders, assign_order, order_stats
from .views_handler_rider import (
    handler_all_orders, handler_pending_orders, handler_assign_order,
    rider_available_orders, rider_my_orders, rider_order_history,
    rider_accept_order, rider_update_status, rider_start_delivery, rider_complete_delivery,
    sos_alerts_list, resolve_sos_alert
)
from .views_payment_ncba import (
    InitiatePaymentView, PaymentStatusView, NCBAPaymentView,
    NCBACallbackView, OrderPaymentStatusView, NCBAQRGenerationView
)

urlpatterns = [
    # Handler Dashboard Endpoints (NEW)
    path('', list_orders, name='list-orders'),  # GET /api/orders/
    path('stats/', order_stats, name='order-stats'),  # GET /api/orders/stats/
    path('<int:order_id>/', views.order_detail_handler, name='order-detail-handler'),  # GET /api/orders/{id}/ for handler
    path('<int:order_id>/assign/', assign_order, name='assign-order'),  # POST /api/orders/{id}/assign/
    
    # Errand Flow (4-step process) - specific patterns first
    path('errands/draft/', create_draft, name='create-draft'),
    path('errands/<int:order_id>/upload-image/', upload_image, name='upload-image'),
    path('errands/<int:order_id>/receiver-info/', add_receiver_info, name='receiver-info'),
    path('errands/<int:order_id>/confirm/', confirm_order, name='confirm-order'),
    path('errands/<int:order_id>/confirm', confirm_order, name='confirm-order-no-slash'),  # App compatibility
    
    # Generic detail - must be after specific patterns
    path('errands/<int:order_id>/', views.order_detail, name='errand-detail'),
    
    # Price calculation (real-time)
    path('errands/calculate-price/', views.calculate_price_realtime, name='calculate-price'),
    
    # Handler Endpoints
    path('handler/all/', handler_all_orders, name='handler-all-orders'),
    path('handler/pending/', handler_pending_orders, name='handler-pending'),
    path('handler/<int:order_id>/assign/', handler_assign_order, name='handler-assign'),
    
    # Rider/Assistant Endpoints
    path('assistant/available/', rider_available_orders, name='rider-available'),
    path('assistant/my-orders/', rider_my_orders, name='rider-my-orders'),
    path('assistant/history/', rider_order_history, name='rider-history'),
    path('assistant/<int:order_id>/accept/', rider_accept_order, name='rider-accept'),
    path('assistant/<int:order_id>/update-status/', rider_update_status, name='rider-update-status'),
    path('assistant/<int:order_id>/start/', rider_start_delivery, name='rider-start'),
    path('assistant/<int:order_id>/complete/', rider_complete_delivery, name='rider-complete'),
    
    # User order endpoints
    path('create/', views.create_order, name='create-order'),
    path('my-orders/', views.my_orders, name='my-orders'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel-order'),
    path('<int:order_id>/tracking/', views.order_tracking, name='order-tracking'),
    path('<int:order_id>/rate/', views.rate_order, name='rate-order'),
    
    # Rider assignment polling
    path('<int:order_id>/rider-assignment/', views.check_rider_assignment, name='rider-assignment'),
    
    # Legacy rider endpoints (kept for backwards compatibility)
    path('available/', rider_available_orders, name='available-orders'),
    path('<int:order_id>/accept/', rider_accept_order, name='accept-order'),
    path('my-deliveries/', rider_my_orders, name='my-deliveries'),
    path('<int:order_id>/update-status/', rider_update_status, name='update-order-status'),
    
    # Payment endpoints
    path('payments/initiate/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('payments/<int:pk>/', PaymentStatusView.as_view(), name='payment-detail'),
    path('payments/<int:payment_id>/process/', NCBAPaymentView.as_view(), name='process-payment'),
    path('payments/ncba/callback/', NCBACallbackView.as_view(), name='ncba-callback'),
    path('payments/ncba/qr-generate/', NCBAQRGenerationView.as_view(), name='ncba-qr-generate'),
    path('<int:order_id>/payment-status/', OrderPaymentStatusView.as_view(), name='order-payment-status'),
]
