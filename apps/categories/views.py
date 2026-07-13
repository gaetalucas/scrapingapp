"""Category ViewSet with multi-tenant CRUD."""

from __future__ import annotations

from rest_framework import viewsets

from apps.core.pagination import StandardPagination
from apps.core.permissions import IsAdminOrManager, IsTenantUser

from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category CRUD with multi-tenant isolation."""

    serializer_class = CategorySerializer
    permission_classes = [IsTenantUser, IsAdminOrManager]
    pagination_class = StandardPagination

    def get_queryset(self):
        """Return categories filtered by user's tenant."""
        queryset = Category.objects.filter(
            tenant_id=self.request.user.tenant_id
        ).select_related('updated_by')

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset

    def perform_create(self, serializer) -> None:
        """Assign tenant and updated_by on create."""
        serializer.save(
            tenant_id=self.request.user.tenant_id,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer) -> None:
        """Track updated_by on update."""
        serializer.save(updated_by=self.request.user)
