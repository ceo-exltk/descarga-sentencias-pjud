# 🚀 GitHub Actions - Descarga de Sentencias

## 📋 Cómo usar el sistema

### 1. **Disparar descarga manual**
1. Ve a **GitHub** → **Actions** → **"Descargar Sentencias por Día"**
2. Haz clic en **"Run workflow"**
3. Ingresa la fecha (formato: YYYY-MM-DD)
4. Haz clic en **"Run workflow"**

### 2. **¿Qué hace el sistema?**
- ✅ Descarga todas las sentencias del día especificado
- ✅ Procesa archivos para ingesta en Supabase
- ✅ Genera archivos consolidados
- ✅ Sube resultados como "artifacts"

### 3. **Archivos generados**
Después de la ejecución encontrarás:
- `sentencias_consolidadas.json` - Archivo completo con metadatos
- `sentencias_para_supabase.json` - Solo sentencias para ingesta
- `estadisticas_descarga.json` - Estadísticas de la descarga
- `descarga_resumen.txt` - Resumen en texto plano

### 4. **Descargar resultados**
1. Ve a la ejecución completada en **Actions**
2. En la sección **"Artifacts"** descarga el archivo
3. Descomprime y usa los archivos JSON para Supabase

## 🔧 **Configuración local (opcional)**

Si quieres probar localmente:

```bash
# Descargar sentencias de un día específico
python3 descargar_sentencias_api.py 2024-01-15 2024-01-15

# Preparar archivos para Supabase
python3 preparar_para_supabase.py output/descarga_api
```

## 📊 **Ejemplo de uso**

**Fecha:** 2024-01-15
**Resultado:** 
- 37 sentencias de Corte Suprema
- Archivos listos para Supabase
- Estadísticas completas

## 🎯 **Ventajas**
- ✅ No necesitas tu computadora
- ✅ Se ejecuta en servidores de GitHub
- ✅ Historial de todas las descargas
- ✅ Archivos listos para Supabase
- ✅ Proceso completamente automatizado
