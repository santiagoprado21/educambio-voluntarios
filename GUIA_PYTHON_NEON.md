# 🚀 Guía Completa: Python + Neon + Webflow

## 📖 ¿Qué hace cada archivo?

### Archivos que SÍ usas en producción:
- **`index.html`** → Formulario que va en Webflow (embedded code)
- **`backend-neon.py`** → Servidor que guarda datos en Neon
- **`matcher.py`** → Script para cruzar donaciones con voluntarios

### Archivos auxiliares (herramientas para TI):
- **`generar-enlaces.html`** → Herramienta para crear enlaces (la abres localmente)
- **`test-backend.bat`** → Para probar el backend en Windows

---

## 🎯 FLUJO COMPLETO DEL SISTEMA

### 1️⃣ **Generar Enlaces (TU computadora)**

```
Tú (admin) → Abres generar-enlaces.html localmente
           → Ingresas lista de voluntarios
           → Copias los enlaces generados
           → Envías cada enlace a su voluntario
```

**Lo que obtienes:**
```
María → https://educambio.com/?ref=MARIA
Juan  → https://educambio.com/?ref=JUAN123
Pedro → https://educambio.com/?ref=PEDRO
```

### 2️⃣ **Voluntarios comparten sus enlaces**

```
Voluntario María → Comparte su enlace en redes sociales
                 → Alguien hace clic
                 → Ve el formulario (index.html en Webflow)
```

### 3️⃣ **Donante completa el formulario**

```
Donante → Ingresa su email
        → El sistema guarda: email + código MARIA
        → Es redirigido a suscripciones.co
        → Completa su donación
```

### 4️⃣ **Matching (cada semana/mes)**

```
Tú (admin) → Exportas CSV de suscripciones.co
           → Ejecutas: python matcher.py donaciones.csv
           → Obtienes reporte: ¿Cuántas donaciones generó cada voluntario?
```

---

## 📋 PASO A PASO DE IMPLEMENTACIÓN

### **PASO 1: Crear cuenta en Neon (5 minutos)**

1. Ve a [https://neon.tech](https://neon.tech)
2. Crea cuenta gratis
3. Crea un nuevo proyecto llamado "educambio"
4. Copia tu **Connection String** (se ve así):
   ```
   postgresql://usuario:password@ep-xxx-xxx.neon.tech/neondb?sslmode=require
   ```

### **PASO 2: Configurar el Backend (10 minutos)**

#### En tu computadora (Windows):

```powershell
# 1. Instalar Python (si no lo tienes)
# Descarga desde: https://www.python.org/downloads/

# 2. Instalar dependencias
pip install Flask Flask-CORS psycopg2-binary

# 3. Configurar la URL de Neon
# Opción A: Variable de entorno (recomendado)
$env:DATABASE_URL = "tu_connection_string_de_neon"

# Opción B: Editar backend-neon.py línea 16
# DATABASE_URL = 'tu_connection_string_de_neon'

# 4. Iniciar el servidor
python backend-neon.py
```

**Deberías ver:**
```
✅ Base de datos inicializada correctamente
✅ Servidor listo para recibir peticiones
🌐 Servidor corriendo en: http://localhost:3000
```

### **PASO 3: Configurar index.html (5 minutos)**

Abre `index.html` y edita estas dos líneas:

```javascript
// Línea 251: URL de suscripciones.co (tu URL real)
const SUSCRIPCIONES_URL = 'https://checkout.suscripciones.co/tu-pagina-real';

// Línea 254: URL del backend (por ahora localhost, luego la cambiarás)
const BACKEND_URL = 'http://localhost:3000/api/track';
```

### **PASO 4: Probar localmente (5 minutos)**

1. **Probar el backend:**
   - Abre: http://localhost:3000/health
   - Deberías ver: `{"status":"ok","database":"connected"}`

2. **Probar el formulario:**
   - Abre `index.html` en tu navegador con un código de prueba:
   - `file:///C:/ruta/index.html?ref=TEST`
   - Ingresa un email y envía el formulario
   - Verifica en la terminal que apareció: `✅ Nuevo tracking guardado`

3. **Ver los datos guardados:**
   - Abre: http://localhost:3000/api/tracks
   - Deberías ver tu prueba registrada

### **PASO 5: Generar enlaces para voluntarios (5 minutos)**

1. Abre `generar-enlaces.html` en tu navegador (doble clic)
2. En "URL Base" pon: `https://educambio.com` (tu dominio real)
3. En "Lista de Voluntarios" ingresa:
   ```
   MARIA, María González
   JUAN123, Juan Pérez
   PEDRO, Pedro López
   ```
4. Clic en "Generar Enlaces"
5. Copia cada enlace y envíalo a cada voluntario por WhatsApp/Email

### **PASO 6: Integrar en Webflow (15 minutos)**

#### Opción A: Página Embebida Completa (Recomendada)

1. En Webflow, crea una nueva página: `/donaciones`
2. Agrega un elemento "Embed"
3. Copia TODO el contenido de `index.html`
4. Pégalo en el embed de Webflow
5. Publica

#### Opción B: Solo el formulario en una sección

1. En Webflow, ve a la página donde quieres el formulario
2. Agrega un elemento "Embed"
3. Copia desde `<div class="container">` hasta `</div>` de `index.html`
4. También copia el `<style>` y el `<script>`
5. Pégalo en el embed
6. Publica

**Nota importante:** Asegúrate de que en `index.html` el `BACKEND_URL` apunte a tu servidor en producción (no localhost).

### **PASO 7: Desplegar Backend en producción (20 minutos)**

#### Opción A: Render (Gratuito)

1. Ve a [https://render.com](https://render.com)
2. Crea cuenta y conecta tu GitHub
3. Sube tu código a GitHub (incluye `backend-neon.py` y `requirements.txt`)
4. En Render: "New +" → "Web Service"
5. Selecciona tu repositorio
6. Configuración:
   - **Name:** educambio-backend
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python backend-neon.py`
7. En "Environment Variables" agrega:
   - **Key:** `DATABASE_URL`
   - **Value:** (tu connection string de Neon)
8. Clic en "Create Web Service"
9. Espera 5-10 minutos
10. Copia la URL que te dan (ej: `https://educambio-backend.onrender.com`)

#### Opción B: Railway (Gratuito con créditos)

1. Ve a [https://railway.app](https://railway.app)
2. Similar proceso a Render
3. Deploy automático desde GitHub

### **PASO 8: Actualizar URLs en producción (5 minutos)**

Edita `index.html` con las URLs reales:

```javascript
const SUSCRIPCIONES_URL = 'https://checkout.suscripciones.co/educambio/tu-pagina';
const BACKEND_URL = 'https://educambio-backend.onrender.com/api/track';
```

Vuelve a copiar el código actualizado en Webflow y publica.

### **PASO 9: Hacer matching de donaciones (10 minutos)**

Cada semana/mes cuando quieras ver resultados:

```bash
# 1. Exporta donaciones desde suscripciones.co (botón exportar)
# Guarda el archivo como: donaciones.csv

# 2. Exporta tracking desde tu backend
# Abre en navegador: https://educambio-backend.onrender.com/api/export/csv
# Se descargará: voluntarios_tracking.csv

# 3. Ejecuta el matcher
python matcher.py donaciones.csv

# 4. Revisa los resultados
# Se crearán dos archivos:
# - donaciones_con_voluntarios.csv (todas las donaciones con su voluntario)
# - resumen_voluntarios.csv (cuántas donaciones por voluntario)
```

**Salida esperada:**
```
✅ Matches encontrados: 42 (87.5%)
❌ Sin match: 6 (12.5%)

📊 Resumen por voluntario:
==================================================
  MARIA: 15 donaciones ($1,500,000)
  JUAN123: 12 donaciones ($1,200,000)
  PEDRO: 8 donaciones ($800,000)
```

---

## 🔧 CONFIGURACIÓN DE requirements.txt

Asegúrate de tener este archivo actualizado:

```txt
Flask==3.0.0
Flask-CORS==4.0.0
psycopg2-binary==2.9.9
pandas==2.1.3
openpyxl==3.1.2
```

---

## ❓ PREGUNTAS FRECUENTES

### **P: ¿Para qué es `generar-enlaces.html` si solo puedo usar embed code en Webflow?**

**R:** `generar-enlaces.html` NO va en Webflow. Es una herramienta AUXILIAR que TÚ (administrador) usas en tu computadora para crear los enlaces de los voluntarios. Solo abres ese archivo localmente, generas los enlaces, y los compartes con tus voluntarios.

Lo que SÍ va en Webflow es `index.html` (el formulario).

### **P: ¿Qué archivo va en Webflow?**

**R:** Solo `index.html`. Este archivo contiene el formulario que los donantes ven cuando hacen clic en el enlace del voluntario.

### **P: ¿Necesito poner el backend en Webflow?**

**R:** NO. El backend (`backend-neon.py`) va en un servidor separado (Render, Railway, Heroku, etc). Webflow solo muestra el formulario, pero los datos se guardan en Neon a través del backend.

### **P: ¿Puedo usar solo Webflow sin servidor?**

**R:** Sí, pero con limitaciones:
- Los datos se guardarían solo en el navegador del usuario (localStorage)
- Si cambian de dispositivo, se pierden
- Es más complicado hacer el matching

Es mejor usar un servidor (Render es gratis).

### **P: ¿Cómo sé si está funcionando?**

**R:** Haz una donación de prueba:
1. Abre tu enlace en modo incógnito: `https://educambio.com/?ref=TEST`
2. Ingresa un email de prueba
3. Verás el mensaje de éxito
4. Ve a: `https://tu-backend.onrender.com/api/tracks`
5. Deberías ver tu email + código TEST

### **P: ¿Los voluntarios pueden ver las donaciones de otros?**

**R:** NO. Los voluntarios solo comparten su enlace único. Solo TÚ (admin) puedes ver todos los datos accediendo a:
- El backend directamente
- El panel de Neon
- Los reportes del matcher

### **P: ¿Qué pasa si suscripciones.co no me permite integraciones?**

**R:** No hay problema, ese es precisamente el propósito de este sistema. NO necesitas integrarte con suscripciones.co. El sistema funciona así:

1. Capturas el email ANTES de que lleguen a suscripciones.co
2. Los rediriges a suscripciones.co (ellos hacen su donación normal)
3. Después, TÚ cruzas los datos exportando desde suscripciones.co

### **P: ¿Cuánto cuesta esto?**

**R:** GRATIS (con limitaciones):
- Neon: Gratis hasta 3 proyectos, 10GB
- Render: Gratis con 750 horas/mes (suficiente)
- Webflow: Depende de tu plan actual

---

## 🚨 TROUBLESHOOTING

### Error: "Failed to fetch" en el formulario

**Causa:** El backend no está corriendo o la URL es incorrecta.

**Solución:**
```bash
# 1. Verifica que el backend esté corriendo
http://localhost:3000/health
# o
https://tu-backend.onrender.com/health

# 2. Verifica que la URL en index.html sea correcta (línea 254)
```

### Error: "Database connection failed"

**Causa:** La URL de Neon es incorrecta o Neon está en pausa.

**Solución:**
```bash
# 1. Verifica tu connection string en Neon
# 2. Reactiva el proyecto si está pausado (gratis se pausa después de inactividad)
# 3. Verifica que la variable DATABASE_URL esté configurada
```

### No encuentro matches en el matcher

**Causa:** El nombre de la columna de email es diferente.

**Solución:**
```bash
# 1. Abre donaciones.csv y mira cómo se llama la columna de email
# 2. Ejecuta el matcher con el nombre correcto:
python matcher.py donaciones.csv --email-column "Correo electrónico"
```

### El formulario no guarda en Webflow

**Causa:** CORS o URL incorrecta.

**Solución:**
```bash
# 1. Abre la consola del navegador (F12)
# 2. Busca errores en rojo
# 3. Si dice "CORS", verifica que tu backend tenga CORS habilitado (ya lo tiene)
# 4. Si dice "Failed to fetch", verifica la URL del backend
```

---

## 📊 MONITOREO EN PRODUCCIÓN

### Ver registros en tiempo real:
```
https://tu-backend.onrender.com/api/tracks
```

### Ver estadísticas por voluntario:
```
https://tu-backend.onrender.com/api/stats
```

### Exportar a CSV:
```
https://tu-backend.onrender.com/api/export/csv
```

### Ver salud del sistema:
```
https://tu-backend.onrender.com/health
```

---

## ✅ CHECKLIST FINAL

- [ ] Cuenta de Neon creada y connection string copiada
- [ ] Backend instalado y corriendo en mi computadora
- [ ] Probé el backend con http://localhost:3000/health
- [ ] Configuré las URLs en `index.html`
- [ ] Probé el formulario localmente
- [ ] Generé enlaces con `generar-enlaces.html`
- [ ] Integré `index.html` en Webflow
- [ ] Desplegué el backend en Render
- [ ] Actualicé `BACKEND_URL` en Webflow con la URL de producción
- [ ] Hice una donación de prueba completa
- [ ] Verifiqué que se guardó en la base de datos
- [ ] Exporté CSV de prueba desde suscripciones.co
- [ ] Ejecuté `matcher.py` con éxito

---

## 🎉 ¡LISTO!

Ahora tienes un sistema completo para trackear las donaciones de tus voluntarios sin necesidad de acceso al backend de suscripciones.co.

**¿Necesitas ayuda?** Revisa los errores en:
1. Consola del navegador (F12)
2. Terminal del backend
3. Logs de Render (si aplica)

**¡Éxito! 💚**

