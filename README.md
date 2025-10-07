# 🏛️ Descarga Automática de Sentencias PJUD

Sistema automatizado para descargar sentencias del Poder Judicial de Chile y cargarlas automáticamente a Supabase usando GitHub Actions.

## 🚀 **Características Principales**

- ✅ **Descarga automática diaria** a las 6:00 AM (UTC-3)
- ✅ **Carga automática a Supabase** sin intervención manual
- ✅ **Sistema de retry** en caso de errores
- ✅ **Descarga manual** para fechas específicas
- ✅ **Monitoreo completo** con logs detallados
- ✅ **Artifacts automáticos** con resultados

## 📋 **Configuración Inicial**

### **1. Configurar Secretos de GitHub**

Ve a tu repositorio en GitHub: `https://github.com/ceo-exltk/descarga-sentencias-pjud`

1. **Settings** → **Secrets and variables** → **Actions**
2. **Agregar los siguientes secretos:**

```
SUPABASE_URL = https://wluachczgiyrmrhdpcue.supabase.co
SUPABASE_ANON_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndsdWFjaGN6Z2l5cm1yaGRwY3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5MjA1NDcsImV4cCI6MjA3MjQ5NjU0N30.gXSqEYy_LFp951EnBhFxU_7RSf5VbJXRc2GlLn7OB7I
```

### **2. Verificar Configuración**

```bash
# Verificar que todo esté configurado correctamente
python3 verificar_configuracion.py
```

## 🎯 **Cómo Usar el Sistema**

### **Opción A: Ejecución Automática (Recomendada)**

El sistema se ejecuta **automáticamente todos los días a las 6:00 AM (UTC-3)** descargando las sentencias del día anterior.

**No necesitas hacer nada** - el sistema funciona solo.

### **Opción B: Ejecución Manual**

#### **1. Desde GitHub (Recomendado)**

1. Ve a **Actions** en tu repositorio
2. Selecciona **"Descarga Diaria Automática"**
3. Click **"Run workflow"**
4. Opcionalmente ingresa una fecha específica
5. Click **"Run workflow"**

#### **2. Desde Terminal Local**

```bash
# Ejecutar para fecha específica
python3 ejecutar_workflow_supabase.py 2024-01-15

# Ejecutar para ayer (automático)
python3 ejecutar_workflow_supabase.py
```

### **Opción C: Descarga Manual (Sin Supabase)**

1. Ve a **Actions** → **"Descargar Sentencias por Día"**
2. Click **"Run workflow"**
3. Ingresa la fecha deseada
4. Click **"Run workflow"**

## 📊 **Monitoreo y Resultados**

### **Ver Progreso en Tiempo Real**

1. Ve a **Actions** en tu repositorio
2. Click en la ejecución en curso
3. Monitorea los logs paso a paso

### **Descargar Resultados**

1. Ve a la ejecución completada
2. En la sección **"Artifacts"** descarga el archivo
3. Descomprime para obtener:
   - `sentencias_consolidadas.json` - Archivo completo
   - `sentencias_para_supabase.json` - Solo para Supabase
   - `estadisticas_descarga.json` - Estadísticas
   - `descarga_resumen.txt` - Resumen en texto

### **Verificar en Supabase**

Los datos se cargan automáticamente en tu base de datos Supabase. Puedes verificar en:
- **Dashboard de Supabase**: https://supabase.com/dashboard
- **Tabla**: `sentencias`

## 🔧 **Workflows Disponibles**

| Workflow | Función | Frecuencia | Supabase |
|----------|---------|------------|----------|
| **Descarga Diaria Automática** | Descarga automática diaria | Diario 6:00 AM | ✅ Sí |
| **Descargar Sentencias por Día** | Descarga manual | Manual | ❌ No |
| **Descargar y Cargar a Supabase** | Descarga + carga manual | Manual | ✅ Sí |

## 🛠️ **Troubleshooting**

### **❌ Error: "No se puede disparar workflow"**

**Causa**: GitHub CLI no configurado o sin permisos

**Solución**:
```bash
# Instalar GitHub CLI
brew install gh  # macOS
# o
sudo apt install gh  # Ubuntu

# Autenticar
gh auth login
```

### **❌ Error: "Supabase connection failed"**

**Causa**: Secretos de GitHub mal configurados

**Solución**:
1. Verificar que los secretos estén en **Settings** → **Secrets and variables** → **Actions**
2. Verificar que los nombres sean exactos: `SUPABASE_URL` y `SUPABASE_ANON_KEY`
3. Verificar que los valores sean correctos

### **❌ Error: "Workflow not found"**

**Causa**: Workflow no está en el repositorio

**Solución**:
```bash
# Hacer push de los workflows
git add .github/workflows/
git commit -m "➕ Agregar workflows"
git push origin main
```

### **❌ Error: "Archivo de sentencias no encontrado"**

**Causa**: La descarga falló o no hay sentencias para esa fecha

**Solución**:
1. Verificar que la fecha sea válida
2. Verificar que haya sentencias publicadas ese día
3. Revisar los logs de la descarga

### **❌ Error: "Timeout"**

**Causa**: La descarga toma más de 1 hora

**Solución**:
1. El sistema tiene retry automático
2. Si persiste, ejecutar manualmente para esa fecha
3. Considerar dividir en fechas más pequeñas

### **❌ Error: "Rate limit exceeded"**

**Causa**: Demasiadas solicitudes a la API

**Solución**:
1. El sistema tiene retry automático
2. Esperar unos minutos y reintentar
3. Verificar que no haya múltiples ejecuciones simultáneas

## 📈 **Límites y Consideraciones**

### **Límites de GitHub Actions**
- **Gratuito**: 2,000 minutos/mes
- **Máximo por job**: 6 horas
- **Workflows paralelos**: Hasta 20

### **Optimizaciones Implementadas**
- **Timeout de 1 hora** por job
- **Retry automático** en caso de fallo
- **Artifacts con retención de 7 días**
- **Descarga incremental** por fecha

## 🔄 **Mantenimiento**

### **Verificar Estado del Sistema**

```bash
# Verificar configuración
python3 verificar_configuracion.py

# Ver logs de GitHub Actions
gh run list
gh run view [run-id]
```

### **Actualizar Secretos**

Si cambias las credenciales de Supabase:

1. Actualizar en **GitHub Secrets**
2. El sistema usará automáticamente los nuevos valores

### **Pausar Ejecución Automática**

Para pausar la ejecución diaria:

1. Ve a **Actions** → **"Descarga Diaria Automática"**
2. Click en **"..."** → **"Disable workflow"**

Para reactivar:

1. Ve a **Actions** → **"Descarga Diaria Automática"**
2. Click **"Enable workflow"**

## 📞 **Soporte**

### **Logs Detallados**
- **GitHub Actions**: Logs completos de cada ejecución
- **Supabase**: Logs de carga en el dashboard
- **Artifacts**: Archivos de resultado descargables

### **Monitoreo**
- **Estado**: Ver en Actions tab
- **Errores**: Notificaciones automáticas
- **Resultados**: Artifacts con datos

## 🎯 **Próximos Pasos**

1. ✅ **Configurar secretos** en GitHub
2. ✅ **Probar ejecución manual** con fecha específica
3. ✅ **Verificar carga en Supabase**
4. ✅ **Monitorear ejecución automática** diaria
5. ✅ **Ajustar parámetros** según necesidades

---

**¡Sistema listo para descarga automática diaria! 🚀**

*El sistema descargará automáticamente las sentencias del día anterior todos los días a las 6:00 AM y las cargará a Supabase sin intervención manual.*