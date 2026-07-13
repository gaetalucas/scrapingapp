from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.products.views import ProductViewSet
from apps.sellers.views import SellerViewSet
from apps.brands.views import BrandViewSet
from apps.categories.views import CategoryViewSet
from apps.channels.views import ChannelViewSet
from apps.auth_custom.views import AuthViewSet

# Crear router
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'sellers', SellerViewSet, basename='seller')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'channels', ChannelViewSet, basename='channel')
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
]