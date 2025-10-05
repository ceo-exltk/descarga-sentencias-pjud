# 🔧 Guía Técnica del Sistema de Descarga de Sentencias

## 📋 Arquitectura del Sistema

### **Componentes Principales**

1. **Sistema de Workers Paralelos**
   - `universal_sentencias_worker.py`: Worker base para todos los tribunales
   - `enhanced_text_worker_correcto.py`: Worker mejorado con extracción de roles
   - `descarga_especifica_100_workers.py`: Sistema de alta velocidad (100 workers)

2. **Sistema de Migración**
   - `migrate_sentencias_final.py`: Migración principal a Supabase
   - `migrate_sentencias_corrected.py`: Migración con correcciones

3. **Sistema de Monitoreo**
   - `monitor_descarga_universal.py`: Dashboard en tiempo real
   - `verificar_progreso.py`: Verificación de progreso

## 🚀 Flujo de Ejecución

### **1. Descarga Universal**
```bash
python3 scripts/descarga/descarga_universal_completa.py
```

**Características:**
- 7 tribunales procesados secuencialmente
- 50 workers por tribunal (350 workers total)
- Pausa de 30 segundos entre tribunales
- Rate limiting automático

### **2. Descarga Específica**
```bash
python3 scripts/descarga/descarga_especifica_100_workers.py
```

**Características:**
- 100 workers simultáneos
- Máxima velocidad de descarga
- Riesgo de bloqueo del servidor
- Ideal para rangos específicos

### **3. Migración a Supabase**
```bash
python3 scripts/migracion/migrate_sentencias_final.py
```

**Características:**
- Procesamiento en lotes de 50 sentencias
- Extracción automática de metadatos
- Validación de datos
- Inserción optimizada

## ⚙️ Configuración Avanzada

### **Parámetros de Workers**

```json
{
  "max_workers_por_tribunal": 50,
  "delay_between_requests": 2.0,
  "delay_between_workers": 0.5,
  "delay_between_pages": 5.0,
  "timeout_requests_segundos": 30,
  "retry_attempts": 3
}
```

### **Rate Limiting**

```json
{
  "max_requests_per_minute": 20,
  "backoff_exponential": true,
  "delay_on_error": 30,
  "max_retries": 3
}
```

### **Configuración de Supabase**

```json
{
  "url": "https://wluachczgiyrmrhdpcue.supabase.co",
  "tabla_sentencias": "sentencias",
  "batch_size": 50
}
```

## 🛠️ Desarrollo y Mantenimiento

### **Estructura de Archivos**

```
scripts/
├── descarga/           # Scripts de descarga
├── migracion/          # Scripts de migración
└── monitoreo/          # Scripts de monitoreo

config/                 # Archivos de configuración
docs/                   # Documentación
output/                 # Datos descargados
logs/                   # Archivos de log
```

### **Logs del Sistema**

- `descarga_universal_completa.log`: Log principal de descarga
- `universal_sentencias_worker.log`: Log de workers
- `migrate_sentencias_final.log`: Log de migración

### **Monitoreo en Tiempo Real**

```bash
# Dashboard interactivo
python3 scripts/monitoreo/monitor_descarga_universal.py

# Verificación de progreso
python3 scripts/monitoreo/verificar_progreso.py
```

## 🔧 Solución de Problemas

### **Error HTTP 419 (Bloqueo del Servidor)**

**Síntomas:**
- Todas las peticiones devuelven HTTP 419
- Workers fallan inmediatamente
- 0 sentencias descargadas

**Soluciones:**
1. **Esperar 24-48 horas** para que se libere el bloqueo
2. **Usar configuración ultra-conservadora**:
   - 1-2 workers máximo
   - 30+ segundos entre peticiones
   - Solo 1-2 páginas por sesión
3. **Cambiar IP** usando VPN o proxy

### **Error de Memoria**

**Síntomas:**
- Proceso se cuelga
- Uso excesivo de RAM
- Workers fallan por memoria

**Soluciones:**
1. **Reducir workers**:
   ```json
   "max_workers_por_tribunal": 25
   ```
2. **Aumentar delays**:
   ```json
   "delay_between_requests": 5.0
   ```
3. **Procesar en lotes más pequeños**

### **Error de Conexión**

**Síntomas:**
- Timeouts frecuentes
- Conexiones rechazadas
- Workers fallan intermitentemente

**Soluciones:**
1. **Aumentar timeout**:
   ```json
   "timeout_requests_segundos": 60
   ```
2. **Implementar backoff exponencial**
3. **Verificar conectividad de red**

## 📊 Métricas y Rendimiento

### **Velocidad de Descarga**

| Configuración | Workers | Velocidad | Tiempo Estimado |
|---------------|---------|-----------|-----------------|
| **Ultra-Conservadora** | 1-2 | 10-20 sentencias/min | 20-40 horas |
| **Conservadora** | 10-20 | 50-100 sentencias/min | 4-8 horas |
| **Moderada** | 50 | 100-200 sentencias/min | 2-4 horas |
| **Agresiva** | 100+ | 500+ sentencias/min | 30-60 minutos |

### **Tasa de Éxito**

- **Sentencias con texto completo**: 60-80%
- **Sentencias con roles**: 40-60%
- **Errores de conexión**: <5% (configuración conservadora)

### **Recursos del Sistema**

- **RAM**: 4-8 GB recomendados
- **CPU**: 4+ cores recomendados
- **Disco**: 50+ GB para almacenamiento
- **Red**: Conexión estable a internet

## 🔒 Consideraciones de Seguridad

### **Rate Limiting**

- Respetar límites del servidor
- Implementar pausas entre peticiones
- Usar backoff exponencial en errores

### **Headers HTTP**

```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'X-Requested-With': 'XMLHttpRequest'
}
```

### **Logging y Trazabilidad**

- Logs detallados de cada operación
- Trazabilidad de errores
- Monitoreo de rendimiento

## 🚀 Optimizaciones Futuras

### **Mejoras Planificadas**

1. **Sistema de Checkpoint**: Recuperación automática de descargas interrumpidas
2. **Distribución de Carga**: Múltiples IPs/proxies para evitar bloqueos
3. **Cache Inteligente**: Evitar re-descargas de datos ya procesados
4. **API Rate Limiting**: Implementación de límites más sofisticados

### **Escalabilidad**

- **Horizontal**: Múltiples máquinas trabajando en paralelo
- **Vertical**: Optimización de recursos por máquina
- **Distribuida**: Sistema de colas para procesamiento asíncrono

## 📞 Soporte Técnico

### **Logs Importantes**

```bash
# Ver logs en tiempo real
tail -f logs/descarga_universal_completa.log

# Verificar errores
grep "ERROR" logs/*.log

# Monitorear progreso
python3 scripts/monitoreo/verificar_progreso.py
```

### **Debugging**

```bash
# Modo debug
export DEBUG=1
python3 scripts/descarga/descarga_universal_completa.py

# Verificar configuración
python3 config/configurar_descarga_universal.py
```

---

**Esta guía técnica proporciona toda la información necesaria para desarrollar, mantener y optimizar el sistema de descarga de sentencias.**
