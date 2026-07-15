# 🗺️ PULSO — Roadmap Fase 2, 3 y 4

**Visión completa del proyecto más allá de Fase 1**

---

## FASE 2: MONITOREO & SCRAPING (Siguiente)

### Objetivo

Automatizar scraping de precios en múltiples canales y detectar desvíos en tiempo real.

### Componentes a Construir

#### 2.1 Scraper (Playwright + httpx)

**Responsabilidad:** Extraer precios de sitios web de distribuidores

```python
# Pseudocódigo
class ProductScraper:
    - scrape_mercado_libre(product, seller)
    - scrape_tienda_nube(product, seller)
    - scrape_vtex(product, seller)
    - validate_price(price)
    - save_capture(product, price, screenshot)
```

**Stacks a soportar:**
- Mercado Libre (JS-heavy → Playwright)
- Tienda Nube (JS-heavy → Playwright)
- VTEX (Static + JS → httpx + Playwright)
- Tienda propia (Static → httpx)
- Plataformas customizadas

**Entrada en requirements.txt:**
```
playwright==1.40.0
httpx==0.25.0
beautifulsoup4==4.12.0
lxml==4.9.0
```

#### 2.2 Scheduler (Celery + Redis)

**Responsabilidad:** Ejecutar scraping según intervalos

```python
# apps/scraper/tasks.py
@shared_task
def scrape_all_seguimientos():
    """Scrape todos los seguimientos cada 8h"""
    seguimientos = Seguimiento.objects.filter(status='active')
    for seg in seguimientos:
        scrape_seguimiento.delay(seg.id)

@shared_task
def scrape_seguimiento(seguimiento_id):
    """Scrape un seguimiento específico"""
    seg = Seguimiento.objects.get(id=seguimiento_id)
    price = scraper.scrape(seg.product, seg.seller, seg.channel)
    Captura.objects.create(
        seguimiento=seg,
        price_captured=price,
        screenshot_url=...,
        timestamp=now()
    )
```

**Configuración en settings.py:**
```python
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'

CELERY_BEAT_SCHEDULE = {
    'scrape-every-8-hours': {
        'task': 'apps.scraper.tasks.scrape_all_seguimientos',
        'schedule': crontab(minute=0, hour='*/8'),
    },
}
```

**Entrada en requirements.txt:**
```
celery==5.3.4
celery-beat==2.5.0
redis==5.0.0
```

#### 2.3 Tabla Captura (Time-Series)

**Modelo:**
```python
class Captura(models.Model):
    seguimiento = ForeignKey(Seguimiento)
    price_captured = BigIntegerField()
    is_promo = BooleanField()
    deviation_pct = DecimalField()  # -12.5 = 12.5% abajo
    screenshot_url = URLField()
    timestamp = DateTimeField(db_index=True)
```

**Índices:**
```python
class Meta:
    indexes = [
        models.Index(fields=['seguimiento', '-timestamp']),
    ]
```

#### 2.4 Alertas Básicas

**Modelo:**
```python
class AlertRule(models.Model):
    tenant = ForeignKey(Tenant)
    seguimiento = ForeignKey(Seguimiento)
    trigger_on = CharField(choices=[
        ('above_pvp', 'Arriba del PVP'),
        ('below_pvp', 'Abajo del PVP'),
        ('any_deviation', 'Cualquier desvío'),
    ])
    deviation_threshold = DecimalField()  # %
    notify_via = CharField(choices=[
        ('email', 'Email'),
        ('webhook', 'Webhook'),
        ('dashboard', 'Dashboard'),
    ])
```

#### 2.5 Panel de Control (Tablero)

**Vista en tiempo real:**
- KPIs: Cumplimiento %, Violaciones activas, Tiempo promedio corrección
- Tabla: Sellers en desvío (hoy)
- Gráfico: Tendencia de cumplimiento (últimos 30 días)
- Alertas: Feed de eventos

**Endpoint:**
```python
GET /api/v1/dashboard/
Response:
{
    "metrics": {
        "compliance_pct": 85.2,
        "active_deviations": 3,
        "avg_correction_time_hours": 12.5,
    },
    "sellers_at_risk": [...],
    "recent_alerts": [...],
}
```

### Checklist Fase 2

- [ ] Scraper (Playwright + httpx) funcional
- [ ] 5+ sitios soportados (Mercado Libre, VTEX, etc.)
- [ ] Celery + Redis configurado
- [ ] Modelo Captura + migraciones
- [ ] Scheduler ejecutando cada 8 horas
- [ ] AlertRule CRUD
- [ ] Panel de Control endpoint
- [ ] Tests para scraper (mock Playwright)
- [ ] Tests para Celery tasks
- [ ] Documentación de cómo agregar sitios nuevos
- [ ] Deploy a Railway (con Redis)

### Tiempo Estimado

**40-50 horas** (1 dev, 1 semana @ 8h/día)

---

## FASE 3: ANÁLISIS & ALERTAS

### Objetivo

Análisis histórico y alertas inteligentes.

### Componentes a Construir

#### 3.1 Scoring (4 Dimensiones)

**Modelo:**
```python
class Scoring(models.Model):
    tenant = ForeignKey(Tenant)
    seller = ForeignKey(Seller)
    period_days = IntegerField()  # 30, 90, 180
    
    # 4 dimensiones
    compliance_rate = DecimalField()      # TC: % días cumpliendo
    correction_speed = DecimalField()     # VC: promedio días para corregir
    deviation_intensity = DecimalField()  # ID: % promedio cuando viola
    recurrence = DecimalField()            # RI: % reincidencia en 30d
    
    # Clasificación
    badge = CharField(choices=[
        ('confiable', 'CONFIABLE'),
        ('ocasional', 'OCASIONAL'),
        ('reincidente', 'REINCIDENTE'),
    ])
```

**Cálculo:**
```python
def calculate_scoring(seller, period_days=90):
    capturas = Captura.objects.filter(
        seguimiento__seller=seller,
        timestamp__gte=now() - timedelta(days=period_days)
    )
    
    # TC: (días cumpliendo / días totales) * 100
    compliance_days = capturas.filter(deviation_pct__gte=0).count()
    tc = (compliance_days / capturas.count()) * 100
    
    # VC: promedio días entre incumplimiento y corrección
    vc = calculate_avg_correction_time(capturas)
    
    # ID: promedio % desvío en días de incumplimiento
    id = capturas.filter(deviation_pct__lt=0).aggregate(
        Avg('deviation_pct')
    )['deviation_pct__avg']
    
    # RI: % episodios que reincidieron en 30d
    ri = calculate_recurrence_rate(seller, capturas)
    
    return Scoring(
        compliance_rate=tc,
        correction_speed=vc,
        deviation_intensity=id,
        recurrence=ri,
        badge=get_badge(tc, ri),
    )
```

**Endpoint:**
```python
GET /api/v1/scoring/?period=90&seller_id=xxx
Response:
{
    "seller": "Garbarino",
    "period": "90 días",
    "dimensions": {
        "compliance_rate": 76,          # TC
        "correction_speed": 2.5,         # VC días
        "deviation_intensity": 8.3,      # ID %
        "recurrence": 35,                # RI %
    },
    "badge": "OCASIONAL",
}
```

#### 3.2 Timeline (Gráficos Históricos)

**Modelo:**
```python
class TimelineData(models.Model):
    seguimiento = ForeignKey(Seguimiento)
    date = DateField()
    pvp_price = BigIntegerField()        # PVP aceptable
    captured_price = BigIntegerField()   # Precio capturado
    is_compliant = BooleanField()
```

**Visualización:**
- Gráfico SVG: línea azul (PVP) vs roja (precio capturado)
- Período seleccionable: 30/90/180 días
- Métricas: días incumplimiento, desvío promedio, patrón
- Tabla: episodios de incumplimiento

**Endpoint:**
```python
GET /api/v1/timeline/?seller_id=xxx&period=90
Response:
{
    "chart_data": [
        {date: "2026-07-01", pvp: 1199000, captured: 1100000},
        ...
    ],
    "metrics": {
        "non_compliance_days": 37,
        "avg_deviation": 6.4,
        "max_deviation": 12.5,
        "pattern": "recurrent_every_10_days",
    },
    "episodes": [
        {start: "2026-07-01", end: "2026-07-04", duration_days: 4, avg_dev: 8.1},
        ...
    ],
}
```

#### 3.3 Alertas Avanzadas

**Tipos:**
```python
ALERT_TYPES = [
    ('new_deviation', 'Nueva violación'),
    ('extended_violation', 'Violación >3 días'),
    ('recurrence', 'Reincidencia detectada'),
    ('critical_seller', 'Seller en riesgo crítico'),
]

class Alert(models.Model):
    tenant = ForeignKey(Tenant)
    seguimiento = ForeignKey(Seguimiento)
    type = CharField(choices=ALERT_TYPES)
    severity = CharField(choices=[('critical', 'Crítica'), ('moderate', 'Moderada'), ('low', 'Baja')])
    triggered_at = DateTimeField()
    resolved_at = DateTimeField(null=True)
    context = JSONField()  # Datos del incidente
```

**Ejemplo de trigger:**
```python
def check_extended_violation(seguimiento):
    """Alerta si viola >3 días"""
    non_compliant = Captura.objects.filter(
        seguimiento=seguimiento,
        is_compliant=False,
        timestamp__gte=now() - timedelta(days=3)
    ).count()
    
    if non_compliant >= 3:
        Alert.objects.create(
            seguimiento=seguimiento,
            type='extended_violation',
            severity='critical',
            context={
                'days': non_compliant,
                'seller': seguimiento.seller.name,
                'deviation_avg': 8.5,
            }
        )
```

#### 3.4 Reportes

**Modelos:**
```python
class Report(models.Model):
    tenant = ForeignKey(Tenant)
    type = CharField(choices=[
        ('monthly_compliance', 'Compliance mensual'),
        ('seller_analysis', 'Análisis de seller'),
        ('category_performance', 'Performance por categoría'),
    ])
    generated_by = ForeignKey(User)
    generated_at = DateTimeField()
    file_url = URLField()  # PDF o Excel
```

**Formatos:**
- Excel con gráficos
- PDF para presentaciones
- JSON para dashboards

**Endpoint:**
```python
GET /api/v1/reports/monthly/?period=2026-07
POST /api/v1/reports/generate/?type=seller_analysis&seller_id=xxx
```

### Checklist Fase 3

- [ ] Modelo Scoring con 4 dimensiones
- [ ] Cálculo automático de scoring
- [ ] Endpoint /scoring/ funcional
- [ ] Modelo Timeline + historiales
- [ ] Gráficos (SVG o Chart.js)
- [ ] Endpoint /timeline/ funcional
- [ ] Alertas automáticas (Celery task)
- [ ] Modelo Alert + resolución
- [ ] Feed de alertas en Dashboard
- [ ] Reportes (Excel + PDF)
- [ ] Endpoint /reports/ funcional
- [ ] Tests para scoring, timeline, alertas
- [ ] Frontend: Scoring view + Timeline view
- [ ] Deploy a Railway

### Tiempo Estimado

**30-40 horas** (1 dev, 5 días @ 8h/día)

---

## FASE 4: EXPANSIÓN & API PÚBLICA

### Objetivo

Escalabilidad, integraciones externas y multi-brand.

### Componentes a Construir

#### 4.1 Multi-Brand

**Cambio en modelo:**
```python
class Product(models.Model):
    tenant = ForeignKey(Tenant)
    brand = ForeignKey(Brand)  # Ahora filtrada
    # ... resto igual ...

# Antes: 1 tenant (Samsung) podía monitorear productos de Samsung
# Ahora: 1 tenant puede monitorear productos de Samsung + LG + Sony simultáneamente
```

**Endpoint:**
```python
GET /api/v1/products/?brand=samsung,lg  # Múltiples marcas
GET /api/v1/dashboard/?brand=samsung    # Dashboard por marca
```

#### 4.2 Permisos Granulares

**Roles extendidos:**
```python
ROLES = [
    ('admin', 'Acceso total + gestión usuarios'),
    ('manager', 'Gestión sellers + alertas'),
    ('analyst', 'Lectura dashboard + reportes'),
    ('viewer', 'Lectura solo'),
    ('custom', 'Permisos personalizados'),
]

class Permission(models.Model):
    user = ForeignKey(User)
    resource = CharField(choices=[
        ('products', 'Productos'),
        ('sellers', 'Sellers'),
        ('scoring', 'Scoring'),
        ('timeline', 'Timeline'),
        ('alerts', 'Alertas'),
        ('reports', 'Reportes'),
    ])
    action = CharField(choices=['read', 'create', 'update', 'delete'])
```

#### 4.3 API Pública + Webhooks

**API Key authentication:**
```python
class APIKey(models.Model):
    tenant = ForeignKey(Tenant)
    key = CharField(unique=True)
    created_at = DateTimeField()
    last_used_at = DateTimeField()
    is_active = BooleanField()
```

**Uso:**
```bash
curl -H "Authorization: Bearer sk_live_xxx" https://api.pulso.app/v2/...
```

**Webhooks:**
```python
class Webhook(models.Model):
    tenant = ForeignKey(Tenant)
    url = URLField()
    events = JSONField()  # ['alert.created', 'compliance.changed']
    
    # Trigger automático
    @classmethod
    def trigger(cls, event, data):
        for webhook in cls.objects.filter(events__contains=event):
            post_to_webhook.delay(webhook.id, event, data)
```

**Eventos:**
```python
WEBHOOK_EVENTS = [
    'alert.created',
    'alert.resolved',
    'compliance.changed',
    'seller.at_risk',
    'report.generated',
]
```

#### 4.4 Integraciones

**Slack:**
```python
# Enviar alertas críticas a Slack
@task
def send_to_slack(alert_id):
    alert = Alert.objects.get(id=alert_id)
    message = f"🚨 {alert.type}: {alert.context['seller']} está -12% en VTEX"
    webhook_url = Tenant.objects.get(id=alert.tenant_id).slack_webhook
    requests.post(webhook_url, json={'text': message})
```

**Microsoft Teams:**
```python
# Similar a Slack
```

**Google Sheets:**
```python
# Exportar reportes automáticamente a Google Sheets
```

#### 4.5 Analytics & Usage

**Tracking:**
```python
class Usage(models.Model):
    tenant = ForeignKey(Tenant)
    date = DateField()
    api_calls = IntegerField()
    scrape_tasks = IntegerField()
    alerts_generated = IntegerField()
```

**Dashboard de billing:**
```python
GET /api/v1/usage/
GET /api/v1/billing/
```

### Checklist Fase 4

- [ ] Soporte multi-brand en modelos
- [ ] Permisos granulares (RBAC)
- [ ] APIKey authentication
- [ ] Webhook support
- [ ] Integraciones: Slack, Teams, Google Sheets
- [ ] Usage analytics
- [ ] Billing dashboard
- [ ] Documentación API pública
- [ ] Rate limiting avanzado
- [ ] Tests e2e
- [ ] Deploy multi-región (opcional)

### Tiempo Estimado

**20-30 horas** (1 dev, 3-4 días @ 8h/día)

---

## TIMELINE TOTAL

| Fase | Horas | Semanas | Status |
|------|-------|---------|--------|
| 1. Database + API + Tests | 4-5 | < 1 | ✅ COMPLETA |
| 2. Scraping + Monitoreo | 40-50 | 1 | ⏳ Próxima |
| 3. Análisis + Alertas | 30-40 | 1 | 📋 Planeada |
| 4. Expansión | 20-30 | < 1 | 📋 Planeada |
| **TOTAL MVP** | **~100-120** | **2-3** | 📊 En progreso |

---

## PRIORIZACIÓN

### Sprint 1 (Semana 2)

**Fase 2 - Parte 1:**
- Scraper básico (1 sitio: Mercado Libre)
- Celery + Redis setup
- Modelo Captura

### Sprint 2 (Semana 3)

**Fase 2 - Parte 2:**
- Scraper multi-sitio (5+ sitios)
- Alertas básicas
- Panel de Control

### Sprint 3 (Semana 4)

**Fase 3:**
- Scoring
- Timeline
- Reportes

### Sprint 4 (Semana 5)

**Fase 4:**
- Multi-brand
- API pública
- Webhooks
- Integraciones

---

## CONSIDERACIONES TÉCNICAS

### Infrastructure (Fase 2+)

```
Actual (Fase 1):
├── Railway PostgreSQL
├── Railway Gunicorn
└── GitHub

Necesario (Fase 2+):
├── Railway Redis (para Celery)
├── Railway Celery Workers (background jobs)
├── S3/R2 (para screenshots)
└── Email service (SendGrid o similar)
```

### Performance

**Fase 1:** 50 requests/min → OK
**Fase 2:** 1000+ scrapes/día → Necesita optimization

**Optimizaciones:**
- Caché de precios (Redis)
- Batch scraping
- Rate limiting de distribuidores
- Compression de screenshots

### Database

**Fase 1:** ~100 MB
**Fase 2:** ~1 GB (time-series)
**Fase 3:** ~5 GB (históricos + reportes)

**Upgrade necesario en Railway:**
- Fase 1: Starter Plan ($5/mes)
- Fase 2: Professional ($20-50/mes)
- Fase 3: Enterprise ($100+/mes)

---

## OPORTUNIDADES DE MONETIZACIÓN

1. **SaaS Freemium:**
   - Starter: 1 seller, 10 productos → $0
   - Professional: 5 sellers, 100 productos → $99/mes
   - Enterprise: Unlimited → $500/mes

2. **API Premium:**
   - 1000 req/mes gratis
   - $0.01 por request adicional

3. **Consulting:**
   - Setup custom de scrapers
   - Integraciones especializadas
   - Reportes personalizados

4. **Data Products:**
   - Índice de compliance por región
   - Predicción de violaciones
   - Benchmark contra industria

---

## MÉTRICAS DE ÉXITO

### Fase 2

- ✅ Scraping funcional para 5+ sitios
- ✅ Alertas generadas <5 min después de violación
- ✅ 99.5% uptime
- ✅ <1 segundo latencia en API

### Fase 3

- ✅ Scoring calculado correctamente
- ✅ Reportes generados en <30 seg
- ✅ >95% precisión en detección de patrones
- ✅ User engagement >50%

### Fase 4

- ✅ 100+ usuarios activos
- ✅ 50+ integraciones activas
- ✅ Revenue: $10k/mes
- ✅ NPS >50

---

## CONCLUSIÓN

Pulso tiene potencial de convertirse en una **plataforma de compliance de precio líder en LatAm**.

**Roadmap propuesto (2-3 meses):**
- Semanas 1-2: Fase 1 ✅ (COMPLETADA)
- Semanas 3-4: Fase 2 (Scraping)
- Semanas 5-6: Fase 3 (Análisis)
- Semana 7: Fase 4 (Expansión)

**Inversión:** 100-150 horas dev (1 senior dev, 2-3 meses)
**ROI potencial:** Alto (SaaS con margen >70%)

---

*Roadmap creado por Claude | 14 de Julio, 2026*
