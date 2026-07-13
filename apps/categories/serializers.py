"""Category serializers with multi-tenant validation."""

from __future__ import annotations

from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category CRUD operations."""

    updated_by_email = serializers.CharField(
        source='updated_by.email', read_only=True, default=None
    )

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'created_at', 'updated_at', 'updated_by', 'updated_by_email',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'updated_by']

    def validate_name(self, value: str) -> str:
        """Ensure name is unique within the tenant."""
        tenant_id = self.context['request'].user.tenant_id
        queryset = Category.objects.filter(tenant_id=tenant_id, name=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('Category name already exists for this tenant.')
        return value
