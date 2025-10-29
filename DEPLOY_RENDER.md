# 🚀 Desplegar en Render - Paso a Paso

## ¿Qué es Render?

Render es una plataforma en la nube que te permite hospedar tu backend **GRATIS** (hasta 750 horas/mes, suficiente para este proyecto).

---

## 📋 Requisitos Previos

- [x] Cuenta de GitHub
- [x] Cuenta de Neon (con tu Connection String)
- [x] Código subido a GitHub

---

## 🔧 Paso 1: Preparar el Repositorio en GitHub

### Si aún NO has subido el código:

```bash
# 1. Inicializar Git
cd "C:\Users\PC SANTI\Desktop\Educambio_Voluntarios"
git init

# 2. Agregar archivos
git add .

# 3. Hacer commit
git commit -m "Initial commit - Educambio Backend"

# 4. Crear repo en GitHub y conectar
git remote add origin https://github.com/TU_USUARIO/educambio-backend.git
git branch -M main
git push -u origin main
```

### Si YA subiste el código:
✅ Continúa con el Paso 2

---

## 🌐 Paso 2: Crear Cuenta en Render

1. Ve a: **https://render.com**
2. Haz clic en **"Get Started for Free"**
3. Inicia sesión con tu cuenta de **GitHub**
4. Autoriza el acceso de Render a GitHub

---

## 🚀 Paso 3: Crear Web Service

1. En el dashboard de Render, haz clic en **"New +"**

2. Selecciona **"Web Service"**

3. **Conecta tu repositorio:**
   - Busca: `educambio-backend`
   - Haz clic en **"Connect"**

4. **Configuración del servicio:**

   ```
   ┌──────────────────────────────────────────┐
   │ Name: educambio-backend                 │
   │ Region: Oregon (US West)                │
   │ Branch: main                            │
   │ Runtime: Python 3                       │
   │ Build Command:                          │
   │   pip install -r requirements.txt       │
   │ Start Command:                          │
   │   python backend-neon.py                │
   │ Instance Type: Free                     │
   └──────────────────────────────────────────┘
   ```

5. Haz clic en **"Advanced"** para agregar variables de entorno

---

## 🔐 Paso 4: Configurar Variables de Entorno

En la sección **"Environment Variables"**:

1. Haz clic en **"Add Environment Variable"**

2. Agrega:
   ```
   Key:   DATABASE_URL
   Value: postgresql://neondb_owner:npg_TW46pOGQbHIU@ep-purple-fire-adc6c84m-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
   ```
   ⚠️ **IMPORTANTE:** Usa TU Connection String de Neon

3. *(Opcional)* Puedes agregar:
   ```
   Key:   PORT
   Value: 3000
   ```

---

## 🎯 Paso 5: Desplegar

1. Revisa la configuración

2. Haz clic en **"Create Web Service"**

3. **Render comenzará a desplegar:**
   - Clonará el repositorio
   - Instalará dependencias (`pip install -r requirements.txt`)
   - Iniciará el servidor (`python backend-neon.py`)

4. **Espera 5-10 minutos** (la primera vez puede tardar más)

5. Verás logs como:
   ```
   ==> Installing dependencies
   ==> Collecting Flask
   ==> Building...
   ==> Starting server
   ✅ Base de datos inicializada correctamente
   ✅ Servidor listo para recibir peticiones
   ```

---

## ✅ Paso 6: Obtener la URL de tu Backend

Una vez desplegado, verás tu URL en la parte superior:

```
https://educambio-backend.onrender.com
```

**Copia esta URL** (la necesitarás para Webflow)

---

## 🧪 Paso 7: Probar que Funciona

### Test 1: Health Check

Abre tu navegador y ve a:
```
https://educambio-backend.onrender.com/health
```

Deberías ver:
```json
{
  "status": "ok",
  "message": "Backend de tracking funcionando correctamente",
  "database": "connected"
}
```

✅ Si ves `"database": "connected"` → **¡PERFECTO!**

### Test 2: Enviar un dato de prueba

Abre PowerShell y ejecuta:

```powershell
$body = @{
    email = "prueba@render.com"
    name = "Test Render"
    volunteerCode = "TEST_RENDER"
    timestamp = (Get-Date).ToString("o")
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://educambio-backend.onrender.com/api/track" -Method POST -Body $body -ContentType "application/json"
```

Deberías ver:
```json
{
  "success": true,
  "message": "Tracking guardado exitosamente",
  "recordId": 1
}
```

### Test 3: Ver los datos guardados

Ve a:
```
https://educambio-backend.onrender.com/api/tracks
```

Deberías ver tu registro de prueba.

---

## 🔄 Paso 8: Actualizar index.html para Webflow

1. Abre `index.html` en tu editor

2. Busca la línea 251:
   ```javascript
   const SUSCRIPCIONES_URL = 'https://suscripciones.co/educambio/donar';
   ```
   Cámbiala por tu URL real de suscripciones.co

3. Busca la línea 254:
   ```javascript
   const BACKEND_URL = 'http://localhost:3000/api/track';
   ```
   
   Cámbiala por:
   ```javascript
   const BACKEND_URL = 'https://educambio-backend.onrender.com/api/track';
   ```
   ⚠️ Usa tu URL de Render (sin barra final)

4. **Guarda el archivo**

5. **Copia TODO** el contenido de `index.html`

6. En **Webflow**:
   - Ve a tu página `/voluntarios`
   - Edita el Embed
   - **Reemplaza** con el nuevo código
   - **Publica**

---

## 🎉 Paso 9: Probar el Flujo Completo

1. Ve a tu sitio en Webflow con un código de voluntario:
   ```
   https://www.educambio.org/voluntarios?ref=MARIA
   ```

2. Completa el formulario con datos de prueba

3. Haz clic en "Continuar a la donación"

4. Verifica que se guardó:
   ```
   https://educambio-backend.onrender.com/api/tracks
   ```

5. ¡Si ves tu registro, **TODO FUNCIONA**! 🎉

---

## 📊 Monitoreo y Mantenimiento

### Ver estadísticas en tiempo real:

- **Todos los registros:** https://educambio-backend.onrender.com/api/tracks
- **Estadísticas por voluntario:** https://educambio-backend.onrender.com/api/stats
- **Exportar CSV:** https://educambio-backend.onrender.com/api/export/csv
- **Estado del servidor:** https://educambio-backend.onrender.com/health

### Ver logs en Render:

1. Ve a tu dashboard en Render
2. Selecciona tu servicio `educambio-backend`
3. Haz clic en **"Logs"**
4. Verás todos los registros en tiempo real

---

## 🔄 Actualizar el Código

Cuando hagas cambios al código:

```bash
# 1. Hacer cambios en tu código local

# 2. Commit y push
git add .
git commit -m "Descripción de los cambios"
git push

# 3. Render detectará automáticamente y redesplegará
```

⚠️ El servicio gratuito de Render puede tardar 1-2 minutos en redesplegar.

---

## ⚠️ Limitaciones del Plan Gratuito

- ✅ **750 horas/mes** (suficiente para Educambio)
- ⚠️ El servicio **se pausa** después de 15 minutos de inactividad
- ⚠️ Al recibir la primera petición después de pausa, tarda ~30 segundos en "despertar"
- ✅ Se reactiva **automáticamente** cuando alguien usa el formulario

### Solución para el "despertar":

Puedes usar un servicio gratuito como **UptimeRobot** para hacer ping cada 14 minutos y mantener el servicio activo.

---

## 🆘 Troubleshooting

### ❌ Error: "Application failed to respond"

**Causa:** Puerto incorrecto o backend no inicia.

**Solución:**
1. Verifica que `backend-neon.py` use el puerto correcto
2. Revisa los logs en Render para ver el error específico

### ❌ Error: "database: disconnected"

**Causa:** Connection String de Neon incorrecto.

**Solución:**
1. Ve a Neon y copia de nuevo tu Connection String
2. En Render → Environment → Edita DATABASE_URL
3. Guarda y redesplega

### ❌ Error: "Build failed"

**Causa:** Error en `requirements.txt` o instalación de dependencias.

**Solución:**
1. Verifica que `requirements.txt` esté correcto
2. Revisa los logs de build en Render

### ❌ El servicio tarda mucho en responder

**Causa:** El servicio estaba pausado (plan gratuito).

**Solución:**
- Normal en plan gratuito
- Primera petición después de pausa: ~30 segundos
- Peticiones siguientes: instantáneas

---

## 💰 Costos

**Plan Gratuito:**
- ✅ 750 horas/mes (31 días × 24 horas = 744 horas)
- ✅ Suficiente para Educambio
- ✅ Sin tarjeta de crédito requerida

**Si necesitas más:**
- Plan Starter: $7/mes (sin pausa automática)

---

## ✅ Checklist Final

- [ ] Backend desplegado en Render
- [ ] URL copiada
- [ ] Test de /health exitoso
- [ ] Variables de entorno configuradas
- [ ] index.html actualizado con URL de Render
- [ ] Código actualizado en Webflow
- [ ] Prueba completa del flujo
- [ ] Registros se guardan correctamente

---

## 🎯 ¡Listo para Producción!

Una vez completados todos los pasos, tu sistema está **100% funcional** y listo para que tus voluntarios lo usen.

**¿Necesitas ayuda?** Revisa los logs en Render o contacta soporte.

---

**¡Éxito con tu despliegue! 💚**

