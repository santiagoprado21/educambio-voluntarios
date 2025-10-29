# 🎯 Sistema de Tracking de Voluntarios - Educambio

Sistema completo para rastrear qué voluntarios generan donaciones cuando no tienes acceso al backend de la plataforma de pagos (suscripciones.co).

**Stack:** Python + PostgreSQL (Neon) + Webflow

---

## 🚀 INICIO RÁPIDO

### 1️⃣ **Configuración Local**
👉 Lee: **[START_HERE_PYTHON_NEON.txt](START_HERE_PYTHON_NEON.txt)** ← Comandos listos para copiar

### 2️⃣ **Subir a GitHub**
👉 Lee: **[GIT_SETUP.md](GIT_SETUP.md)** ← Paso a paso para Git

### 3️⃣ **Desplegar en Render**
👉 Lee: **[DEPLOY_RENDER.md](DEPLOY_RENDER.md)** ← Despliegue a producción

### 📚 **Documentación Completa**
👉 Lee: **[GUIA_PYTHON_NEON.md](GUIA_PYTHON_NEON.md)** ← Guía detallada

---

## 📋 Tabla de Contenidos

- [¿Cómo Funciona?](#cómo-funciona)
- [Instalación Rápida](#instalación-rápida)
- [Configuración](#configuración)
- [Uso](#uso)
- [Matching de Donaciones](#matching-de-donaciones)
- [Opciones de Despliegue](#opciones-de-despliegue)
- [Documentación Adicional](#documentación-adicional)

## 🔍 ¿Cómo Funciona?

El sistema funciona en 3 pasos:

### 1️⃣ Generación de Enlaces
Cada voluntario recibe un enlace único:
```
https://tu-sitio.com/?ref=VOLUNTARIO001
https://tu-sitio.com/?ref=MARIA
https://tu-sitio.com/?ref=JUAN123
```

### 2️⃣ Captura de Información
Cuando alguien hace clic en el enlace:
- Se muestra una landing page profesional
- El donante ingresa su **email** (y opcionalmente su nombre)
- Esta información se guarda asociada al código del voluntario
- El usuario es redirigido a suscripciones.co

### 3️⃣ Matching Posterior
Periódicamente (diario/semanal):
- Exportas las donaciones desde suscripciones.co
- Ejecutas el script `matcher.py`
- El script cruza los emails y te genera un reporte completo

## 🚀 Instalación Rápida

### Instalación Local:

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Crear cuenta en Neon: https://neon.tech
# 3. Copiar Connection String de Neon

# 4. Configurar variable de entorno (PowerShell)
$env:DATABASE_URL = "tu_connection_string_de_neon"

# 5. Iniciar backend
python backend-neon.py
```

📖 **Guía completa:** [START_HERE_PYTHON_NEON.txt](START_HERE_PYTHON_NEON.txt)

## ⚙️ Configuración

### 1. Configurar la URL de Suscripciones.co

Edita el archivo `index.html` y modifica esta línea:

```javascript
// Línea 170 aprox.
const SUSCRIPCIONES_URL = 'https://suscripciones.co/educambio/donar';
```

Cambia la URL por la URL real de donación de suscripciones.co

### 2. Configurar el Backend (si usas hosting diferente)

Si vas a hostear el backend en un servidor diferente al frontend, edita `index.html`:

```javascript
// Línea 173 aprox.
const BACKEND_URL = 'https://tu-servidor.com/api/track';
```

## 📝 Uso

### Para los Voluntarios

Cada voluntario debe compartir su enlace personalizado:

```
https://tu-sitio.com/?ref=CODIGO_DEL_VOLUNTARIO
```

**Ejemplos:**
- `https://educambio.com/?ref=MARIA`
- `https://educambio.com/?ref=JUAN123`
- `https://educambio.com/?ref=VOL001`

### Para los Administradores

#### 1. Monitorear Tracking en Tiempo Real

```bash
# Ver todos los registros guardados
curl http://localhost:3000/api/tracks

# O visita en el navegador:
http://localhost:3000/api/tracks
```

#### 2. Exportar Tracking

```bash
# Descargar CSV con todos los registros
curl http://localhost:3000/api/export/csv -o tracking.csv

# O visita en el navegador:
http://localhost:3000/api/export/csv
```

## 🎯 Matching de Donaciones

### Paso 1: Exportar Donaciones de Suscripciones.co

Exporta las donaciones desde suscripciones.co en formato CSV o Excel.

### Paso 2: Ejecutar el Matcher

```bash
python matcher.py donaciones.csv
```

Si la columna de email tiene otro nombre:

```bash
python matcher.py donaciones.csv --email-column correo_electronico
```

Si quieres usar matching por fecha también:

```bash
python matcher.py donaciones.csv --email-column email --date-column fecha_donacion
```

### Paso 3: Revisar los Resultados

El script genera dos archivos:

1. **`donaciones_con_voluntarios.csv`** - Todas las donaciones con su voluntario asignado
2. **`resumen_voluntarios.csv`** - Resumen de cuántas donaciones generó cada voluntario

Ejemplo de salida:

```
✅ Matches encontrados: 42 (87.5%)
❌ Sin match: 6 (12.5%)

📊 Resumen por voluntario:
==================================================
  MARIA: 15 donaciones
  JUAN123: 12 donaciones
  VOL001: 8 donaciones
  PEDRO: 7 donaciones
```

## 🌐 Opciones de Despliegue

### Opción 1: Webflow (Frontend) + Servidor Simple (Backend)

1. **Frontend en Webflow:**
   - Sube el archivo `index.html` a Webflow como página personalizada
   - O copia el HTML/CSS/JS a un embed de Webflow

2. **Backend:**
   - Despliega el backend en:
     - **Heroku** (gratis para proyectos pequeños)
     - **Render** (gratis con limitaciones)
     - **Railway** (gratis con créditos)
     - Tu propio servidor VPS

### Opción 2: Todo en un Hosting Simple

Si tienes un hosting con PHP/Node.js/Python, puedes subir todo junto:

```
/public_html/
  ├── index.html          (landing page)
  ├── backend-simple.js   (backend)
  └── matcher.py          (script de matching)
```

### Opción 3: Netlify/Vercel (Frontend) + Backend Separado

1. **Frontend:** Despliega `index.html` en Netlify o Vercel (gratis)
2. **Backend:** Usa un servicio serverless o un servidor simple

### Opción 4: Sin Backend (Solo LocalStorage + Export Manual)

Si no puedes/quieres usar un backend:

1. El sistema guardará todo en `localStorage` del navegador
2. Puedes exportar los datos manualmente desde la consola del navegador:

```javascript
// En la consola del navegador (F12)
console.log(localStorage.getItem('educambio_donations'));

// O descargar como archivo:
const data = localStorage.getItem('educambio_donations');
const blob = new Blob([data], {type: 'application/json'});
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'tracking.json';
a.click();
```

## 🎨 Personalización

### Colores y Diseño

Edita el CSS en `index.html` (sección `<style>`):

```css
/* Cambiar colores principales */
background: linear-gradient(135deg, #TU_COLOR_1 0%, #TU_COLOR_2 100%);
```

### Logo

Para agregar tu logo, añade en el `<div class="logo">`:

```html
<img src="tu-logo.png" alt="Educambio" style="max-width: 200px;">
```

### Textos

Todos los textos están en español y puedes modificarlos directamente en el HTML.

## 📊 Ejemplo de Flujo Completo

### Semana 1:
1. Configuras el sistema y lo despliegas
2. Generas enlaces para 10 voluntarios
3. Los voluntarios comparten sus enlaces

### Semana 2:
1. Se registran 50 emails a través de la landing page
2. 42 de esas personas completan su donación en suscripciones.co

### Proceso de Matching:
```bash
# 1. Exportas donaciones
# (descargas donaciones.csv desde suscripciones.co)

# 2. Ejecutas el matcher
python matcher.py donaciones.csv

# 3. Obtienes los resultados
# ✅ 42 matches encontrados
# 📊 MARIA: 15 donaciones
# 📊 JUAN123: 12 donaciones
# etc.
```

## 🔧 Troubleshooting

### Problema: "No se guardan los datos"

**Solución 1:** Verifica que el backend esté corriendo:
```bash
curl http://localhost:3000/health
```

**Solución 2:** Revisa la consola del navegador (F12) para ver errores

**Solución 3:** Verifica CORS si el frontend y backend están en diferentes dominios

### Problema: "El matcher no encuentra matches"

**Solución 1:** Verifica el nombre de la columna de email:
```bash
python matcher.py donaciones.csv --email-column NOMBRE_CORRECTO
```

**Solución 2:** Verifica que los emails estén en minúsculas y sin espacios

**Solución 3:** Revisa que el archivo `voluntarios_tracking.json` exista y tenga datos

### Problema: "CORS Error"

Si ves errores de CORS en la consola:

1. Verifica que el backend tenga CORS habilitado (ya está en el código)
2. Si usas un dominio diferente, actualiza la configuración CORS

## 📚 Documentación

### 🎯 Guías de Implementación:
- **[START_HERE_PYTHON_NEON.txt](START_HERE_PYTHON_NEON.txt)** - Comandos rápidos (EMPIEZA AQUÍ)
- **[GUIA_PYTHON_NEON.md](GUIA_PYTHON_NEON.md)** - Guía completa paso a paso
- **[GIT_SETUP.md](GIT_SETUP.md)** - Subir código a GitHub
- **[DEPLOY_RENDER.md](DEPLOY_RENDER.md)** - Desplegar en producción
- **[CONFIG_NEON.txt](CONFIG_NEON.txt)** - Configurar base de datos Neon
- **[PRUEBA_LOCAL_PASO_A_PASO.txt](PRUEBA_LOCAL_PASO_A_PASO.txt)** - Probar localmente

### 📁 Archivos del Sistema:
- **`backend-neon.py`** - Backend con PostgreSQL (Neon)
- **`index.html`** - Formulario para Webflow (embedded code)
- **`generar-enlaces.html`** - Herramienta para generar enlaces (uso local)
- **`matcher.py`** - Script para matching de donaciones
- **`requirements.txt`** - Dependencias de Python
- **`ejemplo_donaciones_suscripciones.csv`** - Ejemplo con formato real de suscripciones.co

## ❓ Preguntas Frecuentes

### ¿Para qué es generar-enlaces.html?
Es una herramienta administrativa que usas LOCALMENTE para crear los enlaces únicos de cada voluntario. NO va en Webflow.

### ¿Qué archivo va en Webflow?
Solo `index.html` va en Webflow como embedded code. Este es el formulario que ven los donantes.

### ¿Necesito acceso a suscripciones.co?
NO. Solo necesitas poder exportar donaciones periódicamente (función que tienen todas las plataformas).

### ¿Cuál backend debo usar?
- **Neon (PostgreSQL)**: Recomendado para producción, escalable, gratuito hasta 10GB
- **Simple (JSON)**: Para pruebas locales, más fácil de configurar
- **Node.js**: Si prefieres JavaScript sobre Python

## 📞 Soporte

Si tienes problemas:

1. Lee la documentación apropiada en la sección [Documentación Adicional](#documentación-adicional)
2. Revisa la consola del navegador (F12)
3. Revisa los logs del backend
4. Verifica que todas las URLs estén correctamente configuradas

## 📄 Licencia

Este proyecto es de código abierto para uso de Educambio.

---

**¡Buena suerte con el tracking de voluntarios! 💚**

