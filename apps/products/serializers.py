"""Product serializers with multi-tenant validation."""

from __future__ import annotations

from rest_framework import serializers

from apps.brands.models import Brand
from apps.categories.models import Category

from .models import AuditLog, PriceImport, Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product CRUD operations."""

    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    updated_by_email = serializers.CharField(
        source='updated_by.email', read_only=True, default=None
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'brand', 'brand_name', 'model', 'category',
            'category_name', 'sku', 'pvp_full', 'pvp_promo', 'status',
            'created_at', 'updated_at', 'updated_by', 'updated_by_email',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'updated_by']

    def validate_pvp_full(self, value: int) -> int:
        """Ensure pvp_full is a positive integer."""
        if value <= 0:
            raise serializers.ValidationError('PVP Full must be a positive value.')
        return value

    def validate(self, attrs: dict) -> dict:
        """Cross-field validation: pvp_promo must be <= pvp_full."""
        pvp_full = attrs.get('pvp_full') or (self.instance and self.instance.pvp_full)
        pvp_promo = attrs.get('pvp_promo')

        if pvp_promo is not None and pvp_full is not None:
            if pvp_promo > pvp_full:
                raise serializers.ValidationError(
                    {'pvp_promo': 'PVP Promo must be ≤ PVP Full.'}
                )
        return attrs

    def validate_sku(self, value: str) -> str:
        """Ensure SKU is unique within the tenant."""
        tenant_id = self.context['request'].user.tenant_id
        queryset = Product.objects.filter(tenant_id=tenant_id, sku=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('SKU already exists for this tenant.')
        return value

    def validate_brand(self, value: Brand) -> Brand:
        """Ensure brand belongs to the same tenant."""
        tenant_id = self.context['request'].user.tenant_id
        if value.tenant_id != tenant_id:
            raise serializers.ValidationError('Brand does not belong to your tenant.')
        return value

    def validate_category(self, value: Category) -> Category:
        """Ensure category belongs to the same tenant."""
        tenant_id = self.context['request'].user.tenant_id
        if value.tenant_id != tenant_id:
            raise serializers.ValidationError('Category does not belong to your tenant.')
        return value


class ProductImportPreviewSerializer(serializers.Serializer):
    """Serializer for Excel import preview response."""

    row = serializers.IntegerField()
    name = serializers.CharField()
    brand = serializers.CharField()
    model = serializers.CharField()
    sku = serializers.CharField()
    category = serializers.CharField()
    pvp_full = serializers.IntegerField()
    pvp_promo = serializers.IntegerField(allow_null=True)
    status = serializers.CharField()
    error_message = serializers.CharField(allow_blank=True, default='')


class PriceImportSerializer(serializers.ModelSerializer):
    """Serializer for PriceImport records."""

    imported_by_email = serializers.CharField(
        source='imported_by.email', read_only=True
    )

    class Meta:
        model = PriceImport
        fields = [
            'id', 'filename', 'imported_by', 'imported_by_email',
            'row_count', 'success_count', 'error_count', 'status',
            'error_details', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog records (read-only)."""

    user_email = serializers.CharField(source='user.email', read_only=True, default=None)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_email', 'entity_type', 'entity_id',
            'action', 'old_values', 'new_values', 'ip_address',
            'user_agent', 'created_at',
        ]
        read_only_fields = fields
