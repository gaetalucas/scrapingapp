"""Pulso URL Configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.auth_custom.views import AuthViewSet
from apps.brands.views import BrandViewSet
from apps.categories.views import CategoryViewSet
from apps.channels.views import ChannelViewSet
from apps.products.views import ProductViewSet
from apps.sellers.views import SellerViewSet

# API Router
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'sellers', SellerViewSet, basename='seller')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'channels', ChannelViewSet, basename='channel')
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/', include(router.urls)),

    # Frontend pages
    path('', include('apps.frontend.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
