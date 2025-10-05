"""
Base permission classes
"""
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Allow access only to admin users"""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsActiveUser(permissions.BasePermission):
    """Allow access only to active users"""
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_active)


class HasValidAPIKey(permissions.BasePermission):
    """Allow access only to users with valid API keys"""
    
    def has_permission(self, request, view):
        # Check if user has valid API key
        if not request.user or not request.user.is_authenticated:
            return False
        
        # For now, just check if user is active
        # TODO: Implement proper API key validation
        return request.user.is_active
