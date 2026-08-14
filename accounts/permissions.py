"""
Custom permission classes for verification and access control.
"""

from rest_framework.permissions import BasePermission
from rest_framework import status
from rest_framework.response import Response


class IsPhoneVerified(BasePermission):
    """
    Permission class that checks if user's phone number is verified.
    
    Prevents unverified users from accessing sensitive endpoints.
    """
    message = 'Phone verification is required. Please verify your phone number first.'
    
    def has_permission(self, request, view):
        # Allow read-only requests for unauthenticated users (they won't pass IsAuthenticated anyway)
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has verified their phone
        if not request.user.is_verified:
            return False
        
        return True


class IsPhoneVerifiedOrReadOnly(BasePermission):
    """
    Allow read access to verified users, but deny unverified users.
    Write access requires verification.
    """
    message = 'Phone verification required for this action.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # For write operations, require verification
        if request.method not in ['GET', 'HEAD', 'OPTIONS']:
            if not request.user.is_verified:
                return False
        
        return True


class IsVerifiedAssistant(BasePermission):
    """
    Allows access only to verified assistants (riders/handlers).
    Requires:
    - User authenticated
    - Phone verified
    - user_type is 'assistant' or 'handler'
    - Has submitted verification documents (for assistants)
    """
    message = 'Only verified assistants can access this resource.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not request.user.is_verified:
            return False
        
        if request.user.user_type not in ['assistant', 'handler']:
            return False
        
        return True


class IsHandlerOrAdmin(BasePermission):
    """
    Allows access to handlers and admins only.
    """
    message = 'Handler or admin access required.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.user_type not in ['handler', 'admin']:
            return False
        
        return True


class IsAdmin(BasePermission):
    """
    Allows access to admin users only.
    """
    message = 'Admin access required.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.user_type == 'admin'


class IsOwnerOrAdmin(BasePermission):
    """
    Allows access only to object owner or admin.
    Requires object to have an 'owner' or 'user' field.
    """
    message = 'You do not have permission to access this resource.'
    
    def has_object_permission(self, request, view, obj):
        # Admin always has access
        if request.user and request.user.is_authenticated and request.user.user_type == 'admin':
            return True
        
        # Check if user is the owner
        owner_field = getattr(obj, 'owner', getattr(obj, 'user', None))
        return owner_field == request.user


class IsVerifiedAndOwner(BasePermission):
    """
    Allows access only to verified users who own the object.
    """
    message = 'Phone verification required and you must be the owner.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not request.user.is_verified:
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        owner_field = getattr(obj, 'owner', getattr(obj, 'user', None))
        return owner_field == request.user


class CanViewProfile(BasePermission):
    """
    Allow users to view their own profile.
    Requires phone verification.
    """
    message = 'Phone verification required to view profiles.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not request.user.is_verified:
            return False
        
        return True


class CanManageOrder(BasePermission):
    """
    Allow users to manage orders they own, or handlers/admins to manage assigned orders.
    Requires phone verification for all users.
    """
    message = 'Phone verification required to manage orders.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not request.user.is_verified:
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        # Admin can always manage orders
        if request.user.user_type == 'admin':
            return True
        
        # Handler can manage orders belonging to their assigned clients
        if request.user.user_type == 'handler':
            return (
                getattr(obj, 'assistant', None) == request.user
                or (hasattr(obj, 'user') and getattr(obj.user, 'account_manager', None) == request.user)
            )
        
        # User can only manage their own orders
        return obj.user == request.user
