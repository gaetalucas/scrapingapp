"""Shared test fixtures for all test modules."""

import pytest
from rest_framework.test import APIClient

from apps.brands.models import Brand
from apps.categories.models import Category
from apps.channels.models import Channel
from apps.products.models import Product
from apps.sellers.models import Seller
from apps.tenants.models import Tenant, User


@pytest.fixture
def tenant(db):
    """Samsung Argentina tenant."""
    return Tenant.objects.create(
        name="Samsung Argentina",
        slug="samsung-argentina",
        plan="professional",
    )


@pytest.fixture
def tenant_other(db):
    """Second tenant for isolation tests."""
    return Tenant.objects.create(
        name="LG Argentina",
        slug="lg-argentina",
        plan="starter",
    )


@pytest.fixture
def user_admin(tenant):
    """Admin user for Samsung Argentina."""
    return User.objects.create_user(
        email="admin@samsung.com.ar",
        password="admin123",
        name="Lucas Admin",
        role="admin",
        tenant=tenant,
    )


@pytest.fixture
def user_manager(tenant):
    """Manager user for Samsung Argentina."""
    return User.objects.create_user(
        email="manager@samsung.com.ar",
        password="manager123",
        name="María Manager",
        role="manager",
        tenant=tenant,
    )


@pytest.fixture
def user_viewer(tenant):
    """Viewer user for Samsung Argentina (read-only)."""
    return User.objects.create_user(
        email="viewer@samsung.com.ar",
        password="viewer123",
        name="Pablo Viewer",
        role="viewer",
        tenant=tenant,
    )


@pytest.fixture
def user_other_tenant(tenant_other):
    """Admin user for LG Argentina (different tenant)."""
    return User.objects.create_user(
        email="admin@lg.com.ar",
        password="admin123",
        name="Diego Admin",
        role="admin",
        tenant=tenant_other,
    )


@pytest.fixture
def brand(tenant):
    """Samsung brand."""
    return Brand.objects.create(tenant=tenant, name="Samsung")


@pytest.fixture
def brand_other(tenant_other):
    """LG brand in other tenant."""
    return Brand.objects.create(tenant=tenant_other, name="LG")


@pytest.fixture
def category(tenant):
    """Smartphones category."""
    return Category.objects.create(tenant=tenant, name="Smartphones")


@pytest.fixture
def category_other(tenant_other):
    """Televisores category in other tenant."""
    return Category.objects.create(tenant=tenant_other, name="Televisores")


@pytest.fixture
def channel(tenant):
    """Mercado Libre channel."""
    return Channel.objects.create(tenant=tenant, name="Mercado Libre")


@pytest.fixture
def seller(tenant):
    """Frávega seller."""
    return Seller.objects.create(
        tenant=tenant,
        name="Frávega",
        url="https://www.fravega.com",
        contact_email="comercial@fravega.com",
        contact_phone="+5411-4000-0001",
    )


@pytest.fixture
def product(tenant, brand, category):
    """Galaxy S24 product."""
    return Product.objects.create(
        tenant=tenant,
        name="Galaxy S24 128GB",
        brand=brand,
        model="S24",
        category=category,
        sku="SM-S24-128",
        pvp_full=1199000,
        pvp_promo=999000,
    )


@pytest.fixture
def product_other(tenant_other, brand_other, category_other):
    """Product in other tenant for isolation tests."""
    return Product.objects.create(
        tenant=tenant_other,
        name="LG TV 55",
        brand=brand_other,
        model="55UN7300",
        category=category_other,
        sku="LG-TV-55",
        pvp_full=2000000,
    )


@pytest.fixture
def api_client():
    """Unauthenticated API client."""
    return APIClient()


@pytest.fixture
def auth_client(api_client, user_admin):
    """Authenticated API client as admin."""
    api_client.force_authenticate(user=user_admin)
    return api_client


@pytest.fixture
def auth_client_manager(api_client, user_manager):
    """Authenticated API client as manager."""
    client = APIClient()
    client.force_authenticate(user=user_manager)
    return client


@pytest.fixture
def auth_client_viewer(api_client, user_viewer):
    """Authenticated API client as viewer (read-only)."""
    client = APIClient()
    client.force_authenticate(user=user_viewer)
    return client


@pytest.fixture
def auth_client_other_tenant(user_other_tenant):
    """Authenticated API client for other tenant."""
    client = APIClient()
    client.force_authenticate(user=user_other_tenant)
    return client
