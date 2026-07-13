"""Category model — product classification within a tenant."""

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Category(models.Model):
    """A product category belonging to a tenant (e.g., Smartphones, TVs)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE, related_name='categories'
    )
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='categories_updated',
    )

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'name'],
                name='unique_category_per_tenant',
            ),
        ]
        indexes = [
            models.Index(fields=['tenant']),
        ]
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Category name is required.'})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
