from django.urls import path
from . import views

urlpatterns = [
    # Notifications list
    path('', views.get_notifications, name='notifications'),
    path('unread-count/', views.unread_count, name='unread-count'),
    
    # Mark as read
    path('<int:notification_id>/read/', views.mark_as_read, name='mark-as-read'),
    path('mark-all-read/', views.mark_all_read, name='mark-all-read'),
    
    # Delete
    path('<int:notification_id>/delete/', views.delete_notification, name='delete-notification'),
    path('delete-all/', views.delete_all_notifications, name='delete-all'),
    
    # Push tokens
    path('register-token/', views.register_push_token, name='register-push-token'),
    path('unregister-token/', views.unregister_push_token, name='unregister-push-token'),
]
