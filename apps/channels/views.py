"""Channel ViewSet with multi-tenant CRUD."""

from __future__ import annotations

from rest_framework import viewsets

from apps.core.pagination import StandardPagination
from apps.core.permissions import IsAdminOrManager, IsTenantUser

from .models import Channel
from .serializers import ChannelSerializer


class ChannelViewSet(viewsets.ModelViewSet):
    """ViewSet for Channel CRUD with multi-tenant isolation."""

    serializer_class = ChannelSerializer
    permission_classes = [IsTenantUser, IsAdminOrManager]
    pagination_class = StandardPagination

    def get_queryset(self):
        """Return channels filtered by user's tenant."""
        queryset = Channel.objects.filter(
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
