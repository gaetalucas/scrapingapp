"""Middleware for JWT authentication and tenant context."""

import logging

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse

logger = logging.getLogger(__name__)

User = get_user_model()

EXEMPT_PATHS = [
    '/api/v1/auth/login/',
    '/api/v1/auth/refresh/',
    '/admin/',
    '/static/',
]


class JWTAuthenticationMiddleware:
    """Extract and validate JWT token, attach user to request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Process request — decode JWT and attach user if valid."""
        if any(request.path.startswith(path) for path in EXEMPT_PATHS):
            return self.get_response(request)

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            try:
                payload = jwt.decode(
                    token, settings.JWT_SECRET, algorithms=['HS256']
                )
                user = User.objects.select_related('tenant').get(
                    id=payload['user_id']
                )
                request.user = user
            except jwt.ExpiredSignatureError:
                return JsonResponse(
                    {'success': False, 'error': {'code': 'TOKEN_EXPIRED', 'message': 'Token has expired'}},
                    status=401,
                )
            except (jwt.InvalidTokenError, User.DoesNotExist, KeyError):
                return JsonResponse(
                    {'success': False, 'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid token'}},
                    status=401,
                )

        return self.get_response(request)
