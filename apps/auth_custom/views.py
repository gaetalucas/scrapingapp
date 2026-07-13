from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from apps.auth_custom.serializers import LoginSerializer, RefreshTokenSerializer
import jwt
import os
import time

User = get_user_model()


class CustomJWTAuthentication(BaseAuthentication):
    """
    Custom JWT Authentication - valida tokens generados manualmente
    """
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            print("[JWT] No Bearer token found")
            return None
        
        token = auth_header.replace('Bearer ', '', 1)
        secret = os.getenv('JWT_SECRET', 'default-secret-key')
        
        print(f"[JWT] Secret from env: {secret}")
        print(f"[JWT] Token: {token[:50]}...")
        
        try:
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            print(f"[JWT] Payload: {payload}")
        except jwt.ExpiredSignatureError as e:
            print(f"[JWT] Token expirado: {e}")
            raise AuthenticationFailed('Token expirado')
        except jwt.InvalidTokenError as e:
            print(f"[JWT] Token inválido: {e}")
            raise AuthenticationFailed('Token inválido')
        
        try:
            user = User.objects.get(id=payload['user_id'])
            print(f"[JWT] Usuario encontrado: {user.email}")
        except User.DoesNotExist:
            print(f"[JWT] Usuario NO encontrado")
            raise AuthenticationFailed('Usuario no encontrado')
        
        return (user, token)

class AuthViewSet(viewsets.ViewSet):
    """
    Endpoints de autenticación:
    - POST /api/v1/auth/login/ → obtener access_token
    - POST /api/v1/auth/refresh/ → renovar token
    - POST /api/v1/auth/logout/ → logout
    """
    
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """Login: email + password → JWT token"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            access_token = self._generate_token(user, 'access')
            refresh_token = self._generate_token(user, 'refresh')
            
            return Response({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': str(user.id),
                    'name': user.name,
                    'email': user.email,
                    'role': user.role,
                    'tenant_id': str(user.tenant_id),
                }
            }, status=status.HTTP_200_OK)
        
        return Response(
            {'detail': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['post'], url_path='refresh')
    def refresh(self, request):
        """Refresh token: refresh_token → nuevo access_token"""
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            access_token = self._generate_token(user, 'access')
            
            return Response({
                'access_token': access_token,
            }, status=status.HTTP_200_OK)
        
        return Response(
            {'detail': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['post'], url_path='logout', permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Logout: simplemente retorna OK"""
        return Response(
            {'detail': 'Logout exitoso'},
            status=status.HTTP_200_OK
        )
    
    def _generate_token(self, user, token_type='access'):
        """Generar JWT token con timestamps enteros"""
        secret = os.getenv('JWT_SECRET', 'default-secret-key')
        
        if token_type == 'access':
            expires_in = 3600
        else:
            expires_in = 86400 * 7
        
        now = int(time.time())
        
        payload = {
            'user_id': str(user.id),
            'email': user.email,
            'tenant_id': str(user.tenant_id),
            'role': user.role,
            'exp': now + expires_in,
            'iat': now,
            'type': token_type,
        }
        
        token = jwt.encode(payload, secret, algorithm='HS256')
        return token