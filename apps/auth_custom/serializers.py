from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
import jwt
import os

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    """Serializer para login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email o contraseña inválidos")
        
        # Verificar password
        if not check_password(password, user.password):
            raise serializers.ValidationError("Email o contraseña inválidos")
        
        attrs['user'] = user
        return attrs


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer para refresh token"""
    refresh_token = serializers.CharField()
    
    def validate(self, attrs):
        token = attrs.get('refresh_token')
        secret = os.getenv('JWT_SECRET', 'default-secret-key')
        
        try:
            payload = jwt.decode(token, secret, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError("Token expirado")
        except jwt.InvalidTokenError:
            raise serializers.ValidationError("Token inválido")
        
        # Verificar que es un refresh token
        if payload.get('type') != 'refresh':
            raise serializers.ValidationError("Token no es un refresh token")
        
        # Obtener usuario
        try:
            user = User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado")
        
        attrs['user'] = user
        return attrs