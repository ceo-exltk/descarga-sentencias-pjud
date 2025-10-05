# 🌍 Sistema de Descarga Universal de Sentencias

## 📋 Descripción

Sistema completo para la descarga masiva de sentencias de todos los tribunales del Poder Judicial de Chile, con workers máximos y procesamiento optimizado de fechas.

## 🚀 Características Principales

- **Descarga Universal**: Todos los tribunales en un solo sistema
- **Workers Máximos**: Hasta 50 workers por tribunal (350+ workers total)
- **Procesamiento de Fechas**: Normalización y validación de fechas de sentencias
- **Monitoreo en Tiempo Real**: Dashboard de progreso en vivo
- **Configuración Flexible**: Ajuste de workers y tribunales
- **Recuperación de Errores**: Sistema robusto de reintentos

## 🏛️ Tribunales Soportados

| Tribunal | Páginas Estimadas | Workers | Descripción |
|----------|------------------|---------|-------------|
| **Corte Suprema** | 2,615 | 50 | Corte Suprema de Chile |
| **Corte de Apelaciones** | 150,989 | 50 | Cortes de Apelaciones |
| **Laborales** | 17,396 | 50 | Tribunales Laborales |
| **Penales** | 22,801 | 50 | Tribunales Penales |
| **Familia** | 11,335 | 50 | Tribunales de Familia |
| **Civiles** | 33,313 | 50 | Tribunales Civiles |
| **Cobranza** | 2,613 | 50 | Tribunales de Cobranza |

**Total**: ~240,000 páginas con 350+ workers

## 📁 Estructura de Archivos

```
descarga_sentencias/
├── universal_sentencias_worker.py      # Worker principal
├── descarga_universal_completa.py      # Script maestro
├── configurar_descarga_universal.py    # Configurador
├── monitor_descarga_universal.py       # Monitor en tiempo real
├── ejecutar_descarga_universal.sh      # Script de ejecución
└── README_DESCARGA_UNIVERSAL.md        # Esta documentación
```

## 🚀 Inicio Rápido

### **Opción 1: Ejecución Automática (Recomendada)**

```bash
./ejecutar_descarga_universal.sh
```

### **Opción 2: Ejecución Manual**

```bash
# 1. Configurar (opcional)
python3 configurar_descarga_universal.py

# 2. Ejecutar descarga
python3 descarga_universal_completa.py

# 3. Monitorear (en terminal separada)
python3 monitor_descarga_universal.py
```

## ⚙️ Configuración

### **Configuración Básica**

- **Workers por tribunal**: 50 (máximo recomendado)
- **Pausa entre tribunales**: 30 segundos
- **Timeout requests**: 30 segundos
- **Retry attempts**: 3

### **Configuración Avanzada**

```json
{
  "max_workers_por_tribunal": 50,
  "pausa_entre_tribunales_segundos": 30,
  "timeout_requests_segundos": 30,
  "tribunales_habilitados": {
    "Corte_Suprema": {
      "habilitado": true,
      "max_workers": 50,
      "total_pages_estimado": 2615
    }
  }
}
```

## 📊 Monitoreo

### **Dashboard en Tiempo Real**

El monitor muestra:
- ✅ Estado de cada tribunal
- 📊 Estadísticas generales
- 🚀 Velocidad de descarga
- 👥 Progreso de workers
- 📝 Sentencias con texto/roles

### **Archivos de Log**

- `descarga_universal_completa.log`: Log principal
- `universal_sentencias_worker.log`: Log de workers
- `resumen_final_universo.json`: Resumen final

## 📁 Estructura de Salida

```
output/descarga_universal_completa/
├── Corte_Suprema/
│   ├── Corte_Suprema_worker_001/
│   │   ├── batch_000001.json
│   │   ├── batch_000002.json
│   │   └── resumen_worker.json
│   └── resumen_tribunal.json
├── Corte_de_Apelaciones/
├── Laborales/
├── Penales/
├── Familia/
├── Civiles/
├── Cobranza/
└── resumen_final_universo.json
```

## 🔧 Solución de Problemas

### **Error: "No se puede conectar al servidor"**

```bash
# Verificar conexión
curl -I https://juris.pjud.cl

# Reducir workers si hay timeout
python3 configurar_descarga_universal.py
```

### **Error: "Memoria insuficiente"**

```bash
# Reducir workers por tribunal
# Editar config_descarga_universal.json
# Cambiar "max_workers_por_tribunal": 25
```

### **Error: "Archivo no encontrado"**

```bash
# Verificar permisos
chmod +x *.py *.sh

# Reinstalar dependencias
pip3 install requests
```

## 📈 Rendimiento Esperado

### **Estimaciones de Tiempo**

| Tribunal | Páginas | Workers | Tiempo Estimado |
|----------|---------|---------|-----------------|
| Corte Suprema | 2,615 | 50 | 15-30 minutos |
| Corte de Apelaciones | 150,989 | 50 | 8-12 horas |
| Laborales | 17,396 | 50 | 1-2 horas |
| Penales | 22,801 | 50 | 1.5-2.5 horas |
| Familia | 11,335 | 50 | 45-90 minutos |
| Civiles | 33,313 | 50 | 2-3 horas |
| Cobranza | 2,613 | 50 | 15-30 minutos |

**Total**: 12-20 horas

### **Recursos del Sistema**

- **RAM**: 4-8 GB recomendados
- **CPU**: 4+ cores recomendados
- **Disco**: 50+ GB para almacenamiento
- **Red**: Conexión estable a internet

## 🛡️ Consideraciones de Seguridad

- **Rate Limiting**: Pausas entre requests
- **User-Agent**: Identificación apropiada
- **Timeout**: Evitar conexiones colgadas
- **Retry Logic**: Recuperación de errores
- **Logging**: Trazabilidad completa

## 📞 Soporte

Para problemas o preguntas:

1. **Verificar logs**: `tail -f descarga_universal_completa.log`
2. **Revisar configuración**: `cat config_descarga_universal.json`
3. **Monitorear progreso**: `python3 monitor_descarga_universal.py`

## 🎯 Próximos Pasos

1. **Configurar descarga** con parámetros deseados
2. **Ejecutar descarga** en horario de bajo tráfico
3. **Monitorear progreso** con dashboard en tiempo real
4. **Verificar resultados** en archivos de salida
5. **Procesar datos** para análisis posterior

---

**¡Sistema listo para descarga universal de sentencias! 🚀**







