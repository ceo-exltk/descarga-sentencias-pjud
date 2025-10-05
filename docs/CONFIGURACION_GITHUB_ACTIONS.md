# 🔧 Configuración de GitHub Actions

## 📋 Pasos para Configurar el Sistema Cloud

### **1. Configurar Secretos del Repositorio**

Ve a tu repositorio en GitHub: `https://github.com/ceo-exltk/descarga-sentencias-pjud`

1. **Ir a Settings → Secrets and variables → Actions**
2. **Agregar los siguientes secretos:**

```
SUPABASE_URL = https://wluachczgiyrmrhdpcue.supabase.co
SUPABASE_ANON_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndsdWFjaGN6Z2l5cm1yaGRwY3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5MjA1NDcsImV4cCI6MjA3MjQ5NjU0N30.gXSqEYy_LFp951EnBhFxU_7RSf5VbJXRc2GlLn7OB7I
```

### **2. Crear Personal Access Token**

1. **Ir a GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**
2. **Generar nuevo token con permisos:**
   - `repo` (acceso completo a repositorios)
   - `workflow` (actualizar workflows)
   - `actions` (leer y escribir en Actions)

3. **Copiar el token generado**

### **3. Configurar Variables de Entorno Locales**

```bash
# Configurar token de GitHub
export GITHUB_TOKEN="tu_token_aqui"

# Configurar repositorio
export GITHUB_REPO="ceo-exltk/descarga-sentencias-pjud"
```

### **4. Agregar Workflow de GitHub Actions**

Una vez configurados los secretos, agregar el workflow:

```bash
# Restaurar el workflow
git checkout HEAD~1 -- .github/workflows/descarga-incremental.yml
git add .github/workflows/descarga-incremental.yml
git commit -m "➕ Agregar workflow de GitHub Actions"
git push origin main
```

### **5. Probar el Sistema**

```bash
# Ejecutar orquestador
python3 scripts/cloud/orquestador_cloud.py
```

## 🚀 Funcionalidades del Sistema

### **Descarga Incremental**
- **Por fecha**: Descargar sentencias de un período específico
- **Por tribunal**: Seleccionar tribunal específico
- **Páginas limitadas**: Control de volumen de descarga

### **Descarga Histórica**
- **Un tribunal**: Descarga completa de un tribunal
- **Todos los tribunales**: Descarga masiva histórica
- **Carga automática**: Directa a Supabase

### **Monitoreo**
- **Estado de workflows**: Ver progreso en tiempo real
- **Logs detallados**: Seguimiento completo
- **Notificaciones**: Alertas de errores

## 📊 Parámetros de Configuración

### **Descarga Incremental**
```yaml
tribunal_type: Corte_Suprema
fecha_desde: 2024-01-01
fecha_hasta: 2024-12-31
paginas_maximas: 10
workers_paralelos: 3
```

### **Descarga Histórica**
```yaml
tribunal_type: Corte_Suprema
fecha_desde: 2000-01-01
fecha_hasta: 2024-12-31
paginas_maximas: 100
workers_paralelos: 5
```

## 🔍 Monitoreo y Logs

### **Ver Workflows en GitHub**
1. Ir a tu repositorio
2. **Actions tab**
3. Ver ejecuciones en tiempo real

### **Logs Locales**
```bash
# Ver logs del orquestador
tail -f logs/orquestador.log

# Ver logs de GitHub Actions
gh run list
gh run view [run-id]
```

## 🛠️ Solución de Problemas

### **Error: "No se puede disparar workflow"**
- Verificar que `GITHUB_TOKEN` tenga permisos `workflow`
- Verificar que el repositorio tenga Actions habilitado

### **Error: "Supabase connection failed"**
- Verificar que los secretos estén configurados correctamente
- Verificar que la URL y key de Supabase sean correctas

### **Error: "Workflow not found"**
- Verificar que el archivo `.github/workflows/descarga-incremental.yml` exista
- Hacer push del workflow al repositorio

## 📈 Escalabilidad

### **Límites de GitHub Actions**
- **Gratuito**: 2,000 minutos/mes
- **Máximo por job**: 6 horas
- **Workflows paralelos**: Hasta 20

### **Optimizaciones**
- **Descarga por lotes**: Procesar en chunks pequeños
- **Scheduling inteligente**: Distribuir carga en el tiempo
- **Filtros de fecha**: Evitar duplicados

## 🎯 Próximos Pasos

1. **Configurar secretos** en GitHub
2. **Probar descarga incremental** con pocas páginas
3. **Verificar carga en Supabase**
4. **Programar descarga histórica** por tribunal
5. **Monitorear rendimiento** y ajustar parámetros

---

**¡Sistema listo para descarga masiva con IPs dinámicas! 🚀**
