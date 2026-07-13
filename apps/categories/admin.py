from django.contrib import admin

from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'created_at']
    list_filter = ['tenant']
    search_fields = ['name']
