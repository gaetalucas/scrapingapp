"""Tests for Auth API endpoints (login, refresh, logout)."""

import pytest
from rest_framework import status


@pytest.mark.django_db
class TestLoginAPI:
    """Tests for POST /api/v1/auth/login/."""

    def test_login_success(self, api_client, user_admin):
        """Login with valid credentials returns tokens."""
        data = {'email': 'admin@samsung.com.ar', 'password': 'admin123'}
        response = api_client.post('/api/v1/auth/login/', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data
        assert 'refresh_token' in response.data
        assert response.data['user']['email'] == 'admin@samsung.com.ar'
        assert response.data['user']['role'] == 'admin'

    def test_login_wrong_password(self, api_client, user_admin):
        """Login with wrong password returns 400."""
        data = {'email': 'admin@samsung.com.ar', 'password': 'wrongpass'}
        response = api_client.post('/api/v1/auth/login/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_nonexistent_user(self, api_client):
        """Login with non-existent email returns 400."""
        data = {'email': 'nobody@example.com', 'password': 'test123'}
        response = api_client.post('/api/v1/auth/login/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_missing_fields(self, api_client):
        """Login without email/password returns 400."""
        response = api_client.post('/api/v1/auth/login/', {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_returns_user_info(self, api_client, user_admin, tenant):
        """Login response includes user details."""
        data = {'email': 'admin@samsung.com.ar', 'password': 'admin123'}
        response = api_client.post('/api/v1/auth/login/', data, format='json')
        user_data = response.data['user']
        assert user_data['name'] == 'Lucas Admin'
        assert user_data['tenant_id'] == str(tenant.id)


@pytest.mark.django_db
class TestRefreshAPI:
    """Tests for POST /api/v1/auth/refresh/."""

    def test_refresh_with_valid_token(self, api_client, user_admin):
        """Refresh with valid refresh_token returns new access_token."""
        login_data = {'email': 'admin@samsung.com.ar', 'password': 'admin123'}
        login_response = api_client.post('/api/v1/auth/login/', login_data, format='json')
        refresh_token = login_response.data['refresh_token']

        refresh_data = {'refresh_token': refresh_token}
        response = api_client.post('/api/v1/auth/refresh/', refresh_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.data

    def test_refresh_with_invalid_token(self, api_client):
        """Refresh with invalid token returns 400."""
        data = {'refresh_token': 'invalid.token.here'}
        response = api_client.post('/api/v1/auth/refresh/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_refresh_without_token(self, api_client):
        """Refresh without token returns 400."""
        response = api_client.post('/api/v1/auth/refresh/', {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogoutAPI:
    """Tests for POST /api/v1/auth/logout/."""

    def test_logout_authenticated(self, auth_client):
        """Authenticated user can logout."""
        response = auth_client.post('/api/v1/auth/logout/')
        assert response.status_code == status.HTTP_200_OK

    def test_logout_unauthenticated(self, api_client):
        """Unauthenticated user cannot logout."""
        response = api_client.post('/api/v1/auth/logout/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
