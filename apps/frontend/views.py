"""Frontend template views — serves HTML pages for the SPA."""

from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def login_view(request):
    """Render login page."""
    return render(request, 'auth/login.html')


@ensure_csrf_cookie
def products_view(request):
    """Render products list page."""
    return render(request, 'products/list.html', {'active_page': 'products'})


@ensure_csrf_cookie
def sellers_view(request):
    """Render sellers list page."""
    return render(request, 'sellers/list.html', {'active_page': 'sellers'})


@ensure_csrf_cookie
def categories_view(request):
    """Render categories and brands page."""
    return render(request, 'categories/list.html', {'active_page': 'categories'})


@ensure_csrf_cookie
def channels_view(request):
    """Render channels page."""
    return render(request, 'channels/list.html', {'active_page': 'channels'})


@ensure_csrf_cookie
def seguimiento_view(request):
    """Render seguimiento page (Phase 2 placeholder)."""
    return render(request, 'seguimiento/list.html', {'active_page': 'seguimiento'})
