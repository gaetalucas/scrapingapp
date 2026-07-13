"""Frontend URL configuration — HTML page routes."""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login-page'),
    path('products/', views.products_view, name='products-page'),
    path('sellers/', views.sellers_view, name='sellers-page'),
    path('categories/', views.categories_view, name='categories-page'),
    path('channels/', views.channels_view, name='channels-page'),
    path('seguimiento/', views.seguimiento_view, name='seguimiento-page'),
]
