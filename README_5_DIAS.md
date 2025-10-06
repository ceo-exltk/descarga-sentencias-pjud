# 🌍 Descarga Universo Completo - 5 Días

Sistema robusto para descargar **4,115,881 sentencias** del Poder Judicial de Chile durante 5 días de forma **continua y automática** (24/7 sin pausas).

## 🚀 **Inicio Rápido**

```bash
# Opción 1: Script automático
./ejecutar_5_dias.sh

# Opción 2: Python directo
python3 iniciar_descarga_5_dias.py
```

## 📊 **Estadísticas del Universo**

| Tribunal | Total Sentencias | Prioridad | Tiempo Estimado |
|----------|------------------|-----------|-----------------|
| **Corte de Apelaciones** | 1,510,429 | 🔴 Alta | 2 días |
| **Civiles** | 849,956 | 🟡 Media | 1.5 días |
| **Penales** | 862,269 | 🟡 Media | 1.5 días |
| **Familia** | 371,320 | 🟢 Baja | 0.5 días |
| **Laborales** | 233,904 | 🟢 Baja | 0.5 días |
| **Corte Suprema** | 261,871 | 🟢 Baja | 0.5 días |
| **Cobranza** | 26,132 | 🟢 Baja | 0.1 días |

**Total**: 4,115,881 sentencias en 5 días

## ⚙️ **Características del Sistema**

### **🛡️ Seguridad y Estabilidad**
- ✅ **Rate limiting** inteligente (0.5s entre requests)
- ✅ **Retry automático** en caso de errores
- ✅ **Ejecución continua** 24/7 sin pausas nocturnas
- ✅ **Recuperación de estado** automática
- ✅ **Workers limitados** para evitar bloqueos

### **📊 Monitoreo en Tiempo Real**
- ✅ **Dashboard** con progreso detallado
- ✅ **Logs** completos de cada operación
- ✅ **Estado persistente** que se guarda automáticamente
- ✅ **Métricas** de rendimiento y errores

### **🔄 Recuperación Automática**
- ✅ **Continuar** descargas interrumpidas
- ✅ **Reanudar** desde el último batch
- ✅ **Estado guardado** cada 10 batches
- ✅ **Recuperación** por tribunal individual

## 🎯 **Opciones de Ejecución**

### **1. 🚀 Descarga Completa (Recomendada)**
```bash
python3 iniciar_descarga_5_dias.py
# Seleccionar opción 1
```

**Características**:
- Ejecuta durante 5 días completos CONTINUOS
- Sin pausas nocturnas - ejecución 24/7
- Recuperación automática de errores
- Monitoreo continuo

### **2. 📊 Solo Monitoreo**
```bash
python3 iniciar_descarga_5_dias.py
# Seleccionar opción 2
```

**Para ver el progreso** sin ejecutar descarga.

### **3. 🔄 Continuar Descarga Interrumpida**
```bash
python3 iniciar_descarga_5_dias.py
# Seleccionar opción 3
```

**Para reanudar** una descarga que se detuvo.

### **4. 🧪 Prueba con Tribunal Pequeño**
```bash
python3 iniciar_descarga_5_dias.py
# Seleccionar opción 4
```

**Prueba** con Cobranza (~26,000 sentencias, 30 min).

## 📁 **Estructura de Archivos**

```
descarga_sentencias/
├── iniciar_descarga_5_dias.py      # Script principal
├── descarga_universo_completo.py   # Motor de descarga
├── scheduler_5_dias.py             # Scheduler inteligente
├── monitor_descarga_universo.py    # Monitor en tiempo real
├── recuperar_descarga.py           # Recuperación de errores
├── config_descarga_5_dias.json     # Configuración
├── ejecutar_5_dias.sh              # Script de inicio
└── output/universo_completo/       # Resultados
    ├── logs/                       # Logs detallados
    ├── estado_descarga.json        # Estado persistente
    ├── scheduler_estado.json       # Estado del scheduler
    └── [Tribunales]/               # Archivos por tribunal
        ├── batch_000001.json
        ├── batch_000002.json
        └── ...
```

## ⏰ **Horarios de Ejecución**

### **Ejecución Continua**: 24/7 durante 5 días
- **Descarga activa** las 24 horas del día
- **Pausas mínimas** solo entre tribunales (1 minuto)
- **Pausas por error** de 5 minutos máximo
- **Recuperación automática** de errores

## 🔧 **Configuración Avanzada**

### **Ajustar Workers por Tribunal**
Editar `config_descarga_5_dias.json`:
```json
{
  "tribunales": {
    "Corte_de_Apelaciones": {
      "workers": 3  // Aumentar para más velocidad
    }
  }
}
```

### **Ajustar Rate Limiting**
```json
{
  "descarga": {
    "rate_limit_delay": 0.5,  // Segundos entre requests
    "batch_size": 50          // Sentencias por batch
  }
}
```

## 📊 **Monitoreo y Logs**

### **Ver Progreso en Tiempo Real**
```bash
python3 monitor_descarga_universo.py
```

### **Ver Logs Detallados**
```bash
tail -f output/universo_completo/logs/descarga_*.log
```

### **Analizar Estado**
```bash
python3 recuperar_descarga.py
# Seleccionar opción 1
```

## 🚨 **Troubleshooting**

### **❌ Error: "Rate limit exceeded"**
- El sistema tiene **retry automático**
- **Pausas inteligentes** entre requests
- **Workers limitados** para evitar bloqueos

### **❌ Error: "Connection timeout"**
- **Retry automático** con backoff exponencial
- **Pausa de 30 minutos** después de errores
- **Reanudación** desde el último batch

### **❌ Error: "Disk space"**
- **Archivos por batch** (50 sentencias cada uno)
- **Compresión** automática de logs antiguos
- **Limpieza** automática de archivos temporales

### **❌ Error: "Interrupción inesperada"**
- **Estado guardado** automáticamente
- **Recuperación** con `recuperar_descarga.py`
- **Continuar** desde donde se quedó

## 📈 **Métricas de Rendimiento**

### **Velocidad Estimada**
- **Corte de Apelaciones**: ~1,000 sentencias/hora
- **Tribunales medianos**: ~2,000 sentencias/hora  
- **Tribunales pequeños**: ~3,000 sentencias/hora

### **Tiempo Total Estimado**
- **5 días** con horario de 6 AM - 10 PM
- **Pausas nocturnas** incluidas
- **Recuperación** de errores incluida

## 🎯 **Resultados Esperados**

### **Archivos Generados**
- **~82,000 archivos JSON** (batches de 50 sentencias)
- **Logs detallados** de toda la operación
- **Estado persistente** para recuperación
- **Estadísticas** de rendimiento

### **Carga a Supabase**
- **Archivos listos** para ingesta
- **Formato normalizado** para Supabase
- **Metadatos** completos de cada sentencia

## 🚀 **Próximos Pasos**

1. **Ejecutar** el sistema con `./ejecutar_5_dias.sh`
2. **Monitorear** el progreso en tiempo real
3. **Verificar** que no haya errores críticos
4. **Dejar ejecutando** durante 5 días
5. **Recuperar** archivos al finalizar

---

**¡Sistema listo para descarga masiva de 4+ millones de sentencias! 🚀**

*El sistema está diseñado para ser robusto, seguro y recuperable. Puedes dejarlo ejecutando con confianza durante los 5 días.*
