"""Custom permissions for multi-tenant access control."""

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView


class IsTenantUser(permissions.BasePermission):
    """Ensures the user is authenticated and belongs to the same tenant as the object."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check user is authenticated and has a tenant assigned."""
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.tenant_id is not None
        )

    def has_object_permission(self, request: Request, view: APIView, obj) -> bool:
        """Check object belongs to user's tenant."""
        return obj.tenant_id == request.user.tenant_id


class IsAdminOrManager(permissions.BasePermission):
    """Only admin or manager roles can perform write operations."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Allow read for all authenticated; write only for admin/manager."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in ('admin', 'manager')
