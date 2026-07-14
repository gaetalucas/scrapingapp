"""Tests for serializer validation logic."""

import pytest
from rest_framework.test import APIRequestFactory

from apps.products.serializers import ProductSerializer
from apps.sellers.serializers import SellerSerializer


factory = APIRequestFactory()


@pytest.mark.django_db
class TestProductSerializer:
    """Tests for ProductSerializer validation."""

    def _make_request(self, user):
        request = factory.post('/api/v1/products/')
        request.user = user
        return request

    def test_valid_product_data(self, user_admin, brand, category):
        """Serializer accepts valid product data."""
        request = self._make_request(user_admin)
        data = {
            'name': 'Galaxy S25',
            'brand': str(brand.id),
            'model': 'S25',
            'category': str(category.id),
            'sku': 'SM-S25-128',
            'pvp_full': 1500000,
        }
        serializer = ProductSerializer(data=data, context={'request': request})
        assert serializer.is_valid(), serializer.errors

    def test_pvp_promo_greater_than_pvp_full(self, user_admin, brand, category):
        """Serializer rejects pvp_promo > pvp_full."""
        request = self._make_request(user_admin)
        data = {
            'name': 'Galaxy S25',
            'brand': str(brand.id),
            'model': 'S25',
            'category': str(category.id),
            'sku': 'SM-S25-128',
            'pvp_full': 1000000,
            'pvp_promo': 2000000,
        }
        serializer = ProductSerializer(data=data, context={'request': request})
        assert not serializer.is_valid()
        assert 'pvp_promo' in serializer.errors

    def test_pvp_full_must_be_positive(self, user_admin, brand, category):
        """Serializer rejects pvp_full <= 0."""
        request = self._make_request(user_admin)
        data = {
            'name': 'Galaxy S25',
            'brand': str(brand.id),
            'model': 'S25',
            'category': str(category.id),
            'sku': 'SM-S25-128',
            'pvp_full': 0,
        }
        serializer = ProductSerializer(data=data, context={'request': request})
        assert not serializer.is_valid()
        assert 'pvp_full' in serializer.errors

    def test_duplicate_sku_same_tenant(self, user_admin, brand, category, product):
        """Serializer rejects duplicate SKU within same tenant."""
        request = self._make_request(user_admin)
        data = {
            'name': 'Another Product',
            'brand': str(brand.id),
            'model': 'X',
            'category': str(category.id),
            'sku': 'SM-S24-128',  # same as product fixture
            'pvp_full': 999000,
        }
        serializer = ProductSerializer(data=data, context={'request': request})
        assert not serializer.is_valid()
        assert 'sku' in serializer.errors

    def test_brand_from_other_tenant_rejected(self, user_admin, brand_other, category):
        """Serializer rejects brand from a different tenant."""
        request = self._make_request(user_admin)
        data = {
            'name': 'Test Product',
            'brand': str(brand_other.id),
            'model': 'X',
            'category': str(category.id),
            'sku': 'CROSS-TENANT-1',
            'pvp_full': 500000,
        }
        serializer = ProductSerializer(data=data, context={'request': request})
        assert not serializer.is_valid()
        assert 'brand' in serializer.errors

    def test_category_from_other_tenant_rejected(self, user_admin, brand, category_other):
        """Serializer rejects category from a different tenant."""
        request = self._make_request(user_admin)
        data = {
            'name': 'Test Product',
            'brand': str(brand.id),
            'model': 'X',
            'category': str(category_other.id),
            'sku': 'CROSS-TENANT-2',
            'pvp_full': 500000,
        }
        serializer = ProductSerializer(data=data, context={'request': request})
        assert not serializer.is_valid()
        assert 'category' in serializer.errors


@pytest.mark.django_db
class TestSellerSerializer:
    """Tests for SellerSerializer validation."""

    def _make_request(self, user):
        request = factory.post('/api/v1/sellers/')
        request.user = user
        return request

    def test_valid_seller_data(self, user_admin):
        """Serializer accepts valid seller data."""
        request = self._make_request(user_admin)
        data = {
            'name': 'Garbarino',
            'url': 'https://www.garbarino.com',
            'contact_email': 'ventas@garbarino.com',
        }
        serializer = SellerSerializer(data=data, context={'request': request})
        assert serializer.is_valid(), serializer.errors

    def test_duplicate_seller_name_same_tenant(self, user_admin, seller):
        """Serializer rejects duplicate seller name within tenant."""
        request = self._make_request(user_admin)
        data = {
            'name': 'Frávega',  # same as seller fixture
            'url': 'https://different.com',
        }
        serializer = SellerSerializer(data=data, context={'request': request})
        assert not serializer.is_valid()
        assert 'name' in serializer.errors
