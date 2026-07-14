"""Tests for Product API endpoints."""

import pytest
from rest_framework import status


@pytest.mark.django_db
class TestProductListAPI:
    """Tests for GET /api/v1/products/."""

    def test_list_products(self, auth_client, product):
        """List products returns 200 with results."""
        response = auth_client.get('/api/v1/products/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_list_products_unauthenticated(self, api_client, product):
        """Unauthenticated access is allowed (permission_classes=[])."""
        response = api_client.get('/api/v1/products/')
        assert response.status_code == status.HTTP_200_OK

    def test_list_products_pagination(self, auth_client, product):
        """Response includes pagination fields."""
        response = auth_client.get('/api/v1/products/')
        assert 'count' in response.data
        assert 'results' in response.data


@pytest.mark.django_db
class TestProductCreateAPI:
    """Tests for POST /api/v1/products/."""

    def test_create_product_success(self, auth_client, brand, category, tenant):
        """Create product with valid data."""
        data = {
            'name': 'Galaxy A55',
            'brand': str(brand.id),
            'model': 'A55',
            'category': str(category.id),
            'sku': 'SM-A55-128',
            'pvp_full': 699000,
        }
        response = auth_client.post('/api/v1/products/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Galaxy A55'
        assert response.data['sku'] == 'SM-A55-128'

    def test_create_product_invalid_pvp_promo(self, auth_client, brand, category, tenant):
        """Reject product where pvp_promo > pvp_full."""
        data = {
            'name': 'Bad Promo',
            'brand': str(brand.id),
            'model': 'X',
            'category': str(category.id),
            'sku': 'BAD-PROMO',
            'pvp_full': 500000,
            'pvp_promo': 900000,
        }
        response = auth_client.post('/api/v1/products/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_product_zero_pvp_full(self, auth_client, brand, category, tenant):
        """Reject product with pvp_full <= 0."""
        data = {
            'name': 'Zero Price',
            'brand': str(brand.id),
            'model': 'X',
            'category': str(category.id),
            'sku': 'ZERO-PRICE',
            'pvp_full': 0,
        }
        response = auth_client.post('/api/v1/products/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProductDetailAPI:
    """Tests for GET/PUT/DELETE /api/v1/products/{id}/."""

    def test_get_product_detail(self, auth_client, product):
        """Get single product by ID."""
        response = auth_client.get(f'/api/v1/products/{product.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['sku'] == 'SM-S24-128'

    def test_update_product(self, auth_client, product):
        """Update product name."""
        data = {'name': 'Galaxy S24 Ultra'}
        response = auth_client.patch(
            f'/api/v1/products/{product.id}/', data, format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Galaxy S24 Ultra'

    def test_delete_product(self, auth_client, product):
        """Delete product."""
        response = auth_client.delete(f'/api/v1/products/{product.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_get_nonexistent_product(self, auth_client):
        """404 for non-existent product ID."""
        import uuid
        fake_id = uuid.uuid4()
        response = auth_client.get(f'/api/v1/products/{fake_id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestProductArchiveAPI:
    """Tests for archive/unarchive actions."""

    def test_archive_product(self, auth_client, product):
        """POST /api/v1/products/{id}/archive/ sets status to archived."""
        response = auth_client.post(f'/api/v1/products/{product.id}/archive/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['status'] == 'archived'

    def test_unarchive_product(self, auth_client, product):
        """POST /api/v1/products/{id}/unarchive/ sets status to active."""
        product.status = 'archived'
        product.save()
        response = auth_client.post(f'/api/v1/products/{product.id}/unarchive/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['status'] == 'active'


@pytest.mark.django_db
class TestProductExportAPI:
    """Tests for export action."""

    def test_export_products_xlsx(self, auth_client, product):
        """GET /api/v1/products/export/ returns Excel file."""
        response = auth_client.get('/api/v1/products/export/')
        assert response.status_code == status.HTTP_200_OK
        assert 'spreadsheetml' in response['Content-Type']
        assert 'attachment' in response['Content-Disposition']
