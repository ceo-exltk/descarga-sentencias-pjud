#!/usr/bin/env python3
"""
Script de recuperación para continuar descargas interrumpidas
"""

import json
import os
from datetime import datetime
from pathlib import Path

def analizar_estado():
    """Analizar el estado actual de la descarga"""
    estado_file = Path("output/universo_completo/estado_descarga.json")
    scheduler_file = Path("output/universo_completo/scheduler_estado.json")
    
    print("🔍 ANALIZANDO ESTADO DE DESCARGA")
    print("=" * 50)
    
    if not estado_file.exists():
        print("❌ No se encontró archivo de estado")
        return None
    
    with open(estado_file, 'r') as f:
        estado = json.load(f)
    
    print(f"📅 Inicio: {estado.get('inicio', 'Desconocido')}")
    print(f"🔄 Estado: {estado.get('estado', 'Desconocido')}")
    print(f"📊 Total descargado: {estado.get('total_descargado', 0):,}")
    print(f"🎯 Total estimado: {estado.get('total_estimado', 0):,}")
    
    # Analizar tribunales
    print("\n🏛️ ESTADO POR TRIBUNAL:")
    print("-" * 50)
    
    tribunales = estado.get("tribunales", {})
    completados = 0
    en_progreso = 0
    
    for tribunal_name, tribunal_data in tribunales.items():
        estado_tribunal = tribunal_data.get("estado", "no_iniciado")
        total = tribunal_data.get("total", 0)
        descargado = tribunal_data.get("descargado", 0)
        batch_actual = tribunal_data.get("batch_actual", 0)
        
        if estado_tribunal == "completado":
            completados += 1
            emoji = "✅"
        elif estado_tribunal == "descargando":
            en_progreso += 1
            emoji = "🔄"
        else:
            emoji = "⏳"
        
        progreso = (descargado / total) * 100 if total > 0 else 0
        print(f"{emoji} {tribunal_name:<20} | {descargado:>8,} / {total:>8,} | {progreso:>6.1f}% | Batch {batch_actual}")
    
    print("-" * 50)
    print(f"✅ Completados: {completados}")
    print(f"🔄 En progreso: {en_progreso}")
    print(f"⏳ Pendientes: {7 - completados - en_progreso}")
    
    return estado

def continuar_descarga_tribunal(tribunal_name):
    """Continuar descarga de un tribunal específico"""
    print(f"\n🔄 CONTINUANDO DESCARGA DE {tribunal_name}")
    
    # Verificar si el tribunal está en progreso
    estado_file = Path("output/universo_completo/estado_descarga.json")
    with open(estado_file, 'r') as f:
        estado = json.load(f)
    
    tribunal_data = estado.get("tribunales", {}).get(tribunal_name, {})
    if tribunal_data.get("estado") == "completado":
        print(f"✅ {tribunal_name} ya está completado")
        return
    
    print(f"📊 Estado actual: {tribunal_data.get('estado', 'no_iniciado')}")
    print(f"📥 Descargado: {tribunal_data.get('descargado', 0):,}")
    print(f"🎯 Total: {tribunal_data.get('total', 0):,}")
    print(f"📦 Batch actual: {tribunal_data.get('batch_actual', 0)}")
    
    # Ejecutar descarga
    import subprocess
    import sys
    
    try:
        subprocess.run([
            sys.executable,
            "descarga_universo_completo.py",
            "--tribunal", tribunal_name
        ])
    except KeyboardInterrupt:
        print(f"\n⏹️ Descarga de {tribunal_name} detenida")

def continuar_descarga_completa():
    """Continuar descarga completa desde donde se quedó"""
    print("\n🚀 CONTINUANDO DESCARGA COMPLETA")
    
    estado = analizar_estado()
    if not estado:
        return
    
    # Identificar tribunales pendientes
    tribunales_pendientes = []
    tribunales = estado.get("tribunales", {})
    
    for tribunal_name, tribunal_data in tribunales.items():
        estado_tribunal = tribunal_data.get("estado", "no_iniciado")
        if estado_tribunal != "completado":
            tribunales_pendientes.append(tribunal_name)
    
    if not tribunales_pendientes:
        print("🎉 ¡Todos los tribunales están completados!")
        return
    
    print(f"\n📋 Tribunales pendientes: {len(tribunales_pendientes)}")
    for tribunal in tribunales_pendientes:
        print(f"  - {tribunal}")
    
    # Continuar con scheduler
    import subprocess
    import sys
    
    try:
        subprocess.run([sys.executable, "scheduler_5_dias.py"])
    except KeyboardInterrupt:
        print("\n⏹️ Descarga detenida por usuario")

def limpiar_archivos_temporales():
    """Limpiar archivos temporales y logs antiguos"""
    print("\n🧹 LIMPIANDO ARCHIVOS TEMPORALES")
    
    output_dir = Path("output/universo_completo")
    logs_dir = output_dir / "logs"
    
    if logs_dir.exists():
        # Mantener solo los últimos 10 logs
        log_files = list(logs_dir.glob("*.log"))
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for log_file in log_files[10:]:
            log_file.unlink()
            print(f"🗑️ Eliminado: {log_file.name}")
    
    print("✅ Limpieza completada")

def mostrar_opciones_recuperacion():
    """Mostrar opciones de recuperación"""
    print("\n📋 OPCIONES DE RECUPERACIÓN:")
    print("1. 🔍 Analizar estado actual")
    print("2. 🚀 Continuar descarga completa")
    print("3. 🏛️ Continuar tribunal específico")
    print("4. 📊 Solo monitorear")
    print("5. 🧹 Limpiar archivos temporales")
    print("6. ❌ Salir")
    
    while True:
        try:
            opcion = input("\nSelecciona una opción (1-6): ").strip()
            if opcion in ['1', '2', '3', '4', '5', '6']:
                return opcion
            else:
                print("❌ Opción inválida. Selecciona 1-6.")
        except KeyboardInterrupt:
            print("\n👋 Cancelado por usuario")
            return '6'

def main():
    """Función principal"""
    print("🔄 RECUPERACIÓN DE DESCARGA")
    print("=" * 40)
    
    while True:
        opcion = mostrar_opciones_recuperacion()
        
        if opcion == '1':
            analizar_estado()
        elif opcion == '2':
            continuar_descarga_completa()
        elif opcion == '3':
            tribunal = input("Ingresa el nombre del tribunal: ").strip()
            continuar_descarga_tribunal(tribunal)
        elif opcion == '4':
            import subprocess
            import sys
            subprocess.run([sys.executable, "monitor_descarga_universo.py"])
        elif opcion == '5':
            limpiar_archivos_temporales()
        elif opcion == '6':
            print("👋 Hasta luego!")
            break

if __name__ == "__main__":
    main()
