#!/usr/bin/env python3
"""
Script para preparar archivos descargados para ingesta en Supabase
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

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
            
            # Agregar metadatos para Supabase
            for sentencia in sentencias:
                sentencia['tribunal_origen'] = tribunal
                sentencia['batch_id'] = data.get('batch', 0)
                sentencia['fecha_descarga'] = datetime.now().isoformat()
                sentencia['archivo_origen'] = str(archivo)
            
            sentencias_totales.extend(sentencias)
            estadisticas["archivos_procesados"] += 1
            estadisticas["sentencias_totales"] += len(sentencias)
            estadisticas["tribunales"].add(tribunal)
            
            print(f"✅ {archivo.name}: {len(sentencias)} sentencias")
            
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
