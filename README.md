# 🏛️ Sistema de Descarga de Sentencias del Poder Judicial

## 📋 Descripción

Sistema completo para la descarga masiva de sentencias de todos los tribunales del Poder Judicial de Chile desde `juris.pjud.cl`, con workers paralelos optimizados y migración automática a Supabase.

## 🚀 Características Principales

- **Descarga Universal**: Todos los tribunales en un solo sistema
- **Workers Paralelos**: Hasta 100 workers simultáneos
- **Migración Automática**: Integración directa con Supabase
- **Monitoreo en Tiempo Real**: Dashboard de progreso en vivo
- **Recuperación de Errores**: Sistema robusto de reintentos
- **Rate Limiting Inteligente**: Evita bloqueos del servidor

## 📁 Estructura del Proyecto

```
descarga_sentencias/
├── scripts/
│   ├── descarga/                    # Scripts de descarga
│   │   ├── descarga_universal_completa.py
│   │   ├── universal_sentencias_worker.py
│   │   ├── enhanced_text_worker_correcto.py
│   │   ├── descarga_especifica_100_workers.py
│   │   └── descarga_rango_especifico.py
│   ├── migracion/                   # Scripts de migración
│   │   ├── migrate_sentencias_final.py
│   │   └── migrate_sentencias_corrected.py
│   └── monitoreo/                   # Scripts de monitoreo
│       ├── monitor_descarga_universal.py
│       └── verificar_progreso.py
├── config/                          # Configuración
│   ├── config_descarga_universal.json
│   └── configurar_descarga_universal.py
├── docs/                           # Documentación
│   ├── README_DESCARGA_UNIVERSAL.md
│   ├── ANALISIS_BLOQUEO_SERVIDOR.md
│   ├── ESTRATEGIA_DESBLOQUEO.md
│   └── INSTRUCCIONES_MÁQUINA_2.md
├── output/                         # Datos descargados
│   ├── descarga_universal_completa/
│   ├── descarga_corte_suprema_fase3_100workers/
│   └── descarga_completa_1501_2615/
└── README.md                       # Este archivo
```

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

**Total**: ~241,000 páginas con 350+ workers

## 🚀 Inicio Rápido

### **1. Descarga Universal (Recomendada)**

```bash
# Ejecutar descarga completa de todos los tribunales
python3 scripts/descarga/descarga_universal_completa.py

# Monitorear progreso (en terminal separada)
python3 scripts/monitoreo/monitor_descarga_universal.py
```

### **2. Descarga Específica**

```bash
# Descarga con 100 workers (alta velocidad)
python3 scripts/descarga/descarga_especifica_100_workers.py

# Descarga de rango específico
python3 scripts/descarga/descarga_rango_especifico.py
```

### **3. Migración a Supabase**

```bash
# Migrar datos descargados a Supabase
python3 scripts/migracion/migrate_sentencias_final.py
```

## ⚙️ Configuración

### **Configuración Básica**

```bash
# Configurar parámetros del sistema
python3 config/configurar_descarga_universal.py
```

### **Parámetros Principales**

- **Workers por tribunal**: 50 (máximo recomendado)
- **Pausa entre tribunales**: 30 segundos
- **Timeout requests**: 30 segundos
- **Retry attempts**: 3

## 📊 Monitoreo

### **Dashboard en Tiempo Real**

```bash
python3 scripts/monitoreo/monitor_descarga_universal.py
```

### **Verificación de Progreso**

```bash
python3 scripts/monitoreo/verificar_progreso.py
```

## 🗄️ Base de Datos

### **Supabase Configuration**

- **URL**: `https://wluachczgiyrmrhdpcue.supabase.co`
- **Tabla**: `sentencias`
- **Migración**: Automática con scripts incluidos

## 📈 Rendimiento Esperado

### **Estimaciones de Tiempo**

| Configuración | Workers | Velocidad | Tiempo Estimado |
|---------------|---------|-----------|-----------------|
| **Conservadora** | 1-2 | 10-20 sentencias/min | 20-40 horas |
| **Moderada** | 50 | 100-200 sentencias/min | 2-4 horas |
| **Agresiva** | 100+ | 500+ sentencias/min | 30-60 minutos |

## 🛡️ Consideraciones de Seguridad

- **Rate Limiting**: Pausas entre requests
- **User-Agent**: Identificación apropiada
- **Timeout**: Evitar conexiones colgadas
- **Retry Logic**: Recuperación de errores
- **Logging**: Trazabilidad completa

## 🔧 Solución de Problemas

### **Error HTTP 419 (Bloqueo del Servidor)**

```bash
# Verificar estado del servidor
curl -I "https://juris.pjud.cl"

# Usar configuración ultra-conservadora
# Esperar 24-48 horas antes de reintentar
```

### **Error de Memoria**

```bash
# Reducir workers por tribunal
# Editar config/config_descarga_universal.json
# Cambiar "max_workers_por_tribunal": 25
```

## 📞 Soporte

Para problemas o preguntas:

1. **Verificar logs**: `tail -f *.log`
2. **Revisar configuración**: `cat config/config_descarga_universal.json`
3. **Monitorear progreso**: `python3 scripts/monitoreo/verificar_progreso.py`

## 📚 Documentación Adicional

- [README Detallado](docs/README_DESCARGA_UNIVERSAL.md)
- [Análisis de Bloqueos](docs/ANALISIS_BLOQUEO_SERVIDOR.md)
- [Estrategias de Desbloqueo](docs/ESTRATEGIA_DESBLOQUEO.md)

## 🎯 Próximos Pasos

1. **Configurar descarga** con parámetros deseados
2. **Ejecutar descarga** en horario de bajo tráfico
3. **Monitorear progreso** con dashboard en tiempo real
4. **Migrar datos** a Supabase
5. **Verificar resultados** en base de datos

---

**¡Sistema listo para descarga masiva de sentencias! 🚀**
