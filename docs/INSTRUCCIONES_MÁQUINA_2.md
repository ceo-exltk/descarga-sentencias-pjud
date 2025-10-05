# 🚀 INSTRUCCIONES PARA SEGUNDA MÁQUINA

## 📋 **RESUMEN EJECUTIVO**
- **Archivo**: `descarga_maquina2_paginas_901_1500.py`
- **Rango**: Páginas 901-1500 (600 páginas)
- **Workers**: 61-90 (30 workers)
- **Sin colisión**: ✅ Garantizado

## 🎯 **CONFIGURACIÓN SIN COLISIÓN**

### **Máquina 1 (ACTUAL)**
- **Páginas**: 301-900
- **Workers**: 1-60
- **Estado**: En ejecución

### **Máquina 2 (NUEVA)**
- **Páginas**: 901-1500
- **Workers**: 61-90
- **Estado**: Listo para ejecutar

## 📁 **ARCHIVOS NECESARIOS**

### **1. Archivos a copiar a la segunda máquina:**
```
📁 Archivos requeridos:
├── enhanced_text_worker_correcto.py (clase base)
├── descarga_maquina2_paginas_901_1500.py (script principal)
└── INSTRUCCIONES_MÁQUINA_2.md (este archivo)
```

### **2. Estructura de carpetas:**
```
📁 En la segunda máquina:
├── enhanced_text_worker_correcto.py
├── descarga_maquina2_paginas_901_1500.py
└── output/
    └── descarga_corte_suprema_fase3/
        ├── worker_61/
        ├── worker_62/
        ├── ...
        └── worker_90/
```

## ⚙️ **INSTRUCCIONES DE EJECUCIÓN**

### **Paso 1: Preparar la máquina**
```bash
# Crear directorio de trabajo
mkdir -p KB-JURISP
cd KB-JURISP

# Crear estructura de carpetas
mkdir -p output/descarga_corte_suprema_fase3
```

### **Paso 2: Copiar archivos**
```bash
# Copiar archivos necesarios desde la máquina 1
scp usuario@maquina1:/ruta/KB-JURISP/enhanced_text_worker_correcto.py .
scp usuario@maquina1:/ruta/KB-JURISP/descarga_maquina2_paginas_901_1500.py .
```

### **Paso 3: Instalar dependencias**
```bash
# Instalar Python 3.13+ y dependencias
pip install requests beautifulsoup4
```

### **Paso 4: Ejecutar descarga**
```bash
# Ejecutar en segundo plano
nohup python3 descarga_maquina2_paginas_901_1500.py > descarga_maquina2.log 2>&1 &

# Verificar que está ejecutándose
ps aux | grep descarga_maquina2
```

## 📊 **MONITOREO**

### **Verificar progreso:**
```bash
# Ver logs en tiempo real
tail -f descarga_maquina2.log

# Verificar procesos
ps aux | grep descarga_maquina2

# Contar sentencias descargadas
find output/descarga_corte_suprema_fase3/worker_6* -name "*.json" | wc -l
```

### **Estadísticas esperadas:**
- **Páginas**: 600 (901-1500)
- **Sentencias estimadas**: ~60,000
- **Tiempo estimado**: 4-6 horas
- **Memoria requerida**: ~2-3 GB

## 🔒 **GARANTÍAS DE NO COLISIÓN**

### **1. Rangos de páginas:**
- **Máquina 1**: 301-900 ✅
- **Máquina 2**: 901-1500 ✅
- **Sin solapamiento**: ✅

### **2. Workers:**
- **Máquina 1**: worker_01 a worker_60 ✅
- **Máquina 2**: worker_61 a worker_90 ✅
- **Sin conflicto**: ✅

### **3. Archivos de salida:**
- **Máquina 1**: batch_000301.json a batch_000900.json ✅
- **Máquina 2**: batch_000901.json a batch_001500.json ✅
- **Sin colisión**: ✅

## 🚨 **CONSIDERACIONES IMPORTANTES**

### **1. Sincronización:**
- Ambas máquinas pueden ejecutarse simultáneamente
- No hay dependencias entre ellas
- Cada una procesa su rango independientemente

### **2. Recursos:**
- **CPU**: Mínimo 4 cores recomendado
- **RAM**: Mínimo 4 GB recomendado
- **Red**: Conexión estable a internet

### **3. Logs:**
- Cada máquina genera su propio log
- Logs independientes para facilitar monitoreo
- Identificación clara por máquina

## 📈 **EXPANSIÓN FUTURA**

### **Máquina 3 (opcional):**
- **Páginas**: 1501-2100
- **Workers**: 91-120
- **Mismo patrón**: Sin colisión

### **Máquina 4 (opcional):**
- **Páginas**: 2101-2615
- **Workers**: 121-150
- **Mismo patrón**: Sin colisión

## ✅ **VERIFICACIÓN FINAL**

Antes de ejecutar, verificar:
- [ ] Archivos copiados correctamente
- [ ] Dependencias instaladas
- [ ] Estructura de carpetas creada
- [ ] Conexión a internet estable
- [ ] Recursos suficientes disponibles

## 🎉 **RESULTADO ESPERADO**

Al completarse ambas máquinas:
- **Total páginas**: 1,200 (301-1500)
- **Total sentencias**: ~120,000
- **Total workers**: 90 (60 + 30)
- **Tiempo total**: 4-6 horas
- **Cobertura**: ~46% del universo total
