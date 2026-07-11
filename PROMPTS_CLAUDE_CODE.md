# PROMPTS_CLAUDE_CODE.md
## 4 Sesiones para Codificar Pulso Fase 1 Completo

**INSTRUCCIONES DE USO:**
1. Abre Claude Code
2. Copia COMPLETO el prompt de abajo (desde "# SESIÓN 1" hasta "--- END ---")
3. Pega en Claude Code
4. Espera a que complete
5. Cuando termine, ejecuta Sesión 2, luego 3, luego 4

---

## SESIÓN 1: Database Schema + Django Setup + Models

```
# SESIÓN 1: DATABASE SCHEMA & DJANGO MODELS

Eres un arquitecto Django senior. Vas a generar el scaffold inicial para Pulso Fase 1.

## CONTEXTO
- Stack: Python 3.11 + Django 4.2 + DRF 3.14
- Database: PostgreSQL
- Modelo: Multi-tenant (tenant_id en cada tabla)
- Tenant demo: Samsung Argentina
- Objetivo: Generación de datos (Productos, Sellers, Categorías, Marcas, Canales)

## A GENERAR

### 1. manage.py
Archivo Django estándar (cópialo de Django 4.2)

### 2. requirements.txt
```
Django==4.2.13
djangorestframework==3.14.0
psycopg2-binary==2.9.9
python-decouple==3.8
PyJWT==2.8.1
pytest==7.4.3
pytest-django==4.7.0
factory-boy==3.3.0
ruff==0.1.8
openpyxl==3.10.10
sentry-sdk==1.38.0
gunicorn==21.2.0
whitenoise==6.6.0
```

### 3. .env.example
```
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=pulso
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
JWT_SECRET=your-jwt-secret-here
```

### 4. pulso_config/settings.py
DEBE incluir:
- Installed apps (rest_framework, todas las apps)
- Database PostgreSQL
- REST_FRAMEWORK config (pagination, auth)
- TIME_ZONE = 'America/Argentina/Buenos_Aires'
- STATIC_URL y STATIC_ROOT
- Logging config básico
- JWT config
- CORS (si aplica)
- Load .env con python-decouple
- Debug based on DEBUG env var

### 5. pulso_config/urls.py
Rutas principales incluyendo:
- /admin/
- /api/v1/ (namespace para API)
- Static files en DEBUG mode

### 6. apps/tenants/models.py
Tabla TENANTS:
- id UUID primary key
- name VARCHAR unique
- slug VARCHAR unique
- timezone VARCHAR default 'America/Argentina/Buenos_Aires'
- plan VARCHAR (starter, professional, enterprise)
- active BOOLEAN default True
- created_at TIMESTAMP
- updated_at TIMESTAMP

### 7. apps/tenants/models.py - Agregar User model
Extiende Django User o crea custom User:
- id UUID
- tenant FK a Tenants (cascade)
- email UNIQUE per tenant
- password_hash
- name VARCHAR
- role VARCHAR (admin, manager, analyst, viewer)
- status VARCHAR (active, invited, inactive)
- last_login TIMESTAMP
- created_at, updated_at
- Métodos: __str__, get_full_name()

### 8. apps/brands/models.py
Tabla BRANDS:
- id UUID
- tenant_id FK (cascade)
- name VARCHAR unique per tenant
- created_at, updated_at
- updated_by FK to User
- __str__ return name

### 9. apps/categories/models.py
Tabla CATEGORIES (misma estructura que BRANDS):
- id UUID
- tenant_id FK
- name VARCHAR unique per tenant
- created_at, updated_at
- updated_by FK to User

### 10. apps/channels/models.py
Tabla CHANNELS (misma estructura):
- id UUID
- tenant_id FK
- name VARCHAR unique per tenant
- created_at, updated_at
- updated_by FK to User

### 11. apps/sellers/models.py
Tabla SELLERS:
- id UUID
- tenant_id FK
- name VARCHAR unique per tenant
- url VARCHAR optional
- contact_email VARCHAR optional
- contact_phone VARCHAR optional
- created_at, updated_at
- updated_by FK to User
- __str__ return name

### 12. apps/products/models.py (CORE)
Tabla PRODUCTS:
- id UUID primary key
- tenant_id FK (cascade)
- name VARCHAR NOT NULL
- brand_id FK to Brand (restrict)
- model VARCHAR
- category_id FK to Category (restrict)
- sku VARCHAR UNIQUE per tenant
- pvp_full BIGINT (cents: 1199000 = $11.990)
- pvp_promo BIGINT nullable
- status VARCHAR (active, paused, archived) default active
- created_at, updated_at
- updated_by FK to User
- Meta: unique_together = [['tenant', 'sku']], indexes para (tenant, status), (tenant, category)
- __str__ return f"{name} ({sku})"

### 13. apps/products/models.py - Agregar PriceImport model
Tabla PRICE_IMPORTS (para auditar imports):
- id UUID
- tenant_id FK
- filename VARCHAR
- imported_by FK to User
- row_count INT
- success_count INT
- error_count INT
- status VARCHAR (pending, completed, failed)
- error_details TEXT (JSON)
- created_at TIMESTAMP

### 14. apps/products/models.py - Agregar AuditLog model
Tabla AUDIT_LOG (compliance):
- id UUID
- tenant_id FK
- user_id FK to User (nullable)
- entity_type VARCHAR (product, seller, category, brand, channel)
- entity_id UUID
- action VARCHAR (create, update, delete, archive, import)
- old_values JSONB
- new_values JSONB
- ip_address VARCHAR optional
- user_agent VARCHAR optional
- created_at TIMESTAMP
- Meta: indexes para (tenant_id), (entity_type, entity_id), (created_at DESC)

## VALIDACIONES A INCLUIR

En cada modelo, agregar:
- Método clean() que valida reglas (ej: pvp_promo ≤ pvp_full)
- Llamar full_clean() antes de save
- __str__() retorna algo legible

En Product específicamente:
- Validar pvp_promo ≤ pvp_full
- Validar pvp_full > 0
- Validar name no vacío
- Validar sku no vacío

## INITIAL MIGRATION

Después de crear todos los modelos:
```bash
python manage.py makemigrations tenants products brands categories channels sellers
python manage.py migrate
```

Luego generar el archivo de migration (puedes incluirlo en output)

## ADMIN SETUP

Crear apps/*/admin.py simple:
```python
from django.contrib import admin
from .models import MyModel

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name']
```

## EXTRA

- Crear un fixture inicial (JSON) con Samsung Argentina como tenant
- Crear 3 usuarios demo (admin, manager, analyst) para Samsung Argentina
- Crear 5 brands, 6 categorías, 5 canales
- Crear 3 productos de demo (Galaxy S24, Neo QLED, Soundbar)
- Crear 3 sellers de demo (Frávega, Garbarino, Musimundo)

Guardarlo como: fixtures/initial_data.json
Cargar con: python manage.py loaddata fixtures/initial_data.json

## NOTA CRÍTICA

- TODOS los modelos deben tener tenant_id (multi-tenant)
- NUNCA crear un queryset sin filtrar por tenant_id
- Usar UUIDs para IDs (más seguros que integers)
- Timestamps en UTC (Django default)
- Índices en campos de query (tenant_id + status, tenant_id + category, etc.)

Genera todos los archivos listos para `python manage.py migrate`.
Incluye docstrings en cada modelo.
```

--- END SESIÓN 1 ---
```

---

## SESIÓN 2: API REST Endpoints (DRF)

```
# SESIÓN 2: API REST ENDPOINTS (DRF)

Eres un senior DRF developer. Vas a generar todos los endpoints REST para Fase 1.

## CONTEXTO
- Ya tenemos: models.py de Sesión 1
- Necesitamos: serializers + views + urls para cada app
- Multi-tenant: cada query filtra por tenant_id del usuario
- Auth: JWT (simple, sin refresh por ahora)

## A GENERAR

### APPS: products, sellers, brands, categories, channels

Para CADA app, generar:

1. **serializers.py**
   - ModelSerializer para el modelo
   - Incluir validation (ej: pvp_promo ≤ pvp_full)
   - Read-only fields: id, created_at, updated_at
   - Method field para brand.name, category.name, etc. (nested)

2. **views.py**
   - ViewSet con: list, create, retrieve, update, partial_update, destroy
   - Custom actions: /archive/, /unarchive/ (solo products)
   - get_queryset() filtra por tenant_id
   - perform_create() asigna tenant_id automáticamente
   - Filtros: FilterSet o simple __contains
   - Pagination: default 50 items

3. **urls.py**
   - Router.register() las viewsets
   - urlpatterns = router.urls

### SPECIAL: PRODUCTS APP

Además de CRUD básico:

1. POST /api/v1/products/import/
   - Recibe Excel file
   - Valida columnas: Nombre, Marca, Modelo, SKU, Categoría, PVP Full, PVP Promo
   - Retorna preview (primeras 5 filas)
   - Guarda en session para /confirm_import/

2. POST /api/v1/products/import/confirm/
   - Recibe session_id
   - Inserta todas las filas válidas
   - Crea PriceImport record
   - Retorna: imported count, skipped count

3. GET /api/v1/products/export/
   - Retorna Excel file descargable
   - Columnas: Nombre, Marca, Modelo, SKU, Categoría, PVP Full, PVP Promo

### AUTH APP

1. POST /api/v1/auth/login/
   - Body: email, password
   - Retorna: access_token, refresh_token, user data
   - Crea JWT (sign con SECRET_KEY)

2. POST /api/v1/auth/refresh/
   - Body: refresh_token
   - Retorna: new access_token

3. POST /api/v1/auth/logout/
   - Blacklist token (opcional, simple por ahora)

## MIDDLEWARE & PERMISSIONS

1. Create custom permission class:
   ```python
   class IsTenantUser(permissions.BasePermission):
       def has_permission(self, request, view):
           return request.user and request.user.is_authenticated
       
       def has_object_permission(self, request, view, obj):
           return obj.tenant_id == request.user.tenant_id
   ```

2. Create middleware para agregar tenant_id a request:
   ```python
   class TenantMiddleware:
       def __init__(self, get_response):
           self.get_response = get_response
       
       def __call__(self, request):
           # Extract tenant_id from JWT token
           # request.user.tenant_id = <extraído del token>
           response = self.get_response(request)
           return response
   ```

## RESPONSE FORMAT

Todas las respuestas (lista, create, etc.):
```json
{
  "success": true,
  "data": { ... } o [...],
  "error": null,
  "meta": {
    "timestamp": "...",
    "pagination": { "count": 10, "page": 1 }
  }
}
```

Error responses:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "...",
    "details": { "field": ["error1", "error2"] }
  }
}
```

Use custom Response renderer si necesario, o modifica en views.

## VALIDATION

En serializers, agregar:
- `validate_sku()` — unique per tenant
- `validate()` — cross-field validation (pvp_promo ≤ pvp_full)
- `validate_url()` — sellers URL válida

## FILTERS

Para cada viewset:
- searchs: name, sku (products), email (users), url (sellers)
- filters: status (products), role (users)
- ordering: -created_at

## PERMISSIONS

- GET: authenticated users
- POST/PATCH/DELETE: admin y manager solamente
- Viewers: read-only

Usar:
```python
from rest_framework.permissions import IsAuthenticated

class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsTenantUser]
```

## ESTRUCTURA URLs

```
GET    /api/v1/products/                    → list
POST   /api/v1/products/                    → create
GET    /api/v1/products/{id}/               → retrieve
PATCH  /api/v1/products/{id}/               → partial_update
DELETE /api/v1/products/{id}/               → destroy
POST   /api/v1/products/{id}/archive/       → archive
POST   /api/v1/products/{id}/unarchive/     → unarchive
POST   /api/v1/products/import/             → import preview
POST   /api/v1/products/import/confirm/     → confirm import
GET    /api/v1/products/export/             → download Excel

GET    /api/v1/sellers/                     → list
POST   /api/v1/sellers/                     → create
... (DELETE, PATCH, etc.)

GET    /api/v1/brands/
GET    /api/v1/categories/
GET    /api/v1/channels/
... (igual CRUD para cada)

POST   /api/v1/auth/login/
POST   /api/v1/auth/refresh/
POST   /api/v1/auth/logout/
```

## NOTA CRÍTICA

- get_queryset() SIEMPRE filtra por tenant_id=request.user.tenant_id
- NUNCA retornar objeto de otro tenant
- perform_create() SIEMPRE asigna tenant_id
- Tests deben verificar tenant isolation

Genera serializers.py, views.py, urls.py para cada app.
Incluye docstrings en cada método.
Incluye type hints.
```

--- END SESIÓN 2 ---
```

---

## SESIÓN 3: Frontend HTML + HTMX

```
# SESIÓN 3: FRONTEND HTML + HTMX

Eres un frontend dev con expertise en Django templates + HTMX + Tailwind.

## CONTEXTO
- Ya tenemos API REST funcionando
- Necesitamos: HTML templates + HTMX para operaciones CRUD
- Stack: Django templates, HTMX, Tailwind CSS
- UX: responsivo, bonito, rápido (sin full page reload)
- Focus: modales, tablas interactivas, formularios

## A GENERAR

### 1. templates/base.html
- Head: Tailwind CDN, HTMX CDN
- Navbar: logo + menu navegación
- Sidebar: nav con módulos (Productos, Sellers, Categorías y Marcas, etc.)
- Footer: copyright
- Block content para templates hijas

### 2. templates/includes/header.html
- Navbar con logo "Pulso" + usuario info + logout
- Links a: Productos, Seguimiento, Scoring, Timeline, Configuración

### 3. templates/includes/sidebar.html
- Links a cada módulo
- Data-view attributes para HTMX
- Icons de FontAwesome o SVG

### 4. templates/products/list.html
- Tabla: Producto | Marca | Modelo | Categoría | SKU | PVP Full | PVP Promo | Acciones
- Pestañas: Activos | Archivados (con indicador activo)
- Botón "Nuevo producto"
- Botón "Importar" + "Exportar"
- Búsqueda por SKU (con debounce HTMX)
- Paginación (prev/next)

### 5. templates/products/modal_nuevo.html
- Modal form con campos:
  - Nombre (text input)
  - Marca (select dropdown, poblado por API)
  - Modelo (text input)
  - Categoría (select dropdown, poblado por API)
  - SKU (text input)
  - PVP Full (number input)
  - PVP Promo (number input, optional)
- Botones: Cancelar, Guardar
- Validación frontend simple (required fields)
- Mensajes de error si falla (toast)

### 6. templates/products/modal_edit_price.html
- Modal pequeño para editar precio rápido
- Campos: PVP Full, PVP Promo
- Botones: Cancelar, Guardar

### 7. templates/products/modal_import.html
- File upload input
- Drag & drop area
- Preview de primeras 5 filas (tabla)
- Contador: "148 de 150 válidos"
- Botones: Cancelar, Confirmar importación

### 8. templates/sellers/list.html
- Tabla: Nombre | URL | Email | Teléfono | Acciones
- Botón "Nuevo seller"
- Búsqueda

### 9. templates/sellers/modal_nuevo.html
- Campos: Nombre, URL, Email, Teléfono
- Validación URL

### 10. templates/categories/list.html
- Pestañas: Categorías | Marcas
- Tab 1: Tabla Categorías (Nombre | Acciones)
- Tab 2: Tabla Marcas (Nombre | Acciones)
- Botón "Nueva categoría/marca"

### 11. templates/channels/list.html
- Tabla: Nombre | Acciones
- Botón "Nuevo canal"

### 12. templates/seguimiento/list.html
- Tabla grande con columnas:
  Producto (Marca | Modelo | Categoría | SKU | PVP Full | PVP Promo) | Seller | Canal | 🔔 Alertas
- Botón "Nuevo seguimiento"
- Filas altas (2-3 líneas)
- Hover effects

### HTMX PATTERNS

1. Crear producto:
```html
<button hx-get="/products/modal_nuevo/" 
        hx-target="#modals"
        hx-swap="innerHTML">
  Nuevo
</button>

<!-- Modal form submitea con hx-post -->
<form hx-post="/api/v1/products/"
      hx-target="#products-table"
      hx-swap="outerHTML">
  ...
</form>
```

2. Editar precio:
```html
<button hx-get="/products/{{ product.id }}/modal_edit_price/"
        hx-target="#modals"
        hx-swap="innerHTML">
  ✏️
</button>
```

3. Archivar:
```html
<button hx-post="/products/{{ product.id }}/archive/"
        hx-confirm="¿Archivar este producto?"
        hx-target="closest tr"
        hx-swap="outerHTML swap:1s">
  📦
</button>
```

4. Búsqueda (debounce):
```html
<input type="text"
       name="search"
       hx-get="/api/v1/products/"
       hx-trigger="keyup changed delay:500ms"
       hx-target="#products-table"
       hx-swap="innerHTML"
       placeholder="Buscar por SKU...">
```

5. Importar Excel:
```html
<input type="file"
       hx-post="/api/v1/products/import/"
       hx-target="#import-preview"
       hx-swap="innerHTML"
       accept=".xlsx,.csv">
```

### DISEÑO TAILWIND

- Color primario: slate-800 (nav, botones)
- Colores semáforo: rojo #ef4444, amarillo #f59e0b, verde #10b981
- Espacios: gap-4, p-5, px-3
- Rounded: rounded-lg (modales), rounded-xl (cards)
- Shadows: shadow-md on hover
- Typography: font-display (títulos), text-sm (body)
- Responsive: lg: grid-cols-3 (desktop), col-span-full (mobile)

### COMPONENTS

Crear componentes reutilizables en includes/:
- btn-primary.html (botón principal)
- btn-secondary.html
- badge.html (para status, tags)
- input-text.html
- input-number.html
- select.html (dropdown)
- modal-base.html
- table-base.html
- toast.html (notificaciones)

### INTERACTIVIDAD

- Toast notifications: POST exitoso → toast verde "✓ Guardado"
- Modales con close button + click outside para cerrar
- Loading spinner mientras POST/PATCH
- Validación frontend simple (required, email format)
- Hover effects en filas de tabla
- Smooth transitions (100ms)

### SEGURIDAD FRONTEND

- CSRF token en forms (Django {% csrf_token %})
- HTTPS everywhere
- No loguear datos sensibles en console
- Validar input antes de HTMX post

## NOTA

- Templates deben extender base.html
- Usar {% load static %} para CSS/JS
- HTMX CDN: https://unpkg.com/htmx.org@1.9.10
- Tailwind CDN: https://cdn.tailwindcss.com
- Responsive-first (mobile → tablet → desktop)

Genera templates listas para usar.
Incluye comentarios en HTML.
Validaciones simples en JS (script tags).
```

--- END SESIÓN 3 ---
```

---

## SESIÓN 4: Tests + Deployment Config

```
# SESIÓN 4: TESTS + DEPLOYMENT CONFIG

Eres un QA architect + DevOps. Vas a generar tests exhaustivos y config deploy.

## CONTEXTO
- Tests: pytest + pytest-django + factory-boy
- Coverage: >80%
- Deployment: Railway (git push = auto deploy)
- Objetivo: Fase 1 lista para producción

## A GENERAR

### 1. tests/conftest.py
Fixtures reutilizables:
- @pytest.fixture tenant() → Samsung Argentina
- @pytest.fixture user() → admin user
- @pytest.fixture user_manager() → manager
- @pytest.fixture user_viewer() → viewer
- @pytest.fixture brand() → Samsung brand
- @pytest.fixture category() → Smartphones category
- @pytest.fixture product() → Galaxy S24
- @pytest.fixture seller() → Frávega
- @pytest.fixture client (autenticado)
- @pytest.fixture client_other_tenant (otro tenant)

### 2. tests/test_models.py
Tests para models:
- test_product_creation_success
- test_product_sku_uniqueness_per_tenant
- test_product_pvp_validation (promo ≤ full)
- test_tenant_isolation (Tenant A ≠ Tenant B)
- test_audit_log_on_create
- test_brand_uniqueness_per_tenant
- test_seller_url_validation

### 3. tests/test_serializers.py
Tests para serializers:
- test_product_serializer_valid
- test_product_serializer_invalid_sku
- test_product_serializer_pvp_validation
- test_brand_serializer_uniqueness

### 4. tests/test_products_api.py
Tests API endpoints (CRÍTICO):
- test_list_products_success
- test_list_products_pagination
- test_list_products_tenant_isolation (Tenant A can't see Tenant B)
- test_create_product_success
- test_create_product_invalid_validation
- test_create_product_requires_auth
- test_create_product_requires_admin_permission
- test_update_product_success
- test_archive_product_success
- test_archive_product_moves_to_archived_tab
- test_delete_product_success
- test_import_products_excel_success
- test_import_products_excel_validation_fails
- test_import_products_confirm_creates_records
- test_export_products_returns_excel
- test_export_products_includes_all_columns

### 5. tests/test_sellers_api.py
Tests sellers endpoints:
- test_list_sellers_success
- test_create_seller_success
- test_seller_url_validation
- test_update_seller_success
- test_delete_seller_success

### 6. tests/test_brands_api.py
Tests brands endpoints:
- test_list_brands_success
- test_create_brand_success
- test_brand_uniqueness_per_tenant

### 7. tests/test_auth_api.py
Tests auth:
- test_login_success
- test_login_invalid_credentials
- test_login_returns_jwt_token
- test_refresh_token_success
- test_expired_token_fails

### 8. pytest.ini
```ini
[pytest]
DJANGO_SETTINGS_MODULE = pulso_config.settings
python_files = tests.py test_*.py *_tests.py
addopts = --cov=apps --cov-report=html --cov-report=term
testpaths = tests
```

### 9. CI/CD: .github/workflows/test.yml
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run linting
      run: ruff check .
    
    - name: Run tests
      run: pytest
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/pulso_test
```

### 10. Procfile (Railway)
```
release: python manage.py migrate
web: gunicorn pulso_config.wsgi --log-file -
```

### 11. railway.json (Railway config)
```json
{
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "restartPolicyType": "always",
    "restartPolicyMaxRetries": 10
  }
}
```

### 12. Dockerfile (opcional pero recomendado)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "pulso_config.wsgi"]
```

### 13. .gitignore
```
*.pyc
__pycache__/
*.egg-info/
dist/
build/
.env
.venv
venv/
env/
*.db
*.sqlite3
.pytest_cache/
htmlcov/
.coverage
.ruff_cache/
```

### 14. README.md
```markdown
# Pulso — Inteligencia de Precios SaaS

## Quick Start

### Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata fixtures/initial_data.json
```

### Dev Server
```bash
python manage.py runserver
# Acceder http://localhost:8000/
# Admin: http://localhost:8000/admin/
```

### Tests
```bash
pytest              # Todos
pytest -v           # Verbose
pytest --cov=apps   # Con coverage
```

### Lint
```bash
ruff check .
ruff check . --fix
```

## Deploy
Push a main → Railway auto deploya
```

## TESTING CHECKLIST

Antes de release:
- ✅ pytest coverage >80%
- ✅ Todos los tests pasan
- ✅ Multi-tenant isolation tested
- ✅ ruff check pasa
- ✅ No hardcoded secrets
- ✅ .env.example actualizado
- ✅ README.md actualizado
- ✅ SPEC.md actualizado

## COVERAGE TARGETS

| Módulo | Target |
|--------|--------|
| products | 90% |
| sellers | 85% |
| brands | 85% |
| categories | 85% |
| channels | 85% |
| auth | 90% |
| **Total** | **85%** |

## NOTA

- Usa @pytest.mark.django_db para tests que usan DB
- Usa fixtures (conftest.py) para reutilizar setup
- Mock external services (email, storage)
- Test edge cases (validaciones, permisos, tenant isolation)
- Naming: test_<unit>_<scenario>_<expected>

Genera tests exhaustivos listos para `pytest`.
Genera CI/CD y deploy config listo para Railway.
```

--- END SESIÓN 4 ---
```

---

## RESUMEN USO

### Orden de Ejecución:
1. **Sesión 1:** Copia prompt completo → Claude Code → Espera a que termine (Models + DB)
2. **Sesión 2:** Copia prompt → Claude Code → Endpoints API (serializers + views)
3. **Sesión 3:** Copia prompt → Claude Code → Frontend (HTML + HTMX)
4. **Sesión 4:** Copia prompt → Claude Code → Tests + Deploy (CI/CD + Railway)

### Después de cada sesión:
```bash
git add .
git commit -m "feat: sesión X completada"
git push origin main
```

### Deploy a Railway:
```bash
# Railway auto-deploy en push a main
# O manual: railway up
# Ver logs: railway logs
```

### Testing:
```bash
pytest                          # Todos
pytest tests/test_products.py   # Un archivo
pytest --cov=apps               # Coverage
```

---

**¡Listo para empezar! Copia el prompt de la Sesión 1 y ejecuta en Claude Code.**
