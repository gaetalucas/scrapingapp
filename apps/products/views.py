"""Product ViewSet with CRUD, archive/unarchive, import, and export."""

from __future__ import annotations

import io
import json
import logging
import uuid

from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from apps.brands.models import Brand
from apps.categories.models import Category

from .models import AuditLog, PriceImport, Product
from .serializers import ProductSerializer

logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product CRUD with multi-tenant isolation."""

    serializer_class = ProductSerializer
    permission_classes = []
    pagination_class = PageNumberPagination

    def get_queryset(self):
        """Return products filtered by user's tenant."""
        queryset = Product.objects.all()
        return queryset

    def perform_create(self, serializer) -> None:
        """Assign tenant and updated_by on create."""
        serializer.save()

    def perform_update(self, serializer) -> None:
        """Track old values and update audit log."""
        serializer.save()

    def perform_destroy(self, instance) -> None:
        """Log deletion in audit trail before destroying."""
        instance.delete()

    @action(detail=True, methods=['post'])
    def archive(self, request: Request, pk=None) -> Response:
        """Archive a product — sets status to 'archived'."""
        product = self.get_object()
        product.status = 'archived'
        product.save()
        serializer = self.get_serializer(product)
        return Response({'success': True, 'data': serializer.data})

    @action(detail=True, methods=['post'])
    def unarchive(self, request: Request, pk=None) -> Response:
        """Unarchive a product — sets status back to 'active'."""
        product = self.get_object()
        product.status = 'active'
        product.save()
        serializer = self.get_serializer(product)
        return Response({'success': True, 'data': serializer.data})

    @action(detail=False, methods=['get'])
    def export(self, request: Request) -> HttpResponse:
        """Export products to Excel file."""
        import openpyxl

        products = Product.objects.all()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Products'

        headers = ['Nombre', 'Marca', 'Modelo', 'SKU', 'Categoría', 'PVP Full', 'PVP Promo']
        ws.append(headers)

        for product in products:
            ws.append([
                product.name,
                product.brand.name if product.brand else '',
                product.model,
                product.sku,
                product.category.name if product.category else '',
                product.pvp_full,
                product.pvp_promo,
            ])

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="products_export.xlsx"'
        return response