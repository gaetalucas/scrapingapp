# PULSO — Plataforma de Inteligencia de Precios (SaaS)
## Contexto Completo para Desarrollo Fase 1

---

## 1. VISIÓN & OBJETIVO ESTRATÉGICO

**Pulso** es una plataforma SaaS de inteligencia de precios diseñada para que marcas (ej: Samsung Argentina) gobiernen su red de distribuidores verificando MAP (Minimum Advertised Price) compliance en tiempo real y a escala.

### Problema a Resolver
- Marcas no saben si sus distribuidores cumplen el PVP sugerido
- Violaciones se detectan DESPUÉS (días/semanas)
- Decisiones sobre relaciones distribuidor-marca se toman por intuición, no datos
- Tiempo de reacción: de días a horas

### Solución
Plataforma que automatiza scraping de precios en múltiples canales, analiza desvíos y proporciona tres vistas estratégicas:

1. **Panel de Control** — Agente reacciona EN HORAS
2. **Timeline + Scoring** — Gerente decide sobre relaciones
3. **Evidencia** — Director comercial prepara conversaciones

---

## 2. USUARIOS & CASOS DE USO

### Usuario 1: Agente de Cuenta (Operativo, 0-3 minutos)
- **Objetivo:** Reaccionar ante violaciones de precios HOY
- **Herramienta:** Panel de Control (Tablero)
- **Ejemplo:** "Garbarino está -8% en VTEX hace 4 días → Contactar ahora"
- **Decisión:** ¿Enviar aviso? ¿Escalar a comercial?

### Usuario 2: Gerente de Canal (Estratégico, 10-30 minutos)
- **Objetivo:** Tomar decisiones sobre relaciones distribuidor
- **Herramienta:** Scoring + Timeline
- **Ejemplo:** "Garbarino tiene reincidencia cada ~10 días → Política deliberada, no error"
- **Decisión:** ¿Mejores condiciones? ¿Conversación formal? ¿Cambiar distribuidor?

### Usuario 3: Director Comercial (Ejecutivo, 30-60 minutos)
- **Objetivo:** Preparar conversaciones con distribuidores con datos objetivos
- **Herramienta:** Timeline + evidencia (screenshots)
- **Ejemplo:** "Garbarino: 34 días en incumplimiento en 90 días, desvío promedio 8.3%, patrón recurrente cada ~10 días"
- **Decisión:** Argumentación objetiva para conversación

---

## 3. TODO LO TRABAJADO (Mockup v7.4)

### Mockup Actual: 7 Módulos Diseñados

#### **MÓDULO 1: PRODUCTOS** (Crear/Cargar)
- Tabla: Producto | Marca | Modelo | Categoría | SKU | PVP Full | PVP Promo
- Pestañas: Activos | Archivados (con indicador visual activo)
- Acciones: ✏️ Editar precio (modal rápido), ⏸ Pausar, 📦 Archivar
- Modal Nuevo: Campos (Nombre, Marca dropdown, Modelo, SKU, Categoría, PVP Full, PVP Promo)

#### **MÓDULO 2: ACTUALIZACIÓN DE PRECIOS**
- Botones: Exportar (template Excel) | Importar (con preview + validación)
- Búsqueda por SKU en historial
- Historial: Fecha | Archivo | Usuario | Estado | Filas importadas

#### **MÓDULO 3: ATRIBUTOS**
- **Categorías y Marcas** (pestaña dual):
  - Categorías: Smartphones, Televisores, Audio, Electrohogar, Accesorios, Smart Home
  - Marcas: Samsung, LG, Sony, Philips, Bose
- **Sellers:** Nombre + URL
- **Puertas de Venta:** Mercado Libre, Tienda Nube, VTEX, Tienda propia, Banco Provincia

#### **MÓDULO 4: SEGUIMIENTO**
- Tabla completa: Producto (Marca | Modelo | Categoría | SKU | PVP Full | PVP Promo) + Seller + Canal + 🔔 Alertas
- Sin columna Intervalo (simplificación)
- Acción: Configurar alertas per seguimiento

#### **MÓDULO 5: TABLERO (Panel de Control)** ⭐ Más importante
- **Banner Crítico** (rojo, 0-3 seg): Violación + botones acción (CONTACTAR AHORA, Ver Timeline, Escalar)
- **KPIs** (3-10 seg): Cumplimiento%, Violaciones críticas, Sellers en desvío, Racha máxima
- **Tabla Sellers en Desvío** (10-60 seg): Desvío% | Tiempo | Reincidencia | Vel. Corrección | Recomendación | Botón CONTACTAR
- **Modal Contactar:** Contexto pre-llenado + Canales (Email, WhatsApp, Teléfono, Comercial) + Nota + "Marcar contactado"
- **SKUs Críticos:** Qué producto está más afectado
- **Métricas Operativas:** Re-incidentes, Scraping OK, Fallas, Correcciones

#### **MÓDULO 6: SCORING** ⭐ Estratégico
- **Visión:** "¿En quién puedo confiar?" — Patrón de comportamiento sostenido
- **4 Dimensiones:**
  1. **TC (Tasa Cumplimiento):** % días en cumplimiento (0-100%)
  2. **VC (Velocidad Corrección):** Promedio días para corregir (rápido/normal/lento)
  3. **ID (Intensidad Desvíos):** % promedio desvío cuando viola (mínima/moderada/severa)
  4. **RI (Reincidencia):** % episodios que reincidieron en 30d (baja/media/alta)
- **Clasificación:** CONFIABLE (verde) | OCASIONAL (amarillo) | REINCIDENTE (rojo)
- **Período seleccionable:** 30 / 90 / 180 días
- **Sellers ordenados por TC (mayor a menor)**

#### **MÓDULO 7: TIMELINE** ⭐ Analítico
- **Visión:** "¿Cómo llegamos hasta acá?" — Evolución histórica
- **Selector:** Seller + Período
- **Gráfico SVG:** Línea azul (PVP aceptable) vs Línea roja (precio capturado)
- **Métricas:** Días en incumplimiento | Desvío promedio | Desvío máximo | Patrón detectado
- **Tabla de Episodios:** Cada incumplimiento con período, duración, desvío prom, desvío máx
- **Casos de uso:**
  - Frávega: Errores aislados, muy confiable
  - Garbarino: Patrón recurrente cada ~10 días, política deliberada
  - Musimundo: Incumplimiento estructural permanente, riesgo permanente

#### **MÓDULO 8: CONFIGURACIÓN** (Intacto)
- Usuarios (CRUD + Editar)
- Datos de Cuenta
- Plan & Upgrade
- Mi Perfil

---

## 4. ARQUITECTURA & STACK FINAL

```
┌────────────────────────────────────────────────┐
│            CLIENTE (Web Browser)               │
│   Django Templates + HTMX + Tailwind CSS      │
│   - Módulos: Crear/Cargar, Monitoreo, Config  │
│   - Actualizaciones sin full reload            │
└────────────────┬─────────────────────────────┘
                 │ HTTPS
┌────────────────▼─────────────────────────────┐
│         API GATEWAY (Railway)                 │
│   - Rate limit, CORS, JWT auth               │
└────────────────┬─────────────────────────────┘
                 │
┌────────────────▼──────────────────────────────┐
│    BACKEND (Python + Django + DRF)            │
│   - Views, Serializers, Permissions          │
│   - Multi-tenant middleware                   │
│   - Audit logging                             │
└────────────────┬──────────────────────────────┘
                 │
    ┌────────────┼────────────┬────────────┐
    │            │            │            │
┌───▼──┐    ┌───▼─┐      ┌──▼────┐   ┌──▼────┐
│Celery│    │Redis│      │ Logs  │   │Secrets│
│Tasks │    │Cache│      │Stack  │   │ Env   │
└───┬──┘    └─────┘      └───────┘   └───────┘
    │
┌───▼─────────────────────────────────┐
│  SCRAPING (Celery Beat + Workers)   │
│  - Playwright (JS-heavy)            │
│  - httpx (static)                   │
│  - Retry + Circuit breaker          │
└───┬─────────────────────────────────┘
    │
┌───▼──────────────────────────────────┐
│  DATABASE (PostgreSQL → TimescaleDB) │
│  - RLS para multi-tenant             │
│  - Indexes: tenant_id, seller_id    │
└───┬──────────────────────────────────┘
    │
┌───▼─────────────────────────────────┐
│  STORAGE (Cloudflare R2 / B2)       │
│  - Screenshots de evidencia         │
│  - HTML snapshots                   │
└──────────────────────────────────────┘

DEPLOYMENT: Railway (git push → auto deploy)
MONITORING: Sentry + Railway logs
CI/CD: GitHub Actions (ruff + pytest)
```

---

## 5. MODELO DE DATOS CORE (Para Fase 1)

### Entidades Principales
```
TENANT (Samsung Argentina)
├── id (UUID)
├── name
└── created_at

PRODUCT
├── id (UUID)
├── tenant_id (FK → TENANT)
├── name (Galaxy S24 128GB)
├── brand_id (FK → BRAND)
├── model (S24)
├── category_id (FK → CATEGORY)
├── sku (SM-S24)
├── pvp_full (1199000)
├── pvp_promo (1099000 or NULL)
├── status (active / paused / archived)
├── created_at, updated_at, updated_by (audit)

BRAND
├── id
├── tenant_id
├── name (Samsung, LG, Sony, etc.)

CATEGORY
├── id
├── tenant_id
├── name (Smartphones, Televisores, etc.)

SELLER
├── id
├── tenant_id
├── name (Frávega, Garbarino, Musimundo)
├── url (https://...)

CHANNEL / PUERTA
├── id
├── tenant_id
├── name (Mercado Libre, VTEX, etc.)

SEGUIMIENTO (Para Fase 2)
├── id
├── tenant_id
├── product_id (FK)
├── seller_id (FK)
├── channel_id (FK)
├── url
├── interval (8h, 12h, 16h, 24h)

CAPTURA (Para Fase 2 — Time Series)
├── id
├── seguimiento_id (FK)
├── price_captured (1050000)
├── is_promo (boolean)
├── deviation_pct (-12.5)
├── screenshot_url
├── timestamp
```

---

## 6. PALETA DE COLORES & DISEÑO

### Semáforo de Decisión
```
🔴 CRÍTICO (Acción hoy):     #ef4444 (rojo puro)
🟡 MODERADO (Aviso):        #f59e0b (amarillo)
🟢 LEVE (Monitorear):       #10b981 (verde)
🔵 CONTACTADO (En revisión): #3b82f6 (azul)
✓  RESUELTO (Hecho):        #86efac (verde claro)
```

### UX/UI Principles
- **Jerarquía:** Crítico → Secundario → Fondo
- **Affordances:** Botones obvios (→ CONTACTAR)
- **Feedback:** Hover, loading, toast notifications
- **Responsive:** Mobile-first (320px → desktop)
- **Accesibilidad:** WCAG 2.1 AA (contraste ≥7:1)

---

## 7. SEGURIDAD CORE (CRÍTICO)

### Multi-tenant Isolation
- Cada query filtra por `tenant_id` (NUNCA default)
- Row-Level Security (RLS) en PostgreSQL
- Test: Usuario Tenant A ≠ datos Tenant B

### API Security
- JWT con refresh tokens (no localStorage puro)
- CORS estricto (solo dominio cliente)
- Rate limiting por endpoint
- Input validation en backend (nunca confiar frontend)

### Database
- Secrets en `.env` (nunca git)
- Passwords hasheados (bcrypt)
- Audit log: quién, qué, cuándo
- Backups automáticos (Railway)

---

## 8. FLUJOS DE USUARIO (Ejemplos Reales)

### Flujo 1: Agente de Cuenta — Reacción Rápida (3 min)
```
1. Entra a Panel de Control
2. Lee banner rojo: "Garbarino -8% hace 4 días en VTEX"
3. Ve KPI: "1 violación crítica"
4. Clickea "→ CONTACTAR AHORA"
5. Modal pre-llenado con contexto
6. Elige "Email" + nota "Corrige en 24h"
7. "Marcar contactado" → Toast ✓ → Status actualiza
8. Vuelve a Panel → ve status "Contactado hoy 14:32"
```

### Flujo 2: Gerente de Canal — Decisión Estratégica (20 min)
```
1. Entra a Scoring
2. Selecciona período "90 días"
3. Ve: Frávega (CONFIABLE), Garbarino (OCASIONAL), Musimundo (REINCIDENTE)
4. Clickea Garbarino → Ve dimensiones:
   - TC: 76% (Bueno)
   - VC: 2.5d (Reactivo, no proactivo)
   - ID: 8.3% (Moderada)
   - RI: 35% (Media)
5. Decisión: "Conversación formal, alertas automáticas"
```

### Flujo 3: Director Comercial — Preparar Conversación (45 min)
```
1. Entra a Timeline
2. Selecciona Garbarino + 90 días
3. Ve gráfico: línea roja oscila abajo de azul (incumplimiento)
4. Métricas: "37 días en incumplimiento | 6.4% desvío prom | Patrón recurrente cada ~10 días"
5. Tabla: Episodios con período, duración, desvío
6. Genera evidencia: "Garbarino: violación sistemática, no puntual"
7. Prepara conversación: "Hace 90 días, 37 de esos días estuviste -8% en promedio..."
```

---

## 9. FASES DE DESARROLLO

### FASE 1: Generación de Datos (Próxima — lo que codificaremos)
- ✅ CRUD Productos (Crear, Actualizar, Archivar)
- ✅ Import/Export Excel
- ✅ CRUD Sellers, Categorías, Marcas, Puertas
- ✅ Multi-tenant isolation
- ✅ Audit logging

**Entregable:** Backend API + Frontend Crear/Cargar listos

### FASE 2: Monitoreo (Después)
- Scraping: Playwright + httpx + Celery
- Tabla Seguimiento (vincula Producto × Seller × Canal)
- Capturas time-series (PostgreSQL → TimescaleDB)
- Tablero en vivo (KPIs actualizados)

### FASE 3: Análisis (Después)
- Scoring: 4 dimensiones de confiabilidad
- Timeline: gráfico evolución precio vs PVP
- Alertas automáticas

### FASE 4+: Expansión
- Reportes automáticos (Excel/PDF)
- API pública + webhooks
- Multi-brand simultaneo

---

## 10. DATOS FICTICIOS (Para Demo)

### Tenant: Samsung Argentina

**Productos:**
- Galaxy S24 128GB | Samsung | S24 | Smartphones | SM-S24 | $1.199.000 | (vacío)
- Neo QLED 55" | Samsung | QN55 | Televisores | QN55 | $1.450.000 | $1.350.000
- Soundbar HW-Q800 | Samsung | HW-Q800 | Audio | HWQ | $520.000 | (vacío)
- Galaxy A15 | Samsung | A15 | Smartphones | SM-A15 | $450.000 | $400.000 (archivado)

**Sellers:**
- Frávega (https://www.fravega.com)
- Garbarino (https://www.garbarino.com)
- Musimundo (https://www.musimundo.com)

**Categorías:**
- Smartphones, Televisores, Audio, Electrohogar, Accesorios, Smart Home

**Marcas:**
- Samsung, LG, Sony, Philips, Bose

**Canales/Puertas:**
- Mercado Libre, Tienda Nube, VTEX, Tienda propia, Banco Provincia

---

## 11. SKILLS NECESARIOS PARA CODIFICAR

### Frontend Design
- Componentes reutilizables
- Design tokens (colores, espacios)
- Responsive patterns

### Docx
- Generar SPEC.md
- Generar CLAUDE.md

---

## 12. COMANDOS ÚTILES (Para después)

```bash
# Crear repo
git clone <repo> && cd pulso

# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Dev server
python manage.py runserver

# Migrations
python manage.py makemigrations
python manage.py migrate

# Tests
pytest -v

# Lint
ruff check .

# Shell
python manage.py shell
python manage.py dbshell
```

---

## RESUMEN EJECUTIVO PARA CLAUDE CODE

| Componente | Tech | Fase 1 |
|-----------|------|--------|
| DB Schema | PostgreSQL | 4h |
| Backend API | Django + DRF | 16h |
| Frontend CRUD | Django Tmpl + HTMX | 8h |
| Import/Export | openpyxl | 6h |
| Tests | pytest | 8h |
| Deploy | Railway | 2h |
| **TOTAL** | | **44h** |

**Equipo:** 1 dev (1 semana @ 8h/día) o 2 devs paralelos (3-4 días)

---

**Próximo paso:** Copiar los archivos SPEC.md, CLAUDE.md, PROMPTS_CLAUDE_CODE.md a Claude Code y comenzar Sesión 1.
