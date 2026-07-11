# CLAUDE.md — Guía Práctica de Desarrollo
## Pulso Fase 1 — Para Ejecutar en Claude Code

---

## 1. SETUP INICIAL (5 minutos)

### 1.1 Crear repo y estructura base

```bash
# Crear carpeta del proyecto
mkdir pulso && cd pulso

# Inicializar git
git init
git remote add origin <tu-repo-url>

# Crear estructura
mkdir -p apps/{products,sellers,categories,brands,channels,auth}
mkdir -p templates/{products,sellers,includes}
mkdir -p static/css
mkdir -p tests

# Crear archivos base
touch manage.py requirements.txt .env.example README.md
```

### 1.2 Crear virtual environment e instalar deps

```bash
# Virtual env
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install django==4.2.13
pip install djangorestframework==3.14.0
pip install psycopg2-binary==2.9.9
pip install python-decouple==3.8
pip install pyjwt==2.8.1
pip install pytest==7.4.3
pip install pytest-django==4.7.0
pip install factory-boy==3.3.0
pip install ruff==0.1.8
pip install python-dateutil==2.8.2
pip install openpyxl==3.10.10
pip install sentry-sdk==1.38.0

# Guardar deps
pip freeze > requirements.txt
```

### 1.3 Crear Django project

```bash
django-admin startproject pulso_config .
python manage.py startapp products
python manage.py startapp sellers
python manage.py startapp categories
python manage.py startapp brands
python manage.py startapp channels
python manage.py startapp auth_custom
python manage.py startapp tenants
```

### 1.4 Estructura final esperada

```
pulso/
├── pulso_config/
│   ├── __init__.py
│   ├── settings.py          # Aquí va toda la config
│   ├── urls.py              # URLs principales
│   ├── asgi.py
│   ├── wsgi.py
├── apps/
│   ├── __init__.py
│   ├── tenants/
│   │   ├── models.py        # Tenant, User
│   │   ├── admin.py
│   │   ├── apps.py
│   ├── products/
│   │   ├── models.py        # Product
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tests.py
│   │   ├── admin.py
│   ├── sellers/
│   │   ├── (idem)
│   ├── categories/
│   │   ├── (idem)
│   ├── brands/
│   │   ├── (idem)
│   ├── channels/
│   │   ├── (idem)
│   ├── auth_custom/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
├── templates/
│   ├── base.html
│   ├── products/
│   ├── sellers/
├── static/
│   ├── css/
│   │   ├── tailwind.css
├── tests/
│   ├── conftest.py
│   ├── test_products.py
│   ├── test_auth.py
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
```

---

## 2. CONFIGURACIÓN DE DJANGO (settings.py)

### 2.1 Instaladas apps

```python
# pulso_config/settings.py

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # DRF
    'rest_framework',
    
    # Nuestras apps
    'apps.tenants',
    'apps.products',
    'apps.sellers',
    'apps.categories',
    'apps.brands',
    'apps.channels',
    'apps.auth_custom',
]

# DRF Config
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# JWT Config
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'pulso'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Timezone
TIME_ZONE = 'America/Argentina/Buenos_Aires'

# Sentry (Opcional para producción)
import sentry_sdk
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN', ''),
    traces_sample_rate=0.1,
)
```

### 2.2 .env.example

```
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production

DB_NAME=pulso
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

ALLOWED_HOSTS=localhost,127.0.0.1

JWT_SECRET=your-jwt-secret-here

SENTRY_DSN=
R2_ACCESS_KEY=
R2_SECRET_KEY=
```

---

## 3. WORKFLOW DEV (Día a Día)

### 3.1 Crear nueva feature

```bash
# Crear branch
git checkout -b feat/agregar-producto

# Editar models.py (ej: apps/products/models.py)
# ...código...

# Crear migration
python manage.py makemigrations products

# Revisar migration (opcional)
cat apps/products/migrations/0001_initial.py

# Aplicar migration
python manage.py migrate

# Editar serializers.py
# ...código...

# Editar views.py
# ...código...

# Editar urls.py
# ...código...

# Escribir tests (tests/test_products.py)
# ...tests...

# Correr tests
pytest tests/test_products.py -v

# Si falla, debug
python manage.py shell
>>> from apps.products.models import Product
>>> Product.objects.all()

# Linting
ruff check apps/products/

# Commit
git add .
git commit -m "feat: agregar CRUD productos"

# Push
git push origin feat/agregar-producto

# Crear PR en GitHub
```

### 3.2 Testing Pattern (TDD)

```python
# tests/test_products.py

import pytest
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant
from apps.products.models import Product, Brand, Category

User = get_user_model()

@pytest.fixture
def tenant():
    return Tenant.objects.create(name="Samsung", slug="samsung")

@pytest.fixture
def user(tenant):
    return User.objects.create_user(
        email="test@samsung.com",
        password="test123",
        tenant=tenant
    )

@pytest.fixture
def brand(tenant):
    return Brand.objects.create(tenant=tenant, name="Samsung")

@pytest.fixture
def category(tenant):
    return Category.objects.create(tenant=tenant, name="Smartphones")

def test_create_product(user, brand, category, tenant):
    """Test crear producto exitoso"""
    product = Product.objects.create(
        tenant=tenant,
        name="Galaxy S24",
        brand=brand,
        model="S24",
        category=category,
        sku="SM-S24",
        pvp_full=1199000,
    )
    assert product.name == "Galaxy S24"
    assert product.sku == "SM-S24"

def test_product_sku_uniqueness(user, brand, category, tenant):
    """Test SKU único por tenant"""
    Product.objects.create(
        tenant=tenant,
        name="Galaxy S24",
        brand=brand,
        model="S24",
        category=category,
        sku="SM-S24",
        pvp_full=1199000,
    )
    
    with pytest.raises(IntegrityError):
        Product.objects.create(
            tenant=tenant,
            name="Galaxy S24 Otro",
            brand=brand,
            model="S24",
            category=category,
            sku="SM-S24",  # ← Duplicado
            pvp_full=1200000,
        )

def test_tenant_isolation(user, brand, category, tenant):
    """Test aislamiento multi-tenant (CRÍTICO)"""
    # Tenant 2
    tenant2 = Tenant.objects.create(name="LG", slug="lg")
    brand2 = Brand.objects.create(tenant=tenant2, name="LG")
    category2 = Category.objects.create(tenant=tenant2, name="Televisores")
    
    # Producto en Tenant 1
    p1 = Product.objects.create(
        tenant=tenant,
        name="Galaxy S24",
        brand=brand,
        model="S24",
        category=category,
        sku="SM-S24",
        pvp_full=1199000,
    )
    
    # Producto en Tenant 2
    p2 = Product.objects.create(
        tenant=tenant2,
        name="LG TV",
        brand=brand2,
        model="55",
        category=category2,
        sku="LG55",
        pvp_full=2000000,
    )
    
    # Verifica aislamiento
    assert Product.objects.filter(tenant=tenant).count() == 1
    assert Product.objects.filter(tenant=tenant2).count() == 1
    assert p1 in Product.objects.filter(tenant=tenant)
    assert p2 not in Product.objects.filter(tenant=tenant)  # ← CRÍTICO
```

### 3.3 Debugging Tips

```bash
# Django shell
python manage.py shell

>>> from apps.products.models import Product
>>> from apps.tenants.models import Tenant
>>> tenant = Tenant.objects.first()
>>> Product.objects.filter(tenant=tenant)
<QuerySet [<Product: Galaxy S24>]>

# SQL directo
python manage.py dbshell
postgres=# SELECT * FROM products_product WHERE tenant_id = 'xxx';

# PDB breakpoint (en código)
def my_view(request):
    breakpoint()  # ← Se pausa aquí
    return Response(data)

# Logs
python manage.py runserver --verbosity=2
```

---

## 4. MULTI-TENANT PATTERN (CRÍTICO)

### 4.1 En Models

```python
# apps/products/models.py

from django.db import models
from apps.tenants.models import Tenant

class Product(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    pvp_full = models.BigIntegerField()
    pvp_promo = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('paused', 'Paused'),
            ('archived', 'Archived'),
        ],
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['tenant', 'sku']]
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
```

### 4.2 En Views/Serializers

```python
# apps/products/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.products.models import Product
from apps.products.serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        # CRÍTICO: filtrar por tenant del usuario
        return Product.objects.filter(
            tenant_id=self.request.user.tenant_id
        ).select_related('brand', 'category')
    
    def perform_create(self, serializer):
        # CRÍTICO: asignar tenant automáticamente
        serializer.save(tenant_id=self.request.user.tenant_id)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['tenant_id'] = self.request.user.tenant_id
        return context
```

### 4.3 En Serializers

```python
# apps/products/serializers.py

from rest_framework import serializers
from apps.products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'brand', 'model', 'category', 'sku', 'pvp_full', 'pvp_promo', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        # Validar pvp_promo ≤ pvp_full
        if data.get('pvp_promo') and data['pvp_promo'] > data['pvp_full']:
            raise serializers.ValidationError(
                "PVP Promo must be ≤ PVP Full"
            )
        return data
```

### 4.4 Tests Multi-tenant

```python
def test_tenant_isolation_api(client, user, user2, tenant, tenant2):
    """Test API respeta tenant isolation"""
    # User 1 crea producto en Tenant 1
    response = client.post('/api/v1/products/', data={...}, headers={'Authorization': f'Bearer {token1}'})
    assert response.status_code == 201
    product_id = response.data['id']
    
    # User 2 (Tenant 2) intenta acceder producto de Tenant 1
    response = client.get(f'/api/v1/products/{product_id}/', headers={'Authorization': f'Bearer {token2}'})
    assert response.status_code == 404  # ← No ve el producto
```

---

## 5. GIT WORKFLOW

### 5.1 Conventional Commits

```bash
git commit -m "feat: agregar CRUD productos"         # Feature nueva
git commit -m "fix: validar pvp_promo <= pvp_full"  # Bug fix
git commit -m "refactor: reorganizar serializers"    # Código limpio
git commit -m "test: agregar test tenant isolation"  # Tests
git commit -m "docs: actualizar SPEC.md"             # Docs
git commit -m "chore: actualizar requirements.txt"   # Admin
```

### 5.2 Branches

```bash
git checkout -b feat/agregar-productos      # Feature
git checkout -b fix/validacion-sku           # Bug
git checkout -b refactor/models              # Refactor
git checkout -b test/multi-tenant            # Tests
```

### 5.3 Push y PR

```bash
git push origin feat/agregar-productos
# Luego crear PR en GitHub
# → Review
# → Approve
# → Merge a main
```

---

## 6. COMANDOS ÚTILES

```bash
# Crear migration
python manage.py makemigrations <app>

# Aplicar migrations
python manage.py migrate

# Crear super usuario
python manage.py createsuperuser

# Shell interactivo
python manage.py shell

# Database shell
python manage.py dbshell

# Tests
pytest                                    # Todos
pytest tests/test_products.py             # Un archivo
pytest tests/test_products.py::test_create_product -v  # Test específico
pytest --cov=apps --cov-report=html       # Coverage

# Linting
ruff check .                               # Check
ruff check . --fix                         # Auto-fix

# Dev server
python manage.py runserver                 # localhost:8000
python manage.py runserver 0.0.0.0:8000   # Accesible desde otros hosts

# Dump/Restore data
python manage.py dumpdata > backup.json
python manage.py loaddata backup.json

# Ver queries ejecutadas
python manage.py shell
>>> from django.db import connection
>>> connection.queries  # ← Todas las queries
```

---

## 7. ESTRUCTURA DE CARPETAS POR MÓDULO

### Cada app (ej: products/) debe tener:

```
apps/products/
├── __init__.py
├── models.py           # Modelos, validaciones
├── serializers.py      # DRF serializers
├── views.py            # ViewSets, permisos
├── urls.py             # Rutas /api/v1/products/
├── admin.py            # Django admin (opcional)
├── apps.py             # Config app (auto)
├── tests.py            # Tests unitarios
└── migrations/         # Auto-generadas
    ├── 0001_initial.py
    └── ...
```

---

## 8. LOGGING

### 8.1 Setup en settings.py

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

### 8.2 Usar en código

```python
import logging

logger = logging.getLogger(__name__)

def create_product(request):
    logger.info(f"User {request.user.id} creating product")
    # ... código ...
    logger.error(f"Failed to create product: {error}")
```

---

## 9. DEPLOYMENT (Railway)

### 9.1 Conectar GitHub

```bash
# 1. Push a GitHub
git push origin main

# 2. En Railway.app
# - Connect GitHub repo
# - Select branch (main)
# - Auto deploy on push
```

### 9.2 Env vars en Railway

```
DEBUG=False
SECRET_KEY=<generate-random>
DATABASE_URL=postgresql://user:pass@host:port/dbname
ALLOWED_HOSTS=pulso.railway.app
JWT_SECRET=<generate-random>
SENTRY_DSN=<optional>
```

### 9.3 Migrations automáticas

```bash
# Agregar a Procfile (Railway auto-ejecuta)
release: python manage.py migrate
web: gunicorn pulso_config.wsgi
```

### 9.4 Ver logs

```bash
# Si usas Railway CLI
railway logs

# O en Dashboard
Dashboard → Logs → View all logs
```

---

## 10. CHECKLIST PRE-DEPLOYMENT

### Antes de push a main:

- ✅ `pytest` — Todos los tests pasan
- ✅ `pytest --cov=apps` — Cobertura >80%
- ✅ `ruff check .` — Código limpio
- ✅ Migraciones creadas y probadas en local
- ✅ .env.example actualizado
- ✅ SPEC.md actualizado si hay cambios de API
- ✅ Commits con mensajes claros
- ✅ Branch limpio (ningún debug código)

---

## 11. TROUBLESHOOTING

### Problema: `ModuleNotFoundError: No module named 'apps'`
```
Solución: Asegurar que PYTHONPATH incluye el directorio raíz
export PYTHONPATH="${PYTHONPATH}:/path/to/pulso"
```

### Problema: `ProgrammingError: relation "products_product" does not exist`
```
Solución: Ejecutar migrations
python manage.py migrate
```

### Problema: `UNIQUE constraint failed: products_product.tenant_id, products_product.sku`
```
Solución: SKU duplicado en mismo tenant
Revisar datos de entrada, cambiar SKU o limpiar DB
```

### Problema: Tests fallan con `IntegrityError`
```
Solución: Usa `@pytest.mark.django_db` en tests que usan DB
@pytest.mark.django_db
def test_my_function():
    ...
```

---

## PRÓXIMOS PASOS

1. Ejecutar Sesión 1 con Claude Code (generara DB schema + models)
2. Ejecutar Sesión 2 (genera API endpoints)
3. Ejecutar Sesión 3 (genera frontend HTML/HTMX)
4. Ejecutar Sesión 4 (genera tests + deploy config)
5. Deploy a Railway
6. Fase 2: Scraping + Seguimiento

