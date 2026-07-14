"""Tests for Seller API endpoints."""

import pytest
from rest_framework import status


@pytest.mark.django_db
class TestSellerListAPI:
    """Tests for GET /api/v1/sellers/."""

    def test_list_sellers_authenticated(self, auth_client, seller):
        """Authenticated user can list sellers."""
        response = auth_client.get('/api/v1/sellers/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['meta']['pagination']['count'] >= 1

    def test_list_sellers_unauthenticated(self, api_client):
        """Unauthenticated user is rejected."""
        response = api_client.get('/api/v1/sellers/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_sellers_tenant_isolation(self, auth_client, auth_client_other_tenant, seller):
        """User only sees sellers from their own tenant."""
        response = auth_client_other_tenant.get('/api/v1/sellers/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['meta']['pagination']['count'] == 0

    def test_list_sellers_search(self, auth_client, seller):
        """Search sellers by name."""
        response = auth_client.get('/api/v1/sellers/?search=Frávega')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['meta']['pagination']['count'] == 1


@pytest.mark.django_db
class TestSellerCreateAPI:
    """Tests for POST /api/v1/sellers/."""

    def test_create_seller_success(self, auth_client):
        """Admin can create a seller."""
        data = {
            'name': 'Garbarino',
            'url': 'https://www.garbarino.com',
            'contact_email': 'info@garbarino.com',
        }
        response = auth_client.post('/api/v1/sellers/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Garbarino'

    def test_create_seller_viewer_forbidden(self, auth_client_viewer):
        """Viewer role cannot create sellers."""
        data = {'name': 'Blocked Seller', 'url': 'https://blocked.com'}
        response = auth_client_viewer.post('/api/v1/sellers/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_seller_duplicate_name(self, auth_client, seller):
        """Reject duplicate seller name within same tenant."""
        data = {
            'name': 'Frávega',
            'url': 'https://different.com',
        }
        response = auth_client.post('/api/v1/sellers/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestSellerDetailAPI:
    """Tests for GET/PUT/DELETE /api/v1/sellers/{id}/."""

    def test_get_seller_detail(self, auth_client, seller):
        """Get seller by ID."""
        response = auth_client.get(f'/api/v1/sellers/{seller.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Frávega'

    def test_update_seller(self, auth_client, seller):
        """Update seller contact info."""
        data = {'contact_email': 'nuevo@fravega.com'}
        response = auth_client.patch(
            f'/api/v1/sellers/{seller.id}/', data, format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['contact_email'] == 'nuevo@fravega.com'

    def test_delete_seller(self, auth_client, seller):
        """Delete seller."""
        response = auth_client.delete(f'/api/v1/sellers/{seller.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_other_tenant_cannot_access(self, auth_client_other_tenant, seller):
        """User from another tenant cannot see this seller."""
        response = auth_client_other_tenant.get(f'/api/v1/sellers/{seller.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
