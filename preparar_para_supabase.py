#!/usr/bin/env python3
"""
Script corregido para preparar archivos descargados para ingesta en Supabase
con mapeo correcto de campos
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def mapear_sentencia_para_supabase(sentencia_api, tribunal):
    """Mapea una sentencia de la API al formato esperado por Supabase"""
    
    # Solo mapear campos que existen en la tabla Supabase
    sentencia_supabase = {
        # Campos básicos
        "rol_numero": sentencia_api.get("rol_era_sup_s", ""),
        "rol_completo": sentencia_api.get("rol_era_sup_s", ""),
        "correlativo": sentencia_api.get("correlativo", ""),
        "caratulado": sentencia_api.get("caratulado_s", ""),
        "caratulado_anonimizado": sentencia_api.get("caratulado_anonimizado", ""),
        "fallo_anonimizado": sentencia_api.get("fallo_anonimizado", ""),
        
        # Fechas
        "fecha_sentencia": sentencia_api.get("sent__fec_sentencia_dt", ""),
        "fecha_actualizacion": sentencia_api.get("sent__fec_actualiza_dt", ""),
        
        # Información del tribunal
        "era": sentencia_api.get("era_sup_i", ""),
        "corte": tribunal,
        "codigo_corte": sentencia_api.get("cod_juz_i", ""),
        "sala": sentencia_api.get("sala", ""),
        "juzgado": sentencia_api.get("juzgado", ""),
        
        # Información del proceso
        "tipo_recurso": sentencia_api.get("tipo_recurso", ""),
        "resultado_recurso": sentencia_api.get("resultado_recurso", ""),
        "libro": sentencia_api.get("libro", ""),
        
        # Personas
        "ministros": sentencia_api.get("ministros", []),
        "redactor": sentencia_api.get("redactor", ""),
        "id_redactor": sentencia_api.get("id_redactor", ""),
        "relator": sentencia_api.get("relator", ""),
        
        # Clasificación
        "materias": sentencia_api.get("materias", []),
        "descriptores": sentencia_api.get("descriptores", []),
        "normas": sentencia_api.get("normas", []),
        
        # Publicación
        "condicion_publicacion": sentencia_api.get("gls_condicion_publicacion_s", ""),
        "publicacion_original": sentencia_api.get("publicacion_original", ""),
        "url_acceso": sentencia_api.get("url_acceso", ""),
        "url_corta": sentencia_api.get("url_corta", ""),
        
        # Texto completo (si está disponible)
        "texto_completo": sentencia_api.get("texto_completo", "")
    }
    
    # Limpiar campos vacíos o None
    sentencia_limpia = {}
    for key, value in sentencia_supabase.items():
        if value is not None and value != "":
            sentencia_limpia[key] = value
    
    return sentencia_limpia

def procesar_archivos_descarga(directorio_output):
    """Procesa todos los archivos JSON de descarga y los prepara para Supabase"""
    
    print(f"🔄 Procesando archivos en: {directorio_output}")
    
    # Buscar todos los archivos batch
    archivos_batch = list(Path(directorio_output).rglob("batch_*.json"))
    
    if not archivos_batch:
        print("❌ No se encontraron archivos batch_*.json")
        return False
    
    print(f"📁 Encontrados {len(archivos_batch)} archivos batch")
    
    # Procesar cada archivo
    sentencias_totales = []
    estadisticas = {
        "archivos_procesados": 0,
        "sentencias_totales": 0,
        "tribunales": set(),
        "fecha_procesamiento": datetime.now().isoformat()
    }
    
    for archivo in archivos_batch:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extraer sentencias
            sentencias = data.get('sentencias', [])
            tribunal = data.get('tribunal', 'Desconocido')
            
            # Mapear cada sentencia al formato de Supabase
            sentencias_mapeadas = []
            for sentencia in sentencias:
                sentencia_mapeada = mapear_sentencia_para_supabase(sentencia, tribunal)
                sentencias_mapeadas.append(sentencia_mapeada)
            
            sentencias_totales.extend(sentencias_mapeadas)
            estadisticas["archivos_procesados"] += 1
            estadisticas["sentencias_totales"] += len(sentencias_mapeadas)
            estadisticas["tribunales"].add(tribunal)
            
            print(f"✅ {archivo.name}: {len(sentencias_mapeadas)} sentencias mapeadas")
            
        except Exception as e:
            print(f"❌ Error procesando {archivo}: {e}")
    
    # Convertir set a list para JSON
    estadisticas["tribunales"] = list(estadisticas["tribunales"])
    
    # Guardar archivo consolidado para Supabase
    archivo_supabase = os.path.join(directorio_output, "sentencias_consolidadas.json")
    with open(archivo_supabase, 'w', encoding='utf-8') as f:
        json.dump({
            "metadatos": estadisticas,
            "sentencias": sentencias_totales
        }, f, ensure_ascii=False, indent=2, default=str)
    
    # Guardar solo las sentencias (para ingesta directa)
    archivo_solo_sentencias = os.path.join(directorio_output, "sentencias_para_supabase.json")
    with open(archivo_solo_sentencias, 'w', encoding='utf-8') as f:
        json.dump(sentencias_totales, f, ensure_ascii=False, indent=2, default=str)
    
    # Crear archivo de estadísticas
    archivo_stats = os.path.join(directorio_output, "estadisticas_descarga.json")
    with open(archivo_stats, 'w', encoding='utf-8') as f:
        json.dump(estadisticas, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n📊 RESUMEN:")
    print(f"   📁 Archivos procesados: {estadisticas['archivos_procesados']}")
    print(f"   📄 Sentencias totales: {estadisticas['sentencias_totales']}")
    print(f"   🏛️ Tribunales: {', '.join(estadisticas['tribunales'])}")
    print(f"   💾 Archivo consolidado: {archivo_supabase}")
    print(f"   💾 Archivo para Supabase: {archivo_solo_sentencias}")
    print(f"   📊 Estadísticas: {archivo_stats}")
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 preparar_para_supabase.py <directorio_output>")
        print("Ejemplo: python3 preparar_para_supabase.py output/descarga_2024_01_15")
        return False
    
    directorio = sys.argv[1]
    
    if not os.path.exists(directorio):
        print(f"❌ Directorio no encontrado: {directorio}")
        return False
    
    print("🔄 PREPARANDO ARCHIVOS PARA SUPABASE")
    print("=" * 50)
    
    return procesar_archivos_descarga(directorio)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
