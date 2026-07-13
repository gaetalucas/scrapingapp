"""Product, PriceImport, and AuditLog models — core of the pricing platform."""

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Product(models.Model):
    """A product with pricing info, belonging to a tenant."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE, related_name='products'
    )
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(
        'brands.Brand', on_delete=models.RESTRICT, related_name='products'
    )
    model = models.CharField(max_length=100)
    category = models.ForeignKey(
        'categories.Category', on_delete=models.RESTRICT, related_name='products'
    )
    sku = models.CharField(max_length=100)
    pvp_full = models.BigIntegerField(help_text='Price in cents (1199000 = $11,990)')
    pvp_promo = models.BigIntegerField(
        null=True, blank=True, help_text='Promo price in cents, must be <= pvp_full'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products_updated',
    )

    class Meta:
        db_table = 'products'
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'sku'],
                name='unique_sku_per_tenant',
            ),
        ]
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'category']),
            models.Index(fields=['tenant', 'brand']),
            models.Index(fields=['tenant', 'created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"

    def clean(self) -> None:
        super().clean()
        errors = {}
        if not self.name or not self.name.strip():
            errors['name'] = 'Product name is required.'
        if not self.sku or not self.sku.strip():
            errors['sku'] = 'SKU is required.'
        if self.pvp_full is not None and self.pvp_full <= 0:
            errors['pvp_full'] = 'PVP Full must be a positive value.'
        if self.pvp_promo is not None and self.pvp_full is not None:
            if self.pvp_promo > self.pvp_full:
                errors['pvp_promo'] = 'PVP Promo must be ≤ PVP Full.'
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class PriceImport(models.Model):
    """Audit record for bulk price imports via Excel/CSV."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE, related_name='price_imports'
    )
    filename = models.CharField(max_length=255)
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='price_imports'
    )
    row_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_details = models.TextField(blank=True, default='', help_text='JSON error details')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'price_imports'
        indexes = [
            models.Index(fields=['tenant']),
        ]
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.filename} ({self.status})"


class AuditLog(models.Model):
    """Immutable audit trail for compliance — records all entity changes."""

    ENTITY_TYPE_CHOICES = [
        ('product', 'Product'),
        ('seller', 'Seller'),
        ('category', 'Category'),
        ('brand', 'Brand'),
        ('channel', 'Channel'),
    ]

    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('archive', 'Archive'),
        ('import', 'Import'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE, related_name='audit_logs'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPE_CHOICES)
    entity_id = models.UUIDField()
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_log'
        indexes = [
            models.Index(fields=['tenant']),
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['-created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.action} {self.entity_type} ({self.entity_id})"
