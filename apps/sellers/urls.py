"""Seller URL configuration."""

from rest_framework.routers import DefaultRouter

from .views import SellerViewSet

router = DefaultRouter()
router.register('', SellerViewSet, basename='seller')

urlpatterns = router.urls
