#!/usr/bin/env python3
"""
Verificador de Progreso de Descarga
Muestra estadísticas detalladas del progreso de descarga
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

def count_json_files(directory: Path) -> int:
    """Cuenta archivos JSON en un directorio."""
    if not directory.exists():
        return 0
    return len(list(directory.glob("*.json")))

def count_sentencias_in_file(file_path: Path) -> int:
    """Cuenta sentencias en un archivo JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'sentencias' in data and isinstance(data['sentencias'], list):
                return len(data['sentencias'])
        return 0
    except Exception:
        return 0

def get_database_count():
    """Obtiene el conteo de sentencias en la base de datos."""
    try:
        from supabase import create_client, Client
        SUPABASE_URL = "https://wluachczgiyrmrhdpcue.supabase.co"
        SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndsdWFjaGN6Z2l5cm1yaGRwY3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5MjA1NDcsImV4cCI6MjA3MjQ5NjU0N30.gXSqEYy_LFp951EnBhFxU_7RSf5VbJXRc2GlLn7OB7I"
        
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        response = supabase.from_('sentencias').select('id', count='exact').execute()
        return response.count if response.count else 0
    except Exception as e:
        print(f"Error obteniendo conteo de BD: {e}")
        return 0

def analyze_download_progress():
    """Analiza el progreso de la descarga."""
    print("=" * 80)
    print("📊 REPORTE DE PROGRESO DE DESCARGA DE SENTENCIAS")
    print("=" * 80)
    print(f"🕐 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Fase 1: Páginas 901-1500
    print("📋 FASE 1: PÁGINAS 901-1500")
    print("-" * 40)
    
    fase1_dir = Path("output/descarga_corte_suprema_fase3_100workers")
    if fase1_dir.exists():
        archivos_fase1 = count_json_files(fase1_dir)
        print(f"📁 Archivos JSON generados: {archivos_fase1}")
        
        # Contar sentencias en archivos
        total_sentencias_fase1 = 0
        for file_path in fase1_dir.rglob("*.json"):
            total_sentencias_fase1 += count_sentencias_in_file(file_path)
        
        print(f"📄 Total sentencias descargadas: {total_sentencias_fase1}")
        print(f"📊 Progreso estimado: {(archivos_fase1 / 600) * 100:.1f}%")
    else:
        print("❌ Directorio de Fase 1 no encontrado")
    
    print()
    
    # Fase 2: Páginas 1501-2615
    print("📋 FASE 2: PÁGINAS 1501-2615")
    print("-" * 40)
    
    fase2_dir = Path("output/descarga_completa_1501_2615")
    if fase2_dir.exists():
        archivos_fase2 = count_json_files(fase2_dir)
        print(f"📁 Archivos JSON generados: {archivos_fase2}")
        
        # Contar sentencias en archivos
        total_sentencias_fase2 = 0
        for file_path in fase2_dir.rglob("*.json"):
            total_sentencias_fase2 += count_sentencias_in_file(file_path)
        
        print(f"📄 Total sentencias descargadas: {total_sentencias_fase2}")
        print(f"📊 Progreso estimado: {(archivos_fase2 / 1115) * 100:.1f}%")
    else:
        print("⏳ Fase 2 no iniciada aún")
    
    print()
    
    # Base de datos
    print("🗄️ BASE DE DATOS SUPABASE")
    print("-" * 40)
    
    try:
        db_count = get_database_count()
        print(f"📊 Total sentencias en BD: {db_count:,}")
        
        if db_count > 0:
            print(f"✅ Base de datos activa y poblada")
        else:
            print("⚠️ Base de datos vacía o no accesible")
    except Exception as e:
        print(f"❌ Error accediendo a BD: {e}")
    
    print()
    
    # Resumen total
    print("📈 RESUMEN TOTAL")
    print("-" * 40)
    
    total_archivos = archivos_fase1 + (archivos_fase2 if fase2_dir.exists() else 0)
    total_sentencias_descargadas = total_sentencias_fase1 + (total_sentencias_fase2 if fase2_dir.exists() else 0)
    
    print(f"📁 Total archivos JSON: {total_archivos}")
    print(f"📄 Total sentencias descargadas: {total_sentencias_descargadas:,}")
    print(f"🗄️ Total sentencias en BD: {db_count:,}")
    
    # Progreso general
    total_paginas_objetivo = 600 + 1115  # 1715 páginas total
    total_paginas_procesadas = archivos_fase1 + (archivos_fase2 if fase2_dir.exists() else 0)
    progreso_general = (total_paginas_procesadas / total_paginas_objetivo) * 100
    
    print(f"📊 Progreso general: {progreso_general:.1f}%")
    
    print()
    print("=" * 80)

def check_active_processes():
    """Verifica procesos activos de descarga."""
    print("🔍 PROCESOS ACTIVOS")
    print("-" * 40)
    
    try:
        import subprocess
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        descarga_activa = False
        migracion_activa = False
        
        for line in lines:
            if 'descarga_maquina2_100_workers.py' in line and 'python' in line:
                print("✅ Descarga Fase 1 (901-1500): ACTIVA")
                descarga_activa = True
            elif 'descarga_completa_1501_2615.py' in line and 'python' in line:
                print("✅ Descarga Fase 2 (1501-2615): ACTIVA")
                descarga_activa = True
            elif 'migrate' in line and 'python' in line:
                print("✅ Migración: ACTIVA")
                migracion_activa = True
        
        if not descarga_activa and not migracion_activa:
            print("⏸️ No hay procesos de descarga/migración activos")
        
    except Exception as e:
        print(f"❌ Error verificando procesos: {e}")

def main():
    """Función principal."""
    analyze_download_progress()
    print()
    check_active_processes()
    print()
    print("💡 Para monitoreo continuo: watch -n 30 python3 verificar_progreso.py")

if __name__ == "__main__":
    main()







