"""Tests for model validation and constraints."""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.brands.models import Brand
from apps.categories.models import Category
from apps.products.models import Product
from apps.sellers.models import Seller


@pytest.mark.django_db
class TestProductModel:
    """Tests for the Product model."""

    def test_product_creation_success(self, product):
        """Product can be created with valid data."""
        assert product.name == "Galaxy S24 128GB"
        assert product.sku == "SM-S24-128"
        assert product.pvp_full == 1199000
        assert product.pvp_promo == 999000
        assert product.status == "active"
        assert str(product) == "Galaxy S24 128GB (SM-S24-128)"

    def test_product_sku_uniqueness_per_tenant(self, tenant, brand, category):
        """SKU must be unique within the same tenant."""
        Product.objects.create(
            tenant=tenant, name="Product A", brand=brand,
            model="A", category=category, sku="SAME-SKU", pvp_full=100000,
        )
        with pytest.raises((IntegrityError, ValidationError)):
            Product.objects.create(
                tenant=tenant, name="Product B", brand=brand,
                model="B", category=category, sku="SAME-SKU", pvp_full=200000,
            )

    def test_product_same_sku_different_tenant(self, tenant, tenant_other, brand, brand_other, category, category_other):
        """Same SKU is allowed in different tenants."""
        Product.objects.create(
            tenant=tenant, name="Product A", brand=brand,
            model="A", category=category, sku="SHARED-SKU", pvp_full=100000,
        )
        p2 = Product.objects.create(
            tenant=tenant_other, name="Product B", brand=brand_other,
            model="B", category=category_other, sku="SHARED-SKU", pvp_full=200000,
        )
        assert p2.sku == "SHARED-SKU"

    def test_product_pvp_promo_must_be_lte_pvp_full(self, tenant, brand, category):
        """pvp_promo must be <= pvp_full."""
        with pytest.raises(ValidationError) as exc_info:
            Product.objects.create(
                tenant=tenant, name="Bad Price", brand=brand,
                model="X", category=category, sku="BAD-1",
                pvp_full=100000, pvp_promo=200000,
            )
        assert 'pvp_promo' in str(exc_info.value)

    def test_product_pvp_full_must_be_positive(self, tenant, brand, category):
        """pvp_full must be > 0."""
        with pytest.raises(ValidationError) as exc_info:
            Product.objects.create(
                tenant=tenant, name="Zero Price", brand=brand,
                model="X", category=category, sku="ZERO-1",
                pvp_full=0,
            )
        assert 'pvp_full' in str(exc_info.value)

    def test_product_name_required(self, tenant, brand, category):
        """Product name cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            Product.objects.create(
                tenant=tenant, name="", brand=brand,
                model="X", category=category, sku="NO-NAME",
                pvp_full=100000,
            )
        assert 'name' in str(exc_info.value)

    def test_product_sku_required(self, tenant, brand, category):
        """Product SKU cannot be empty."""
        with pytest.raises(ValidationError) as exc_info:
            Product.objects.create(
                tenant=tenant, name="No SKU", brand=brand,
                model="X", category=category, sku="",
                pvp_full=100000,
            )
        assert 'sku' in str(exc_info.value)


@pytest.mark.django_db
class TestBrandModel:
    """Tests for the Brand model."""

    def test_brand_creation(self, brand):
        """Brand can be created with valid data."""
        assert brand.name == "Samsung"
        assert str(brand) == "Samsung"

    def test_brand_uniqueness_per_tenant(self, tenant):
        """Brand name must be unique per tenant."""
        Brand.objects.create(tenant=tenant, name="Apple")
        with pytest.raises((IntegrityError, ValidationError)):
            Brand.objects.create(tenant=tenant, name="Apple")

    def test_brand_name_required(self, tenant):
        """Brand name cannot be empty."""
        with pytest.raises(ValidationError):
            Brand.objects.create(tenant=tenant, name="")


@pytest.mark.django_db
class TestCategoryModel:
    """Tests for the Category model."""

    def test_category_creation(self, category):
        """Category can be created."""
        assert category.name == "Smartphones"
        assert str(category) == "Smartphones"

    def test_category_uniqueness_per_tenant(self, tenant):
        """Category name must be unique per tenant."""
        Category.objects.create(tenant=tenant, name="Audio")
        with pytest.raises((IntegrityError, ValidationError)):
            Category.objects.create(tenant=tenant, name="Audio")


@pytest.mark.django_db
class TestSellerModel:
    """Tests for the Seller model."""

    def test_seller_creation(self, seller):
        """Seller can be created with valid data."""
        assert seller.name == "Frávega"
        assert seller.url == "https://www.fravega.com"

    def test_seller_invalid_url(self, tenant):
        """Seller URL must be valid if provided."""
        with pytest.raises(ValidationError):
            Seller.objects.create(
                tenant=tenant, name="Bad URL Seller", url="not-a-url",
            )

    def test_seller_name_required(self, tenant):
        """Seller name cannot be empty."""
        with pytest.raises(ValidationError):
            Seller.objects.create(tenant=tenant, name="")
