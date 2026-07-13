"""Seller model — retailers/resellers being monitored within a tenant."""

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models


class Seller(models.Model):
    """A seller/retailer being monitored for price compliance."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.CASCADE, related_name='sellers'
    )
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=2048, blank=True, default='')
    contact_email = models.EmailField(max_length=255, blank=True, default='')
    contact_phone = models.CharField(max_length=20, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sellers_updated',
    )

    class Meta:
        db_table = 'sellers'
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'name'],
                name='unique_seller_per_tenant',
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
            raise ValidationError({'name': 'Seller name is required.'})
        if self.url:
            validator = URLValidator()
            try:
                validator(self.url)
            except ValidationError:
                raise ValidationError({'url': 'Enter a valid URL.'})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
