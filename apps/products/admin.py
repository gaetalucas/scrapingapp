from django.contrib import admin

from .models import AuditLog, PriceImport, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'brand', 'category', 'pvp_full', 'pvp_promo', 'status', 'tenant']
    list_filter = ['status', 'brand', 'category', 'tenant']
    search_fields = ['name', 'sku']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(PriceImport)
class PriceImportAdmin(admin.ModelAdmin):
    list_display = ['filename', 'tenant', 'imported_by', 'row_count', 'success_count', 'error_count', 'status', 'created_at']
    list_filter = ['status', 'tenant']
    search_fields = ['filename']
    readonly_fields = ['id', 'created_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['entity_type', 'action', 'user', 'tenant', 'created_at']
    list_filter = ['entity_type', 'action', 'tenant']
    search_fields = ['entity_id']
    readonly_fields = ['id', 'created_at', 'old_values', 'new_values']
