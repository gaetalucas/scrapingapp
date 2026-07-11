# SPEC.md — Especificación Técnica Fase 1
## Pulso — Módulo Generación de Datos

---

## 1. RESUMEN EJECUTIVO

### Qué se construye en Fase 1
Backend API REST completo + Frontend CRUD para generar y administrar datos base del proyecto:
- Productos (crear, editar, archivar, importar precios)
- Sellers
- Categorías
- Marcas
- Canales / Puertas de Venta

### Objetivos
1. ✅ Datos consistentes y validados
2. ✅ Multi-tenant isolation (Samsung Argentina aislada)
3. ✅ API REST lista para consumir desde Fase 2 (Scraping)
4. ✅ Audit trail (quién, qué, cuándo)
5. ✅ Frontend operable para agregar/editar datos

### Out of Scope (Fase 2+)
- ❌ Scraping de precios
- ❌ Seguimiento (Producto × Seller × Canal)
- ❌ Capturas de precios
- ❌ Scoring / Timeline / Tablero
- ❌ Alertas
- ❌ Reportes

---

## 2. MODELO DE DATOS (SQL)

### 2.1 Tabla: TENANTS

```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    timezone VARCHAR(50) DEFAULT 'America/Argentina/Buenos_Aires',
    plan VARCHAR(20) DEFAULT 'starter', -- starter, professional, enterprise
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice
CREATE UNIQUE INDEX idx_tenants_slug ON tenants(slug);
```

### 2.2 Tabla: USERS (Multi-tenant)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL, -- admin, manager, analyst, viewer
    status VARCHAR(20) DEFAULT 'active', -- active, invited, inactive
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, email)
);

-- Índices (CRÍTICO para multi-tenant)
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
```

### 2.3 Tabla: BRANDS

```sql
CREATE TABLE brands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id),
    UNIQUE(tenant_id, name)
);

CREATE INDEX idx_brands_tenant_id ON brands(tenant_id);
```

### 2.4 Tabla: CATEGORIES

```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id),
    UNIQUE(tenant_id, name)
);

CREATE INDEX idx_categories_tenant_id ON categories(tenant_id);
```

### 2.5 Tabla: CHANNELS

```sql
CREATE TABLE channels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL, -- Mercado Libre, VTEX, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id),
    UNIQUE(tenant_id, name)
);

CREATE INDEX idx_channels_tenant_id ON channels(tenant_id);
```

### 2.6 Tabla: SELLERS

```sql
CREATE TABLE sellers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(2048),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id),
    UNIQUE(tenant_id, name)
);

CREATE INDEX idx_sellers_tenant_id ON sellers(tenant_id);
```

### 2.7 Tabla: PRODUCTS (CORE)

```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    brand_id UUID NOT NULL REFERENCES brands(id) ON DELETE RESTRICT,
    model VARCHAR(100),
    category_id UUID NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    sku VARCHAR(100) NOT NULL,
    pvp_full BIGINT NOT NULL, -- Cents: 1199000 = $11.990
    pvp_promo BIGINT, -- Can be NULL
    status VARCHAR(20) DEFAULT 'active', -- active, paused, archived
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id),
    UNIQUE(tenant_id, sku)
);

-- Índices (CRÍTICO)
CREATE INDEX idx_products_tenant_id ON products(tenant_id);
CREATE INDEX idx_products_status ON products(tenant_id, status);
CREATE INDEX idx_products_category ON products(tenant_id, category_id);
CREATE INDEX idx_products_brand ON products(tenant_id, brand_id);
```

### 2.8 Tabla: PRICE_IMPORTS (Audit)

```sql
CREATE TABLE price_imports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    imported_by UUID NOT NULL REFERENCES users(id),
    row_count INT,
    success_count INT,
    error_count INT,
    status VARCHAR(20) DEFAULT 'completed', -- pending, completed, failed
    error_details TEXT, -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_price_imports_tenant_id ON price_imports(tenant_id);
```

### 2.9 Tabla: AUDIT_LOG (Compliance)

```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    entity_type VARCHAR(50), -- product, seller, category, brand, channel
    entity_id UUID,
    action VARCHAR(50), -- create, update, delete, archive, import
    old_values JSONB, -- Qué cambió
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_tenant ON audit_log(tenant_id);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_date ON audit_log(created_at DESC);
```

---

## 3. API ENDPOINTS (REST)

### Base URL
```
https://pulso.railway.app/api/v1/
```

### Authentication
```
Header: Authorization: Bearer <JWT_TOKEN>
```

### Response Format
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "timestamp": "2026-07-11T14:32:00Z"
  }
}
```

### 3.1 PRODUCTS Endpoints

#### GET /api/v1/products/
```
Query Params:
  - status: active, archived, all (default: active)
  - category: <category_id> (filter)
  - brand: <brand_id> (filter)
  - search: <query> (busca en name, sku)
  - page: 1 (default)
  - page_size: 50 (default)

Response:
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "name": "Galaxy S24 128GB",
      "brand": {
        "id": "uuid",
        "name": "Samsung"
      },
      "model": "S24",
      "category": {
        "id": "uuid",
        "name": "Smartphones"
      },
      "sku": "SM-S24",
      "pvp_full": 1199000,
      "pvp_promo": null,
      "status": "active",
      "created_at": "2026-07-11T...",
      "updated_at": "2026-07-11T...",
      "updated_by": "lucas@samsung.com.ar"
    }
  ]
}

Status: 200 OK
```

#### POST /api/v1/products/
```
Body:
{
  "name": "Galaxy S24 128GB",
  "brand_id": "uuid",
  "model": "S24",
  "category_id": "uuid",
  "sku": "SM-S24",
  "pvp_full": 1199000,
  "pvp_promo": null
}

Validation:
  ✅ name: required, max 255 chars
  ✅ brand_id: required, must exist
  ✅ model: required, max 100 chars
  ✅ category_id: required, must exist
  ✅ sku: required, unique per tenant, max 100 chars
  ✅ pvp_full: required, positive integer
  ✅ pvp_promo: optional, if present must be ≤ pvp_full

Response:
{
  "id": "uuid",
  "name": "Galaxy S24 128GB",
  ...
}

Errors:
  - 400: Validation failed (sku duplicado, pvp_promo > pvp_full, etc.)
  - 403: Permisos insuficientes (only admin/manager can create)
```

#### PATCH /api/v1/products/{id}/
```
Body (any subset):
{
  "name": "Galaxy S24 256GB",
  "pvp_full": 1299000,
  "pvp_promo": 1199000
}

Response: 200 OK + updated product

Errors:
  - 404: Producto no encontrado
  - 403: No permisos o tenant mismatch
```

#### DELETE /api/v1/products/{id}/
```
Response: 204 No Content

Errors:
  - 404: Producto no existe
  - 403: No permisos
```

#### POST /api/v1/products/{id}/archive/
```
Body: {}

Effect: Cambia status a "archived"
Response: 200 OK + updated product
```

#### POST /api/v1/products/{id}/unarchive/
```
Body: {}

Effect: Cambia status a "active"
Response: 200 OK + updated product
```

#### POST /api/v1/products/import/
```
Body: multipart/form-data
  - file: <Excel/CSV file>

Expected Excel columns:
  - Nombre | Marca | Modelo | SKU | Categoría | PVP Full | PVP Promo

Processing:
  1. Validate columns
  2. Preview (return first 5 rows + validation errors)
  3. Store in session/cache
  4. Wait for /confirm_import

Response:
{
  "session_id": "uuid",
  "preview": [
    {
      "row": 1,
      "name": "Galaxy S24",
      "brand": "Samsung",
      ...
      "status": "valid" or "error",
      "error_message": "..."
    }
  ],
  "total_rows": 150,
  "valid_rows": 148,
  "error_rows": 2
}

Errors:
  - 400: Formato inválido, columnas faltantes
```

#### POST /api/v1/products/import/confirm/
```
Body:
{
  "session_id": "uuid"
}

Effect:
  1. Inserta filas válidas
  2. Crea price_import record
  3. Log en audit_log

Response:
{
  "imported": 148,
  "skipped": 2,
  "import_id": "uuid"
}
```

#### GET /api/v1/products/export/
```
Response: Excel file descargable

Formato:
  Nombre | Marca | Modelo | SKU | Categoría | PVP Full | PVP Promo
```

### 3.2 SELLERS Endpoints (Misma estructura)

```
GET /api/v1/sellers/
POST /api/v1/sellers/
PATCH /api/v1/sellers/{id}/
DELETE /api/v1/sellers/{id}/

Body (POST):
{
  "name": "Frávega",
  "url": "https://www.fravega.com",
  "contact_email": "...",
  "contact_phone": "..."
}
```

### 3.3 BRANDS Endpoints

```
GET /api/v1/brands/
POST /api/v1/brands/
PATCH /api/v1/brands/{id}/
DELETE /api/v1/brands/{id}/

Body (POST):
{
  "name": "Samsung"
}

Validation:
  ✅ name: unique per tenant
```

### 3.4 CATEGORIES Endpoints

```
GET /api/v1/categories/
POST /api/v1/categories/
PATCH /api/v1/categories/{id}/
DELETE /api/v1/categories/{id}/
```

### 3.5 CHANNELS Endpoints

```
GET /api/v1/channels/
POST /api/v1/channels/
PATCH /api/v1/channels/{id}/
DELETE /api/v1/channels/{id}/
```

### 3.6 AUTH Endpoints (Basic)

```
POST /api/v1/auth/login/
Body:
{
  "email": "lucas@samsung.com.ar",
  "password": "..."
}
Response:
{
  "access_token": "jwt...",
  "refresh_token": "jwt...",
  "user": {
    "id": "uuid",
    "name": "Lucas",
    "email": "...",
    "role": "admin"
  }
}

POST /api/v1/auth/refresh/
Body:
{
  "refresh_token": "..."
}
Response:
{
  "access_token": "new_jwt..."
}
```

---

## 4. FRONTEND FLOWS (User Stories)

### Story 1: Crear Producto
```
Actor: Admin / Manager
Steps:
  1. Click "Nuevo producto"
  2. Modal abre con campos:
     - Nombre (text)
     - Marca (dropdown, poblado desde brands)
     - Modelo (text)
     - Categoría (dropdown, poblado desde categories)
     - SKU (text)
     - PVP Full (number)
     - PVP Promo (number, optional)
  3. Click "Guardar"
  4. Backend valida
  5. Si error: muestra toast rojo + campo destaca
  6. Si ok: cierra modal, tabla refresca (HTMX), toast verde "✓ Producto creado"

Expected Time: <5 seconds
```

### Story 2: Editar Precio (Rápido)
```
Actor: Cualquiera
Steps:
  1. En tabla Productos, click botón ✏️ en fila
  2. Modal pequeño: PVP Full + PVP Promo
  3. Click "Guardar"
  4. Tabla actualiza sin reload

Expected Time: <30 seconds
```

### Story 3: Importar Precios (Excel)
```
Actor: Admin
Steps:
  1. Click "Importar"
  2. Drag & drop (o click) archivo Excel
  3. Preview: muestra primeras 5 filas + contador (148/150 válidos)
  4. Si hay errores, muestra cuáles (ej: "Fila 23 — SKU no existe")
  5. Click "Confirmar"
  6. Backend procesa
  7. Toast: "✓ 148 productos importados"

Expected Time: <2 minutes
```

### Story 4: Archivar Producto
```
Actor: Cualquiera
Steps:
  1. Botón "Archivar" en tabla
  2. Confirmación: "¿Seguro?"
  3. Producto desaparece de Activos
  4. Pestaña "Archivados" +1

Expected Time: <10 seconds
```

### Story 5: Administrar Marcas
```
Actor: Admin
Steps:
  1. Click "Categorías y Marcas"
  2. Pestaña "Marcas"
  3. CRUD: crear, editar, borrar
  4. Cambios reflejan en dropdown "Marca" de productos

Expected Time: 1 minute
```

---

## 5. VALIDATION RULES

### Products
```
✅ name: required, 1-255 chars
✅ brand_id: required, must exist
✅ model: required, 1-100 chars
✅ category_id: required, must exist
✅ sku: required, 1-100 chars, UNIQUE per tenant
✅ pvp_full: required, positive, integer (cents)
✅ pvp_promo: optional, if set must be ≤ pvp_full
✅ status: active, paused, archived (default: active)
```

### Sellers
```
✅ name: required, 1-255 chars, UNIQUE per tenant
✅ url: optional, must be valid URL
✅ contact_email: optional, must be valid email
✅ contact_phone: optional, 1-20 chars
```

### Brands, Categories, Channels
```
✅ name: required, 1-255 chars, UNIQUE per tenant
```

---

## 6. ERROR HANDLING

### HTTP Status Codes

| Code | Scenario | Example |
|------|----------|---------|
| 200 | Éxito (GET, PATCH, POST) | Producto actualizado |
| 201 | Creación (POST) | Nuevo seller creado |
| 204 | Éxito sin body (DELETE, archive) | Producto archivado |
| 400 | Validación fallida | pvp_promo > pvp_full |
| 401 | No autenticado | Token ausente/expirado |
| 403 | Permisos insuficientes | Viewer intenta crear producto |
| 404 | Recurso no existe | /products/invalid-id/ |
| 409 | Conflicto (duplicado) | SKU ya existe |
| 422 | Datos inválidos | Marca sin name |
| 500 | Error servidor | Database crash |

### Response Format (Error)

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "PVP Promo must be ≤ PVP Full",
    "details": {
      "pvp_promo": ["PVP Promo must be ≤ PVP Full"]
    }
  }
}
```

---

## 7. TESTING STRATEGY

### Unit Tests (40% cobertura)
```python
test_product_model.py
  - test_product_creation
  - test_sku_uniqueness_per_tenant
  - test_pvp_validation (promo ≤ full)

test_brand_model.py
  - test_brand_creation
  - test_name_uniqueness_per_tenant
```

### Integration Tests (40% cobertura)
```python
test_product_api.py
  - test_create_product_success
  - test_create_product_validation_fails
  - test_tenant_isolation (tenant A can't see tenant B products)
  - test_import_excel_success
  - test_import_excel_validation_fails

test_auth.py
  - test_login_success
  - test_jwt_refresh
  - test_expired_token_fails
```

### E2E Tests (20% cobertura)
```python
test_product_flow.py
  - test_full_create_edit_archive_flow
  - test_multi_user_same_tenant
```

### Acceptance Criteria
- ✅ Cobertura mínima: 80%
- ✅ Críticos: multi-tenant isolation (100% cobertura)
- ✅ Todos los tests pasan antes de deploy

---

## 8. PERFORMANCE TARGETS

| Operación | Target | Notes |
|-----------|--------|-------|
| GET /products/ (50 items) | <200ms | Con índices |
| POST /products/ | <500ms | Validación + DB insert |
| PATCH /products/{id}/ | <300ms | Update + audit log |
| Import 10k rows | <5s | Batch insert |
| Listar 1000 productos | <500ms | Paginación |

### Optimizaciones
- Índices en: tenant_id, status, category_id, brand_id
- Paginación: 50 items default
- Query optimization: SELECT only needed fields
- N+1 prevention: prefetch_related for brands, categories

---

## 9. SEGURIDAD CHECKLIST

### Multi-tenant Isolation
- ✅ Middleware: añade tenant_id a cada request (from JWT)
- ✅ QuerySet filtering: `queryset.filter(tenant_id=request.user.tenant_id)`
- ✅ NUNCA query sin tenant_id filter
- ✅ Tests: Usuario Tenant A ≠ datos Tenant B

### API Security
- ✅ JWT auth en todos los endpoints (excepto /login/)
- ✅ CORS: solo dominio cliente permitido
- ✅ Rate limit: 100 req/min por usuario
- ✅ Input validation: backend (no confiar frontend)
- ✅ SQL injection prevention: ORM (Django)

### Database
- ✅ Secrets en .env (DB_PASSWORD, SECRET_KEY, JWT_SECRET)
- ✅ Passwords hasheados: bcrypt
- ✅ Audit log: cada cambio registrado
- ✅ Backups: automáticos Railway (daily)

### Logging
- ✅ Nunca loguear: tokens, passwords, datos sensibles
- ✅ Sí loguear: quién, qué, cuándo, resultado
- ✅ Formato: timestamp | level | module | message

---

## 10. DEPLOYMENT CHECKLIST

### Pre-deployment
- ✅ Todas las migraciones creadas
- ✅ Tests pasan (pytest coverage >80%)
- ✅ Lint passes (ruff check .)
- ✅ SPEC.md actualizado
- ✅ .env.example con todas las vars

### Deployment (Railway)
- ✅ Conectar GitHub repo
- ✅ Configurar env vars (SECRET_KEY, DB_URL, etc.)
- ✅ Railway auto-deploy on git push
- ✅ Migrations auto on deploy
- ✅ Logs: `railway logs`

### Post-deployment
- ✅ Test endpoints en producción
- ✅ Verificar audit logs
- ✅ Monitor Sentry para errores
- ✅ Backup database

### Env Vars Requeridas
```
DEBUG=False (producción)
SECRET_KEY=<random-256-chars>
DATABASE_URL=postgres://user:pass@host:5432/pulso
ALLOWED_HOSTS=pulso.railway.app,www.pulso.railway.app
JWT_SECRET=<random-256-chars>
JWT_EXPIRY=3600
SENTRY_DSN=https://...
R2_ACCESS_KEY=...
R2_SECRET_KEY=...
R2_BUCKET=pulso-screenshots
```

---

## RESUMEN

| Componente | Entidad | Endpoints |
|-----------|---------|-----------|
| Products | 1 tabla core | GET, POST, PATCH, DELETE, archive, import, export |
| Brands | lookup | GET, POST, PATCH, DELETE |
| Categories | lookup | GET, POST, PATCH, DELETE |
| Channels | lookup | GET, POST, PATCH, DELETE |
| Sellers | lookup | GET, POST, PATCH, DELETE |
| Auth | - | POST /login, /refresh |
| Total | - | ~35 endpoints |

**Estimated LOC:** ~2000 líneas (models + serializers + views + tests)
**Estimated Time:** 40-44 horas (1 dev, 1 week @ 8h/day)
