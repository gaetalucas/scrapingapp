from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Tenant, User


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'plan', 'active', 'created_at']
    list_filter = ['plan', 'active']
    search_fields = ['name', 'slug']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'name', 'tenant', 'role', 'status', 'is_staff']
    list_filter = ['role', 'status', 'is_staff', 'tenant']
    search_fields = ['email', 'name']
    ordering = ['email']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'tenant', 'role', 'status')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'tenant', 'role', 'password1', 'password2'),
        }),
    )
