from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrAnonymous(BasePermission):
    def has_permission(self, request, view): # type: ignore
        # Allow safe methods for everyone
        if request.method in SAFE_METHODS:
            return True
        
        # Allow POST for anonymous users or superusers
        if request.method == 'POST':
            return request.user.is_anonymous or request.user.is_superuser
        
        return False
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True 
        return request.user.is_anonymous
    
class IsAdminOrUserOwner(BasePermission):
    def has_permission(self, request, view): # type: ignore
        if request.method in SAFE_METHODS:
            return True
        
        if request.method == 'POST':
            return request.user.is_authenticated
    
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return request.user == obj
    
class IsAdminOrBookingUser(BasePermission):
    def has_permission(self, request, view): # type: ignore
        if request.method in SAFE_METHODS:
            return True
        
        if request.method == 'POST':
            return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj): # type: ignore
        if request.user.is_superuser:
            return True
        return hasattr(obj, 'customer') and obj.customer == request.user