# 🛠️ Guía de Troubleshooting - Descarga de Sentencias

## 🚨 **Problemas Comunes y Soluciones**

### **1. Errores de Configuración**

#### **❌ Error: "No se puede disparar workflow"**

**Síntomas**:
```
❌ GitHub CLI no está instalado
❌ No se encontró repositorio git
❌ Error ejecutando workflow: authentication required
```

**Causas**:
- GitHub CLI no instalado
- No autenticado con GitHub
- Token de GitHub expirado o inválido

**Soluciones**:

1. **Instalar GitHub CLI**:
   ```bash
   # macOS
   brew install gh
   
   # Ubuntu/Debian
   sudo apt install gh
   
   # Windows
   winget install GitHub.cli
   ```

2. **Autenticar con GitHub**:
   ```bash
   gh auth login
   # Seleccionar: GitHub.com
   # Seleccionar: HTTPS
   # Seleccionar: Login with a web browser
   ```

3. **Verificar autenticación**:
   ```bash
   gh auth status
   ```

#### **❌ Error: "Workflow not found"**

**Síntomas**:
```
❌ No se encontró el workflow de Supabase
❌ Workflow 'descargar-sentencias-supabase.yml' not found
```

**Causas**:
- Workflow no está en el repositorio
- Archivo no sincronizado con GitHub
- Nombre del workflow incorrecto

**Soluciones**:

1. **Verificar que el workflow existe**:
   ```bash
   ls -la .github/workflows/
   ```

2. **Sincronizar con GitHub**:
   ```bash
   git add .github/workflows/
   git commit -m "➕ Agregar workflows"
   git push origin main
   ```

3. **Verificar en GitHub**:
   - Ir a Actions tab
   - Verificar que aparezcan los workflows

### **2. Errores de Supabase**

#### **❌ Error: "Supabase connection failed"**

**Síntomas**:
```
❌ Archivo de sentencias no encontrado
❌ Error: Invalid API key
❌ Error: Invalid URL
```

**Causas**:
- Secretos de GitHub mal configurados
- URL o API key incorrectos
- Supabase no disponible

**Soluciones**:

1. **Verificar secretos en GitHub**:
   - Ir a Settings → Secrets and variables → Actions
   - Verificar que existan:
     - `SUPABASE_URL`
     - `SUPABASE_ANON_KEY`

2. **Verificar valores de secretos**:
   ```bash
   # Verificar URL (debe empezar con https://)
   echo "URL debe ser: https://wluachczgiyrmrhdpcue.supabase.co"
   
   # Verificar API key (debe ser JWT válido)
   echo "API key debe empezar con: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
   ```

3. **Probar conexión localmente**:
   ```bash
   python3 cargar_a_supabase.py test.json https://wluachczgiyrmrhdpcue.supabase.co eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

#### **❌ Error: "Archivo de sentencias no encontrado"**

**Síntomas**:
```
❌ Archivo de sentencias no encontrado
❌ FileNotFoundError: [Errno 2] No such file or directory
```

**Causas**:
- La descarga falló
- No hay sentencias para esa fecha
- Error en el procesamiento

**Soluciones**:

1. **Verificar que la descarga funcionó**:
   ```bash
   # Verificar archivos generados
   ls -la output/descarga_api/
   ```

2. **Verificar logs de descarga**:
   - Ir a Actions → Ver logs del step "Descargar sentencias del día"
   - Buscar errores específicos

3. **Probar con fecha diferente**:
   - Usar fecha que sepas que tiene sentencias
   - Ejemplo: 2024-01-15

### **3. Errores de Descarga**

#### **❌ Error: "Rate limit exceeded"**

**Síntomas**:
```
❌ HTTP 429: Too Many Requests
❌ Rate limit exceeded
```

**Causas**:
- Demasiadas solicitudes a la API del PJUD
- Múltiples ejecuciones simultáneas
- API temporalmente saturada

**Soluciones**:

1. **El sistema tiene retry automático** - esperar
2. **Verificar que no hay ejecuciones duplicadas**:
   - Ir a Actions
   - Verificar que solo hay una ejecución en curso

3. **Si persiste, esperar y reintentar**:
   - Esperar 10-15 minutos
   - Ejecutar manualmente

#### **❌ Error: "Timeout"**

**Síntomas**:
```
❌ Timeout after 60 minutes
❌ Job timed out
```

**Causas**:
- Descarga muy lenta
- Muchas sentencias para procesar
- Problemas de red

**Soluciones**:

1. **El sistema tiene retry automático**
2. **Si persiste, dividir la descarga**:
   - Ejecutar para fechas más pequeñas
   - Ejemplo: 2024-01-15 a 2024-01-15

3. **Verificar logs para identificar el problema**:
   - Ver en qué step se detiene
   - Identificar si es descarga o procesamiento

### **4. Errores de Procesamiento**

#### **❌ Error: "JSON decode error"**

**Síntomas**:
```
❌ JSONDecodeError: Expecting value
❌ Invalid JSON format
```

**Causas**:
- Archivo JSON corrupto
- Respuesta de API inválida
- Error en el procesamiento

**Soluciones**:

1. **Verificar archivos JSON**:
   ```bash
   # Verificar que los archivos JSON son válidos
   python3 -m json.tool output/descarga_api/sentencias_consolidadas.json
   ```

2. **Reintentar la descarga**:
   - Ejecutar manualmente para la misma fecha
   - El sistema regenerará los archivos

#### **❌ Error: "Permission denied"**

**Síntomas**:
```
❌ Permission denied: 'output/descarga_api'
❌ Cannot create directory
```

**Causas**:
- Permisos de archivos incorrectos
- Directorio no se puede crear

**Soluciones**:

1. **Verificar permisos**:
   ```bash
   ls -la output/
   chmod -R 755 output/
   ```

2. **Crear directorio manualmente**:
   ```bash
   mkdir -p output/descarga_api
   chmod 755 output/descarga_api
   ```

### **5. Errores de GitHub Actions**

#### **❌ Error: "Actions not enabled"**

**Síntomas**:
```
❌ Actions are not enabled for this repository
❌ Workflow cannot be triggered
```

**Causas**:
- GitHub Actions deshabilitado
- Repositorio privado sin permisos

**Soluciones**:

1. **Habilitar Actions**:
   - Ir a Settings → Actions → General
   - Seleccionar "Allow all actions and reusable workflows"
   - Click "Save"

2. **Verificar permisos del repositorio**:
   - Si es privado, verificar que tienes permisos de admin

#### **❌ Error: "Workflow disabled"**

**Síntomas**:
```
❌ Workflow is disabled
❌ Cannot run disabled workflow
```

**Causas**:
- Workflow deshabilitado manualmente
- Cambios en configuración

**Soluciones**:

1. **Habilitar workflow**:
   - Ir a Actions → "Descarga Diaria Automática"
   - Click "Enable workflow"

2. **Verificar configuración**:
   - Verificar que el archivo .yml esté correcto
   - Verificar sintaxis YAML

## 🔍 **Diagnóstico Avanzado**

### **Verificar Estado del Sistema**

```bash
# Verificar configuración completa
python3 verificar_configuracion.py

# Verificar workflows disponibles
gh workflow list

# Verificar ejecuciones recientes
gh run list --limit 10

# Ver logs de ejecución específica
gh run view [RUN_ID]
```

### **Logs Detallados**

1. **GitHub Actions Logs**:
   - Ir a Actions → Seleccionar ejecución
   - Click en cada step para ver logs detallados

2. **Supabase Logs**:
   - Ir a Supabase Dashboard
   - Logs → API Logs
   - Filtrar por tabla "sentencias"

3. **Logs Locales**:
   ```bash
   # Si ejecutas localmente
   python3 descargar_sentencias_api.py 2024-01-15 2024-01-15 2>&1 | tee descarga.log
   ```

### **Monitoreo en Tiempo Real**

```bash
# Monitorear ejecuciones
watch -n 30 "gh run list --limit 5"

# Ver estado de workflows
gh workflow list
```

## 🚨 **Escalación de Problemas**

### **Si Nada Funciona**

1. **Verificar estado de servicios**:
   - GitHub: https://www.githubstatus.com/
   - Supabase: https://status.supabase.com/
   - PJUD API: Probar manualmente

2. **Ejecutar diagnóstico completo**:
   ```bash
   python3 verificar_configuracion.py
   gh auth status
   gh run list --limit 5
   ```

3. **Contactar soporte**:
   - GitHub: Issues en el repositorio
   - Supabase: Support en dashboard

### **Recuperación de Datos**

Si el sistema falla y necesitas recuperar datos:

1. **Descargar artifacts**:
   - Ir a Actions → Ejecución exitosa
   - Descargar artifacts
   - Descomprimir y usar archivos JSON

2. **Cargar manualmente a Supabase**:
   ```bash
   python3 cargar_a_supabase.py archivo.json URL KEY
   ```

## 📞 **Contacto y Soporte**

- **GitHub Issues**: Para reportar bugs
- **Supabase Support**: Para problemas de base de datos
- **Logs**: Siempre incluir logs completos al reportar problemas

---

**¡Sistema robusto con recuperación automática! 🚀**
