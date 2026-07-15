# 🧪 PULSO — Guía Completa de Testing

**Cómo testear Pulso SaaS sin interfaz visual (usando API REST + Postman)**

---

## 📋 TABLA DE CONTENIDOS

1. [Setup Inicial](#setup-inicial)
2. [Configurar Postman](#configurar-postman)
3. [Configurar Google Sheets](#configurar-google-sheets)
4. [Ejecutar Test Cases](#ejecutar-test-cases)
5. [Reportar Bugs](#reportar-bugs)
6. [Guía de Ambientes](#guía-de-ambientes)

---

## SETUP INICIAL

### Requisitos

- ✅ Postman (descargado)
- ✅ Google Sheets (acceso)
- ✅ Colección Postman (`PULSO_Postman_Collection.json`)
- ✅ Test Cases CSV (`PULSO_Test_Cases.csv`)
- ✅ URL de ambiente (local, staging, o production)

### Paso 1: Descargar Postman

```
https://www.postman.com/downloads/
```

Instalar y abrir.

### Paso 2: Descargar Insomnia (Alternativa más fácil)

```
https://insomnia.rest/
```

(Postman y Insomnia son equivalentes, Insomnia es un poco más simple)

---

## CONFIGURAR POSTMAN

### Paso 1: Importar Colección

1. **Abre Postman**
2. **Click "Collections"** (lado izquierdo)
3. **Click "Import"**
4. **Selecciona:** `PULSO_Postman_Collection.json`
5. **Click "Import"**

✅ Deberías ver la carpeta "Pulso API - Colección Completa" con todos los endpoints.

### Paso 2: Configurar Environment

#### Opción A: Para LOCAL

1. **Click "Environments"** (lado izquierdo)
2. **Click "+"** (nuevo environment)
3. **Nombre:** `Local`
4. **Agregar variables:**
   ```
   base_url = http://localhost:8000
   access_token = (se llena después de login)
   refresh_token = (se llena después de login)
   ```
5. **Click "Save"**

#### Opción B: Para PRODUCTION

1. **Click "+"** (nuevo environment)
2. **Nombre:** `Production`
3. **Agregar variables:**
   ```
   base_url = https://pulso-production.up.railway.app
   access_token = (se llena después de login)
   refresh_token = (se llena después de login)
   ```
4. **Click "Save"**

#### Opción C: Para STAGING

1. **Click "+"** (nuevo environment)
2. **Nombre:** `Staging`
3. **Agregar variables:**
   ```
   base_url = https://pulso-staging.up.railway.app
   access_token = (se llena después de login)
   refresh_token = (se llena después de login)
   ```
4. **Click "Save"**

### Paso 3: Seleccionar Environment Activo

**En la esquina superior derecha de Postman**, hay un dropdown que dice "No Environment".

**Click** y selecciona el environment que quieres usar (Local, Production, Staging).

### Paso 4: Probar Login

1. **Navega a:** Pulso API → 🔐 Auth → Login
2. **Click "Send"**
3. **Resultado esperado:**
   - Response `200`
   - JSON con `access_token` y `refresh_token`
   - Tokens guardados automáticamente en el environment

✅ Si ves el token guardado, ¡está funcionando!

---

## CONFIGURAR GOOGLE SHEETS

### Paso 1: Crear Google Sheet

1. Abre **Google Sheets** (https://sheets.google.com)
2. **Crear nuevo documento**
3. **Nombre:** `Pulso - Test Cases`

### Paso 2: Importar Test Cases CSV

1. **En tu Google Sheet, click "File" → "Import"**
2. **Selecciona:** `PULSO_Test_Cases.csv`
3. **Opción:** "Replace current sheet"
4. **Click "Import"**

✅ Deberías tener 50 test cases con columnas listas.

### Paso 3: Configurar el Sheet para Colaboración

1. **Click "Share"** (esquina superior derecha)
2. **Compartir con:** tu team
3. **Permisos:** Editor (para que todos puedan editar)

---

## EJECUTAR TEST CASES

### Flujo Típico de Testing

#### Fase 1: Login (Caso #1-4)

```
1. Abre Postman
2. Selecciona Environment "Local" (o Production)
3. Navega a: Auth → Login
4. Click "Send"
5. Verifica:
   - Response Status = 200
   - Response contiene access_token
   - Response contiene refresh_token
6. En Google Sheets:
   - Test Case #1: Marca ✅ PASS
   - Responsable: Tu nombre
   - Fecha: Hoy
```

#### Fase 2: Preparar Datos (Casos #23-40)

```
Crear Marcas, Categorías, Sellers primero:

1. Auth → Login (para obtener token)
2. Marcas → Crear Marca
   - Body: {"name": "Samsung"}
   - Send → Copiar el ID
3. Categorías → Crear Categoría
   - Body: {"name": "Smartphones"}
   - Send → Copiar el ID
4. Sellers → Crear Seller
   - Body: {"name": "Frávega", ...}
   - Send
5. Canales → Crear Canal
   - Body: {"name": "Mercado Libre", ...}
   - Send

En Google Sheets, marca todos como ✅ PASS
```

#### Fase 3: Test CRUD Productos (Casos #5-22)

**Crear Producto:**
```
1. Productos → Crear Producto
2. Body:
{
  "name": "Galaxy S24 Ultra",
  "sku": "SM-S918B-TEST",
  "model": "S24 Ultra",
  "brand_id": "COPIAR_DEL_PASO_ANTERIOR",
  "category_id": "COPIAR_DEL_PASO_ANTERIOR",
  "pvp_full": 1299000,
  "pvp_promo": 1099000
}
3. Click Send
4. Copiar el "id" de la respuesta

En Google Sheets:
- Test Case #6: ✅ PASS
- Notas: "Creado correctamente, ID: xxx"
```

**Listar Productos:**
```
1. Productos → Listar Productos
2. Click Send
3. Verifica que el producto que creaste aparece

En Google Sheets:
- Test Case #9: ✅ PASS
```

**Actualizar Producto:**
```
1. Productos → Actualizar Producto
2. Reemplaza {id} con el ID del producto anterior
3. Body:
{
  "pvp_full": 1199000
}
4. Click Send
5. Verifica status 200

En Google Sheets:
- Test Case #10: ✅ PASS
```

**Archivar Producto:**
```
1. Productos → Archivar Producto
2. Reemplaza {id}
3. Click Send
4. Verifica status 200 y status='archived'

En Google Sheets:
- Test Case #12: ✅ PASS
```

**Eliminar Producto:**
```
1. Productos → Eliminar Producto
2. Reemplaza {id}
3. Click Send
4. Verifica status 204 (No Content)

En Google Sheets:
- Test Case #11: ✅ PASS
```

#### Fase 4: Test Importación Excel (Casos #16-22)

**Crear archivo Excel:**
```
1. Abre Excel o Google Sheets
2. Crea archivo con columnas:
   Nombre | Marca | Modelo | SKU | Categoría | PVP Full | PVP Promo
   
3. Agrega datos:
   Galaxy S24 Ultra | Samsung | S24 Ultra | SM-S918B | Smartphones | 1299000 | 1099000
   Galaxy S24 | Samsung | S24 | SM-S918 | Smartphones | 999000 | 899000
   
4. Guarda como "productos.xlsx"
```

**Importar:**
```
1. Productos → Importar Productos (Excel)
2. Click "Select Files" en el campo "file"
3. Selecciona "productos.xlsx"
4. Click "Send"
5. Copia el "session_id" de la respuesta

En Google Sheets:
- Test Case #16: ✅ PASS
- Notas: "Session ID: abc123"
```

**Confirmar Importación:**
```
1. Productos → Confirmar Importación
2. Body:
{
  "session_id": "PEGAR_SESSION_ID_ANTERIOR"
}
3. Click "Send"
4. Verifica status 200 y "imported": 2

En Google Sheets:
- Test Case #18: ✅ PASS
```

**Exportar:**
```
1. Productos → Exportar Productos (Excel)
2. Click "Send"
3. Archivo Excel se descargará automáticamente
4. Verifica que contiene los productos

En Google Sheets:
- Test Case #21-22: ✅ PASS
```

---

## REPORTAR BUGS

### Si un Test FALLA (❌)

#### En Google Sheets:

1. **Status:** Marca ❌ FAIL
2. **Notas:** Describe exactamente qué pasó

**Ejemplo:**
```
Test Case #6: Crear Producto
Status: ❌ FAIL
Notas: "Error 400. Mensaje: 'brand_id is required'"
```

#### Crear Issue en GitHub:

1. Ve a: https://github.com/tu-usuario/pulso/issues
2. Click "New Issue"
3. **Título:** `[BUG] Crear producto falla sin brand_id`
4. **Descripción:**
   ```
   **Escenario:** Crear producto vía POST /api/v1/products/
   
   **Pasos:**
   1. Enviar POST con payload completo pero sin brand_id
   2. Response: 400
   
   **Resultado esperado:** Rechazo claro con error validation
   **Resultado actual:** Error 400 confuso
   
   **Ambiente:** Local
   **Responsable:** Lucas
   ```

---

## GUÍA DE AMBIENTES

### Environment 1: LOCAL (Tu máquina)

```
URL Base: http://localhost:8000

Ventajas:
✅ Cero latencia
✅ Acceso a logs en terminal
✅ Puedes debuggear fácilmente

Desventajas:
❌ Solo tú puedes testear
❌ Requiere que tengas servidor corriendo

Cuándo usar:
- Durante desarrollo
- Para debugging
- Tests rápidos personales
```

**Cómo correr:**
```bash
python manage.py runserver
```

### Environment 2: STAGING (Railway)

```
URL Base: https://pulso-staging.up.railway.app

Ventajas:
✅ Todos pueden testear
✅ Similar a producción
✅ BD separada de prod

Desventajas:
❌ Requiere crear repo staging en Railway

Cuándo usar:
- Testing con el team
- Validar cambios antes de production
- Pruebas funcionales
```

**Cómo crear:**
1. Railway.app → New Project
2. Deploy from GitHub repo
3. Nombre: `pulso-staging`
4. Env vars: iguales a production
5. Deploy

### Environment 3: PRODUCTION (Railway)

```
URL Base: https://pulso-production.up.railway.app

Ventajas:
✅ Versión final
✅ Datos reales

Desventajas:
❌ NO testear datos destructivos aquí
❌ Afecta a usuarios reales

Cuándo usar:
- Solo pruebas lectura (GET)
- Validar que la versión funciona
- Demo a usuarios
```

---

## WORKFLOW RECOMENDADO

### Día 1: Setup

```
[ ] Descargar Postman/Insomnia
[ ] Importar colección Pulso
[ ] Crear 3 environments (Local, Staging, Production)
[ ] Crear Google Sheet de test cases
[ ] Invitar al team a Google Sheet
```

### Día 2-3: Testing en LOCAL

```
[ ] Testear todos los casos en ambiente Local
[ ] Anotar resultados en Google Sheet
[ ] Reportar bugs encontrados
[ ] Ejecutar fixes si es necesario
```

### Día 4: Testing en STAGING

```
[ ] Crear ambiente Staging en Railway
[ ] Repetir tests en Staging
[ ] Verificar que todo funciona igual que Local
[ ] Anotar diferencias si las hay
```

### Día 5: Demo en PRODUCTION

```
[ ] Hacer demo a usuarios finales
[ ] Recopilar feedback
[ ] Anotar mejoras solicitadas
```

---

## TIPS & TRICKS

### Tip 1: Guardar Responses Automáticamente

**En Postman:**
1. Haz click en "Tests" (pestaña arriba del Body)
2. Agrega script:
```javascript
// Guardar ID del producto creado
if (pm.response.code === 201) {
    var jsonData = pm.response.json();
    pm.environment.set('last_product_id', jsonData.id);
}
```

Luego puedes usar `{{last_product_id}}` en otros requests.

### Tip 2: Usar Timestamps para SKU Único

**En Body del request:**
```json
{
  "sku": "SM-S918B-{{$timestamp}}"
}
```

Esto genera SKU único cada vez que envías, evitando errores de duplicado.

### Tip 3: Ver Logs en Production

**En Railway:**
1. Click en el deployment
2. Click "Logs"
3. Verás errores en tiempo real

Útil para debuggear bugs de production.

### Tip 4: Compartir Resultados

**En Google Sheets:**
1. Click "Share"
2. Copiar link
3. Enviar a stakeholders

Ellos pueden ver resultados en vivo sin necesidad de Postman.

---

## CHECKLIST DE COMPLETITUD

| Fase | Tarea | Status |
|------|-------|--------|
| Setup | Postman instalado | ⏳ |
| Setup | Colección importada | ⏳ |
| Setup | Environments creados | ⏳ |
| Setup | Google Sheet compartido | ⏳ |
| Testing | 50 test cases ejecutados | ⏳ |
| Testing | Bugs reportados | ⏳ |
| Testing | Validaciones pasadas | ⏳ |
| Staging | Staging en Railway | ⏳ |
| Staging | Repetir tests en Staging | ⏳ |
| Demo | Demo a usuarios | ⏳ |
| Demo | Feedback recopilado | ⏳ |

---

## PREGUNTAS FRECUENTES

### P: ¿Necesito el frontend visual para testear?
**R:** No. El API REST es completamente funcional. Frontend es opcional.

### P: ¿Puedo testear en producción?
**R:** Sí, pero SOLO lectura (GET). No crear/editar/eliminar datos reales.

### P: ¿Qué pasa si un test falla?
**R:** Reporta en GitHub issues. Developer lo arreglará. Repite el test después del fix.

### P: ¿Cuánto tiempo toma testear todo?
**R:** ~4-6 horas si es la primera vez. Después ~1-2 horas por ciclo.

### P: ¿Puedo testear sin Postman?
**R:** Sí, con `curl` en terminal. Pero Postman es más cómodo.

---

## CONTACTO & SOPORTE

Si tienes dudas:
1. Crea un issue en GitHub
2. O pregunta directamente en el chat

---

**¡Buena suerte testando! 🧪**

*Guía creada por Claude | 14 de Julio, 2026*
