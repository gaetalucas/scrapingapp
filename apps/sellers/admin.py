from django.contrib import admin

from .models import Seller


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'url', 'contact_email', 'created_at']
    list_filter = ['tenant']
    search_fields = ['name', 'url']
