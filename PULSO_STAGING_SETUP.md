# 🚀 PULSO — Setup Staging en Railway

**Cómo crear un ambiente de staging para testing sin afectar producción**

---

## ¿QUÉ ES STAGING?

**Staging = Copia exacta de production, con BD separada.**

```
Production:   https://pulso-production.up.railway.app  → Usuarios reales
                                                ↓
Staging:      https://pulso-staging.up.railway.app     → Testing (sin usuarios)
                                                ↓
Local:        http://localhost:8000                    → Tu máquina
```

**Ventajas:**
- ✅ Todos pueden testear sin afectar prod
- ✅ BD separada (no tocas datos reales)
- ✅ Igual a production (detecta bugs que no ves en local)
- ✅ Auto-deploy desde GitHub (igual que prod)

---

## PASO A PASO: CREAR STAGING

### PASO 1: Ir a Railway.app

```
https://railway.app/
```

Asegúrate de estar logged-in con tu cuenta.

---

### PASO 2: Crear Nuevo Proyecto

1. **Click "New Project"** (botón principal)
2. **Opción:** "Deploy from GitHub repo"

---

### PASO 3: Conectar tu repo Pulso

1. **Selecciona:** `tu-usuario/pulso`
2. **Autoriza** si Railway pide permisos
3. **Click "Deploy"**

---

### PASO 4: Configurar Variables de Entorno

Después de que empieza el deploy (tarda ~1-2 minutos):

1. **Click en el deployment** que dice `web`
2. **Click en "Variables"** (pestaña superior)
3. **Agregar estas env vars:**

```
DEBUG=False
SECRET_KEY=staging-secret-key-2026-change-me
ALLOWED_HOSTS=*
JWT_SECRET=staging-jwt-secret-2026
DATABASE_URL=(auto-generada por Railway, déjala vacía)
```

**Nota:** Railway crea `DATABASE_URL` automáticamente cuando activas PostgreSQL.

---

### PASO 5: Activar PostgreSQL (Auto)

**Railway automáticamente:**
1. Crea una BD PostgreSQL separada
2. Genera `DATABASE_URL`
3. La asigna al proyecto

**Para verificar:**
1. Click en "Variables"
2. Busca `DATABASE_URL`
3. Debe estar presente (no editar manualmente)

---

### PASO 6: Ejecutar Migraciones

**Railway ejecuta automáticamente:**
```bash
python manage.py migrate
```

Porque está en el `Procfile`:
```
release: python manage.py migrate
```

**Para verificar que pasó:**
1. Click en "Deployments"
2. Mira los logs
3. Busca mensaje de migración

---

### PASO 7: Obtener URL de Staging

1. **Click en el deployment**
2. **Busca en la parte superior derecha**
3. **URL similar a:**
```
https://pulso-staging-xxxxx.up.railway.app
```

**Cópiala.**

---

### PASO 8: Probar que Funciona

**En Postman:**

1. **Crea nuevo Environment:** `Staging`
2. **Agrega variable:**
   ```
   base_url = https://pulso-staging-xxxxx.up.railway.app
   ```
3. **Selecciona Environment:** `Staging`
4. **Ejecuta:** Auth → Login
5. **Resultado esperado:** 200 + token

✅ Si ves el token, ¡Staging está VIVO!

---

## REPLICAR DATOS DE PRODUCTION A STAGING (Opcional)

### Opción A: Manual (Recomendado)

**En Staging, crear datos de demo:**

1. Login en Staging
2. Crear Marcas (Samsung, LG)
3. Crear Categorías (Smartphones, Televisores)
4. Crear Sellers (Frávega, Garbarino)
5. Crear Canales (Mercado Libre, etc.)
6. Importar productos via Excel

**Ventaja:** Datos controlados, sin info sensible.

### Opción B: Clonación de BD (Avanzado)

Railway permite clonar BD, pero es más complejo. Saltemos esto por ahora.

---

## WORKFLOW CON STAGING

### Semana 1: Desarrollo en LOCAL

```
Developer:
1. Código en Local (http://localhost:8000)
2. Tests en Local
3. Commit a GitHub
```

### Semana 1-2: Testing en STAGING

```
QA/Testers:
1. Railway auto-deploya desde GitHub
2. Tests en Staging (https://pulso-staging-xxxxx.up.railway.app)
3. Reportan bugs en GitHub Issues
```

### Semana 2: Deploy a PRODUCTION

```
DevOps:
1. Aprobar cambios
2. Merge a main (o crear release branch)
3. Railway auto-deploya a Production
4. Usuarios finales usan production
```

---

## COMPARAR LOCAL vs STAGING vs PRODUCTION

| Aspecto | Local | Staging | Production |
|--------|-------|---------|-----------|
| **URL** | http://localhost:8000 | https://...staging... | https://...production... |
| **BD** | SQLite (local) | PostgreSQL (Railway) | PostgreSQL (Railway) |
| **Server** | Runserver (dev) | Gunicorn (prod) | Gunicorn (prod) |
| **Usuarios** | Solo tú | Team | Usuarios reales |
| **Datos** | Demo | Demo controlados | Reales |
| **Uptime** | No importa | 99.5% | 99.9% |

---

## MONITOREAR STAGING

### Ver Logs

1. Railway.app → Proyecto Staging
2. Click "Deployments"
3. Click en el deployment actual
4. Scroll down → "Logs"

Verás todos los eventos y errores en tiempo real.

### Ver Métricas

1. Click "Metrics"
2. Ver:
   - CPU usage
   - Memory usage
   - Network I/O
   - Request count

---

## TROUBLESHOOTING

### Problema: Staging no inicia

**Solución:**
1. Check logs → qué error dice
2. Si dice "Database error" → Esperar 1-2 min
3. Si dice "Migration error" → Check settings.py

### Problema: Staging no puede conectar a BD

**Solución:**
1. Verifica que `DATABASE_URL` existe
2. Si no, Railway no activó PostgreSQL aún
3. Espera 2-3 minutos más
4. Click "Redeploy"

### Problema: Staging siempre dice "Crashed"

**Solución:**
1. Mira "Build Logs" (no Deploy Logs)
2. Busca errores de compilation
3. Probablemente falta dependencia en requirements.txt
4. Agrega a requirements.txt
5. Push a GitHub
6. Railway auto-redeploya

---

## PUSH AUTOMÁTICO DESDE GITHUB

**Railway monitorea tu repo.**

```
Tu workflow:
1. Haces cambios en Local
2. git push origin main
3. GitHub recibe push
4. Railway detecta cambio
5. Railway auto-deploy en Staging (y Production)

Tiempo: ~2-3 minutos
```

---

## COSTO DE STAGING EN RAILWAY

| Recurso | Costo |
|---------|-------|
| PostgreSQL (BD) | $5/mes (compartida) |
| Gunicorn server | $0 (free tier) o $5 (pro) |
| **TOTAL** | $5-10/mes |

**Más barato que:** AWS, Google Cloud, Heroku.

---

## CONFIGURACIÓN FINAL RECOMENDADA

```
Railway Dashboard:

Proyecto: pulso-production
├── Ambiente: production
└── URL: https://pulso-production.up.railway.app

Proyecto: pulso-staging
├── Ambiente: staging
└── URL: https://pulso-staging-xxxxx.up.railway.app

GitHub:
└── Repo: pulso
    ├── Branch: main (auto-deploy a production)
    ├── Branch: staging (auto-deploy a staging)
    └── Branch: develop (trabajo local)
```

---

## CHECKLIST FINAL

| Tarea | Status |
|-------|--------|
| Crear proyecto en Railway | ⏳ |
| Conectar GitHub repo | ⏳ |
| Configurar env vars | ⏳ |
| PostgreSQL creada | ⏳ |
| Migraciones ejecutadas | ⏳ |
| Obtener URL staging | ⏳ |
| Probar login en Staging | ⏳ |
| Crear datos de demo | ⏳ |
| Compartir URL con team | ⏳ |

---

## PRÓXIMO PASO

**Una vez Staging esté listo:**

1. Comparte URL con el team: `https://pulso-staging-xxxxx.up.railway.app`
2. Comparte colección Postman
3. Comparte Google Sheet de test cases
4. ¡Comienzan las pruebas!

---

## CONTACTO

Si tienes dudas con Railway:
- Documentación: https://docs.railway.app/
- Support: https://railway.app/support

---

*Guía creada por Claude | 14 de Julio, 2026*
