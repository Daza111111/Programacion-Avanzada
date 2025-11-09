# Configuración de GitHub Pages para tu Aplicación React

## ✅ Cambios Realizados

He corregido la configuración de GitHub Actions para que tu aplicación React se despliegue correctamente en GitHub Pages.

### Archivos Modificados:

1. **`.github/workflows/deploy-react.yml`** (NUEVO)
   - Workflow correcto para construir y desplegar React
   - Instala dependencias con Yarn
   - Construye la aplicación
   - Despliega la carpeta `build` a GitHub Pages

2. **`frontend/package.json`**
   - Agregado: `"homepage": "https://daza111111.github.io/Programacion-Avanzada"`

3. **`frontend/src/App.js`**
   - Agregado `basename="/Programacion-Avanzada"` al BrowserRouter para rutas correctas (solo en producción)

4. **`frontend/public/.nojekyll`** (NUEVO)
   - Evita que GitHub Pages procese la app como Jekyll

5. **Eliminados workflows antiguos:**
   - ❌ `jekyll-gh-pages.yml`
   - ❌ `static.yml`

---

## 🚀 Pasos para Habilitar GitHub Pages

### 1. Habilitar GitHub Pages en tu Repositorio

Ve a tu repositorio en GitHub:
```
https://github.com/Daza111111/Programacion-Avanzada
```

Luego:

1. **Settings** (Configuración) → **Pages** (en el menú lateral izquierdo)

2. En **"Source"** (Fuente), selecciona:
   - **Source:** `GitHub Actions`

3. ¡Listo! No necesitas seleccionar ninguna rama manualmente.

### 2. Hacer Push de los Cambios

Haz commit y push de todos estos cambios a tu repositorio:

```bash
git add .
git commit -m "Configurar GitHub Pages para React"
git push origin main
```

### 3. Ver el Progreso del Despliegue

1. Ve a la pestaña **Actions** en tu repositorio:
   ```
   https://github.com/Daza111111/Programacion-Avanzada/actions
   ```

2. Verás el workflow "Deploy React App to GitHub Pages" ejecutándose

3. Espera a que termine (toma 2-3 minutos)

4. ✅ Cuando veas una marca verde, tu sitio estará listo

### 4. Acceder a tu Aplicación

Una vez desplegado, tu aplicación estará disponible en:

**🌐 https://daza111111.github.io/Programacion-Avanzada/**

---

## ⚠️ Nota Importante sobre el Backend

Tu aplicación React usa una API backend (FastAPI). Para que funcione en GitHub Pages, necesitas:

**Opción 1: Desplegar el Backend por Separado**
- Desplegar el backend en un servicio como:
  - Render (https://render.com)
  - Railway (https://railway.app)
  - Heroku
  - DigitalOcean

- Luego actualizar `REACT_APP_BACKEND_URL` en el código para apuntar a tu backend desplegado

**Opción 2: Usar GitHub Pages solo para Demo**
- La aplicación se verá pero no funcionarán las funciones que requieren backend
- Es útil para mostrar el diseño y la interfaz

---

## 🔧 Solución de Problemas

### Error de cache en GitHub Actions
- **Resuelto**: El workflow ahora usa un sistema de cache manual optimizado
- Si ves errores sobre `yarn.lock`, asegúrate de que el archivo existe en `frontend/yarn.lock`

### La página muestra una pantalla en blanco
- Verifica que el workflow se haya ejecutado sin errores
- Revisa la consola del navegador (F12) para ver errores
- Asegúrate de que GitHub Pages esté habilitado en Settings → Pages

### Los estilos no se cargan
- El archivo `.nojekyll` debería resolver esto
- Verifica que el `homepage` en package.json sea correcto

### Las rutas no funcionan (Error 404)
- El `basename="/axx"` en BrowserRouter debería resolver esto
- Considera usar HashRouter si persisten los problemas

---

## 📝 Comandos Útiles

### Construir localmente para probar:
```bash
cd frontend
yarn build
```

### Ver la build localmente:
```bash
cd frontend/build
npx serve -s .
```

---

¿Necesitas ayuda adicional? ¡Pregunta! 🚀
