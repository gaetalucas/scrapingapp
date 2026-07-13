"""Tenant and User models — foundation of multi-tenant architecture."""

import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models


class Tenant(models.Model):
    """Organization/company that owns a set of data in the platform."""

    PLAN_CHOICES = [
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    timezone = models.CharField(max_length=50, default='America/Argentina/Buenos_Aires')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='starter')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tenants'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class UserManager(BaseUserManager):
    """Custom manager for User model with email as identifier."""

    def create_user(
        self, email: str, password: str | None = None, **extra_fields
    ) -> 'User':
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields
    ) -> 'User':
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """User belonging to a tenant with role-based access."""

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('analyst', 'Analyst'),
        ('viewer', 'Viewer'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('invited', 'Invited'),
        ('inactive', 'Inactive'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name='users', null=True, blank=True
    )
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'users'
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'email'],
                name='unique_email_per_tenant',
            ),
        ]
        indexes = [
            models.Index(fields=['tenant']),
            models.Index(fields=['email']),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.email})"

    def get_full_name(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        if not self.email:
            raise ValidationError({'email': 'Email is required.'})
