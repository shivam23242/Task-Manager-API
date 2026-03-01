from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a task or admins to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner or admin users
        return obj.owner == request.user or request.user.is_admin()


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin()

