# 📋 INDEX — PULSO FASE 1 READY FOR CLAUDE CODE

**Status:** ✅ Listo para codificar en Claude Code

**Última actualización:** 2026-07-11

---

## 📁 ARCHIVOS GENERADOS

| Archivo | Tipo | Propósito | Lecturas |
|---------|------|----------|----------|
| **DESCRIPCIÓN_PROYECTO.md** | 📖 Contexto | TODO lo que trabajamos + proyecto completo | 1x antes de empezar |
| **SPEC.md** | 📋 Técnico | Especificación detallada (DB, API, endpoints, validación) | Consultar durante dev |
| **CLAUDE.md** | 🛠️ Práctico | Guía paso a paso (setup, debugging, deployment) | Siempre a mano |
| **PROMPTS_CLAUDE_CODE.md** | 🤖 Ejecución | 4 prompts listos para copiar/pegar en Claude Code | Sesión 1, 2, 3, 4 |
| **Este archivo** | 🗺️ Mapa | Te estás leyendo ahora |  |

---

## 🚀 QUICK START (5 minutos)

### 1. LEE ESTO PRIMERO
```
DESCRIPCIÓN_PROYECTO.md — Secciones clave:
  § 1. VISIÓN & OBJETIVO
  § 2. USUARIOS & CASOS DE USO
  § 3. TODO LO TRABAJADO (Mockup v7.4 completo)
  § 10. DATOS FICTICIOS
  
Tiempo: 5-10 minutos
```

### 2. ENTIENDE LA ARQUITECTURA
```
DESCRIPCIÓN_PROYECTO.md — Secciones:
  § 4. ARQUITECTURA & STACK
  § 5. MODELO DE DATOS CORE
  § 8. FLUJOS DE USUARIO (Ejemplos reales)
  
Tiempo: 5-10 minutos
```

### 3. PREPÁRATE PARA CODIFICAR
```
CLAUDE.md — Secciones:
  § 1. SETUP INICIAL (5 min)
  § 2. CONFIGURACIÓN DJANGO
  § 3. WORKFLOW DEV
  
Tiempo: 10 minutos (Lee, no ejecutes aún)
```

### 4. ABRE CLAUDE CODE
```
PROMPTS_CLAUDE_CODE.md → Sesión 1

En Claude Code:
  1. Copia TODO el prompt Sesión 1 (desde # SESIÓN 1 hasta --- END ---)
  2. Pega en Claude Code
  3. Envía
  4. Espera a que complete (~10 min)
  
Resultado: DB schema + Django setup completo
```

### 5. REPITE PARA SESIONES 2, 3, 4
```
Sesión 2: API REST (serializers, views, endpoints)
Sesión 3: Frontend (HTML + HTMX templates)
Sesión 4: Tests + Deploy config

Cada sesión: ~15-30 minutos en Claude Code
Total: ~2 horas para Fase 1 completo
```

---

## 📚 LECTURA RECOMENDADA ANTES DE EMPEZAR

### Mínimo (30 minutos):
1. **DESCRIPCIÓN_PROYECTO.md** — Secciones 1, 2, 3, 10
2. **CLAUDE.md** — Secciones 1, 3, 4

### Ideal (1 hora):
1. **DESCRIPCIÓN_PROYECTO.md** — Todas las secciones
2. **CLAUDE.md** — Todas las secciones
3. Rápida ojeada a **SPEC.md** — Para entender estructura API

### Experto (2 horas):
1. Todo arriba
2. **SPEC.md** — Completo
3. Revisar **PROMPTS_CLAUDE_CODE.md** — Sesiones 1 y 2

---

## 🤖 WORKFLOW CLAUDE CODE (4 Sesiones)

### SESIÓN 1: Database + Django Models (40-50 min)
**Archivo:** PROMPTS_CLAUDE_CODE.md → Sesión 1

**Qué genera:**
- ✅ manage.py + settings.py completo
- ✅ Models para: Tenants, Users, Products, Brands, Categories, Channels, Sellers
- ✅ Modelo de datos SQL (con índices, unique constraints, RLS)
- ✅ Initial migrations
- ✅ Fixtures de demo (Samsung Argentina + 3 usuarios + datos iniciales)

**Checklist después:**
- ✅ `python manage.py migrate` ejecuta sin errores
- ✅ `python manage.py shell` abre Django shell
- ✅ Base de datos tiene 8 tablas (tenants, auth_user, products, etc.)

**Referencia:** SPEC.md § 2 (Modelo de Datos)

---

### SESIÓN 2: API REST Endpoints (60-80 min)
**Archivo:** PROMPTS_CLAUDE_CODE.md → Sesión 2

**Qué genera:**
- ✅ Serializers para todos los modelos (con validación)
- ✅ ViewSets (list, create, retrieve, update, delete)
- ✅ Custom actions (/archive/, /import/, /export/)
- ✅ Auth endpoints (/login/, /refresh/)
- ✅ Middleware + Permissions para multi-tenant
- ✅ URLs routing completo (/api/v1/...)

**Endpoints resultado:**
```
GET    /api/v1/products/                    → list
POST   /api/v1/products/                    → create
GET    /api/v1/products/{id}/               → retrieve
PATCH  /api/v1/products/{id}/               → update
DELETE /api/v1/products/{id}/               → delete
POST   /api/v1/products/{id}/archive/       → archive
POST   /api/v1/products/import/             → import preview
POST   /api/v1/products/import/confirm/     → confirm import
GET    /api/v1/products/export/             → download Excel

... (idem para sellers, brands, categories, channels)

POST   /api/v1/auth/login/
POST   /api/v1/auth/refresh/
```

**Checklist después:**
- ✅ `python manage.py runserver` inicia servidor
- ✅ Acceder http://localhost:8000/api/v1/products/ → retorna JSON
- ✅ POST /login/ devuelve JWT token

**Referencia:** SPEC.md § 3 (API Endpoints)

---

### SESIÓN 3: Frontend HTML + HTMX (60-80 min)
**Archivo:** PROMPTS_CLAUDE_CODE.md → Sesión 3

**Qué genera:**
- ✅ base.html (layout + navbar + sidebar)
- ✅ Módulo Productos: list.html + modales (nuevo, edit precio, import)
- ✅ Módulo Sellers/Categorías/Canales: CRUD templates
- ✅ Módulo Seguimiento: tabla completa
- ✅ HTMX integrations (crear, editar, archivar sin reload)
- ✅ Tailwind CSS styling (responsive, design system)
- ✅ Formularios con validación frontend

**Resultado visual:**
- Navbar con logo + usuario
- Sidebar con módulos clickeables
- Tablas interactivas con HTMX
- Modales para crear/editar
- Toast notifications (verde ✓, rojo ✗)

**Checklist después:**
- ✅ Acceder http://localhost:8000/ → ve página bonita
- ✅ Click "Nuevo producto" → modal abre
- ✅ Llenar datos + "Guardar" → API call + tabla actualiza sin reload

**Referencia:** DESCRIPCIÓN_PROYECTO.md § 3 (Todo lo trabajado)

---

### SESIÓN 4: Tests + Deployment (60-90 min)
**Archivo:** PROMPTS_CLAUDE_CODE.md → Sesión 4

**Qué genera:**
- ✅ conftest.py con fixtures reutilizables
- ✅ test_models.py (validaciones)
- ✅ test_serializers.py (DRF serialization)
- ✅ test_products_api.py (endpoints + multi-tenant isolation)
- ✅ test_sellers_api.py, test_auth_api.py (idem)
- ✅ pytest.ini configurado
- ✅ GitHub Actions CI/CD (.github/workflows/test.yml)
- ✅ Procfile para Railway (auto migrate + web server)
- ✅ Dockerfile opcional
- ✅ .gitignore + README.md

**Cobertura resultado:**
- >80% de cobertura (models, serializers, API endpoints)
- Todos los tests pasan
- Multi-tenant isolation verificado

**Checklist después:**
- ✅ `pytest` — 50+ tests pasan
- ✅ `pytest --cov=apps` — coverage >80%
- ✅ `ruff check .` — no linting errors
- ✅ `git push origin main` → Railway auto-deploya

**Referencia:** CLAUDE.md § 6 (Testing Pattern)

---

## ⚙️ DESPUÉS DE CLAUDE CODE

### 1. Setup Local (15 min)
```bash
# Crear virtual env
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar deps
pip install -r requirements.txt

# Copiar .env
cp .env.example .env

# Migraciones
python manage.py migrate

# Super usuario (admin)
python manage.py createsuperuser

# Datos iniciales
python manage.py loaddata fixtures/initial_data.json

# Dev server
python manage.py runserver
# Acceder http://localhost:8000
```

### 2. Verificar Todo Funciona (10 min)
```bash
# Tests
pytest -v

# API test (desde otra terminal)
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@samsung.com", "password": "admin123"}'

# Debería retornar JWT token
```

### 3. Limpiar Código (5 min)
```bash
ruff check . --fix
```

### 4. Preparar Deploy (5 min)
```bash
# Crear .env producción con:
DEBUG=False
SECRET_KEY=<generate random>
DATABASE_URL=<Railway PostgreSQL>
# Ver CLAUDE.md § 9 para detalles

# Push a GitHub
git add .
git commit -m "feat: fase 1 completo"
git push origin main

# Railway auto-deploya
# Ver logs: railway logs
```

---

## 📖 GUÍAS DE REFERENCIA RÁPIDA

### Necesitas entender...

| Pregunta | Referencia |
|----------|-----------|
| ¿Cuál es la visión del proyecto? | DESCRIPCIÓN § 1 |
| ¿Quiénes son los usuarios? | DESCRIPCIÓN § 2 |
| ¿Cómo es el mockup? | DESCRIPCIÓN § 3 |
| ¿Cuáles son los datos ficticios? | DESCRIPCIÓN § 10 |
| ¿Cómo es el schema DB? | SPEC § 2 |
| ¿Cuáles son los endpoints? | SPEC § 3 |
| ¿Cómo configurar Django? | CLAUDE § 2 |
| ¿Cómo hacer debugging? | CLAUDE § 6 |
| ¿Cómo escribir tests? | CLAUDE § 7 |
| ¿Cómo deployar a Railway? | CLAUDE § 9 |
| ¿Cuál es el workflow dev día a día? | CLAUDE § 3 |
| ¿Cómo funciona multi-tenant? | CLAUDE § 4 |

---

## 🔑 KEY CONCEPTS

### Multi-tenant (CRÍTICO)
- Samsung Argentina es un "tenant"
- Cada tabla tiene `tenant_id` (FK)
- NUNCA queryear sin filtrar por tenant_id
- Tests verifican isolation (User A ≠ datos User B)

**Referencia:** CLAUDE.md § 4

### JWT Auth
- Login genera JWT token
- Token en header Authorization: `Bearer <token>`
- Token expira en 1 hora
- Refresh token renueva access token

**Referencia:** SPEC.md § 3.6 (AUTH Endpoints)

### DRF Serializers
- Validan input (required, unique, format)
- Retornan JSON estructurado
- Método `validate()` para validaciones cross-field

**Referencia:** SPEC.md § 5 (Validation Rules)

### HTMX
- Soporta GET, POST, PATCH, DELETE sin reload
- `hx-post`, `hx-get`, `hx-swap`, `hx-target`
- Debounce para búsquedas
- hx-confirm para confirmaciones

**Referencia:** CLAUDE.md § 8 (HTMX Integration)

---

## 🎯 GOALS FASE 1

✅ **Objetivo primario:** Backend API + Frontend CRUD funcional

| Módulo | Status | LOC Aprox |
|--------|--------|-----------|
| Models + Migrations | ✅ | 300 |
| Serializers | ✅ | 250 |
| ViewSets + URLs | ✅ | 400 |
| Frontend HTML | ✅ | 800 |
| Tests | ✅ | 600 |
| Config (settings, deploy) | ✅ | 200 |
| **TOTAL** | **✅** | **2500-2700** |

**Effort:** 1 developer, 1 week @ 8h/day (con Claude Code: ~2 horas para generar, 5 horas para revisar/iterar)

---

## 📞 TROUBLESHOOTING

### "ModuleNotFoundError: No module named 'apps'"
```
→ CLAUDE.md § 11 Troubleshooting
→ Solución: export PYTHONPATH
```

### "ProgrammingError: relation 'products_product' does not exist"
```
→ Ejecutar: python manage.py migrate
```

### "Tenant A ve datos de Tenant B"
```
→ ¡CRÍTICO! Revisar get_queryset() en views
→ Debe filtrar: .filter(tenant_id=request.user.tenant_id)
→ Ver: CLAUDE.md § 4
```

### Tests fallan con "IntegrityError"
```
→ CLAUDE.md § 11
→ Usar @pytest.mark.django_db en fixtures
```

---

## ✨ SIGUIENTE PASO

### 👉 **ABRE CLAUDE CODE AHORA**

1. Copia PROMPTS_CLAUDE_CODE.md → Sesión 1
2. Pega en Claude Code
3. Espera a que complete
4. Repite para Sesión 2, 3, 4
5. ¡Listo!

---

## 📝 NOTAS FINALES

- **No necesitas memorizar todo** — Los archivos están para consultar
- **Sigue el orden:** Descripción → Spec → Claude → Prompts
- **Claude Code hace el trabajo sucio** — Tú revisas y iteras
- **Git es tu amigo** — Commit después de cada sesión
- **Pytest + Ruff te protegen** — Coverage + linting antes de prod
- **Railway es simple** — Push = Deploy automático

---

**¡Muchos éxitos con Pulso! 🚀**

---

**Última actualización:** 2026-07-11 • **Status:** ✅ Ready for Claude Code • **Fase:** 1 de 4
