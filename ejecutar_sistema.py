#!/usr/bin/env python3
"""
Script Principal del Sistema de Descarga de Sentencias
Menú interactivo para ejecutar todas las funcionalidades del sistema
"""

import os
import sys
import subprocess
from pathlib import Path

def mostrar_menu():
    """Muestra el menú principal del sistema"""
    print("🏛️ SISTEMA DE DESCARGA DE SENTENCIAS DEL PODER JUDICIAL")
    print("=" * 60)
    print("1. 📥 Descarga Universal (Todos los tribunales)")
    print("2. ⚡ Descarga Específica (100 workers)")
    print("3. 🎯 Descarga por Rango")
    print("4. 📊 Monitoreo en Tiempo Real")
    print("5. 🔍 Verificar Progreso")
    print("6. 🗄️ Migrar a Supabase")
    print("7. ⚙️ Configurar Sistema")
    print("8. 📚 Ver Documentación")
    print("9. 🚪 Salir")
    print("=" * 60)

def ejecutar_descarga_universal():
    """Ejecuta la descarga universal"""
    print("🌍 Iniciando descarga universal...")
    script_path = "scripts/descarga/descarga_universal_completa.py"
    if Path(script_path).exists():
        subprocess.run([sys.executable, script_path])
    else:
        print("❌ Script no encontrado:", script_path)

def ejecutar_descarga_especifica():
    """Ejecuta la descarga específica con 100 workers"""
    print("⚡ Iniciando descarga específica con 100 workers...")
    script_path = "scripts/descarga/descarga_especifica_100_workers.py"
    if Path(script_path).exists():
        subprocess.run([sys.executable, script_path])
    else:
        print("❌ Script no encontrado:", script_path)

def ejecutar_descarga_rango():
    """Ejecuta la descarga por rango específico"""
    print("🎯 Iniciando descarga por rango...")
    script_path = "scripts/descarga/descarga_rango_especifico.py"
    if Path(script_path).exists():
        subprocess.run([sys.executable, script_path])
    else:
        print("❌ Script no encontrado:", script_path)

def ejecutar_monitoreo():
    """Ejecuta el monitoreo en tiempo real"""
    print("📊 Iniciando monitoreo en tiempo real...")
    script_path = "scripts/monitoreo/monitor_descarga_universal.py"
    if Path(script_path).exists():
        subprocess.run([sys.executable, script_path])
    else:
        print("❌ Script no encontrado:", script_path)

def ejecutar_verificacion():
    """Ejecuta la verificación de progreso"""
    print("🔍 Verificando progreso...")
    script_path = "scripts/monitoreo/verificar_progreso.py"
    if Path(script_path).exists():
        subprocess.run([sys.executable, script_path])
    else:
        print("❌ Script no encontrado:", script_path)

def ejecutar_migracion():
    """Ejecuta la migración a Supabase"""
    print("🗄️ Iniciando migración a Supabase...")
    script_path = "scripts/migracion/migrate_sentencias_final.py"
    if Path(script_path).exists():
        subprocess.run([sys.executable, script_path])
    else:
        print("❌ Script no encontrado:", script_path)

def ejecutar_configuracion():
    """Ejecuta la configuración del sistema"""
    print("⚙️ Iniciando configuración del sistema...")
    script_path = "config/configurar_descarga_universal.py"
    if Path(script_path).exists():
        subprocess.run([sys.executable, script_path])
    else:
        print("❌ Script no encontrado:", script_path)

def mostrar_documentacion():
    """Muestra la documentación disponible"""
    print("📚 DOCUMENTACIÓN DISPONIBLE:")
    print("-" * 40)
    
    docs_dir = Path("docs")
    if docs_dir.exists():
        for doc_file in docs_dir.glob("*.md"):
            print(f"📄 {doc_file.name}")
            print(f"   Ruta: {doc_file}")
            print()
    else:
        print("❌ Directorio de documentación no encontrado")

def main():
    """Función principal del sistema"""
    while True:
        mostrar_menu()
        
        try:
            opcion = input("Seleccione una opción (1-9): ").strip()
            
            if opcion == "1":
                ejecutar_descarga_universal()
            elif opcion == "2":
                ejecutar_descarga_especifica()
            elif opcion == "3":
                ejecutar_descarga_rango()
            elif opcion == "4":
                ejecutar_monitoreo()
            elif opcion == "5":
                ejecutar_verificacion()
            elif opcion == "6":
                ejecutar_migracion()
            elif opcion == "7":
                ejecutar_configuracion()
            elif opcion == "8":
                mostrar_documentacion()
            elif opcion == "9":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida. Por favor, seleccione 1-9.")
            
            if opcion in ["1", "2", "3", "4", "5", "6", "7"]:
                input("\n⏸️ Presione Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Sistema interrumpido por el usuario")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\n⏸️ Presione Enter para continuar...")

if __name__ == "__main__":
    main()
