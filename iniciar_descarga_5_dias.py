#!/usr/bin/env python3
"""
Script principal para iniciar la descarga del universo completo durante 5 días
"""

import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path

def verificar_requisitos():
    """Verificar que todos los requisitos estén disponibles"""
    print("🔍 Verificando requisitos...")
    
    # Verificar archivos necesarios
    archivos_requeridos = [
        "descarga_universo_completo.py",
        "monitor_descarga_universo.py", 
        "scheduler_5_dias.py",
        "descargar_sentencias_api.py",
        "preparar_para_supabase.py",
        "cargar_a_supabase.py"
    ]
    
    for archivo in archivos_requeridos:
        if not Path(archivo).exists():
            print(f"❌ Archivo faltante: {archivo}")
            return False
        print(f"✅ {archivo}")
    
    # Verificar directorio de output
    output_dir = Path("output/universo_completo")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Directorio de output: {output_dir}")
    
    return True

def mostrar_informacion():
    """Mostrar información del sistema"""
    print("\n🌍 SISTEMA DE DESCARGA UNIVERSO COMPLETO")
    print("=" * 60)
    print("📊 Total de sentencias: 4,115,881")
    print("🏛️ Tribunales: 7")
    print("⏰ Duración estimada: 5 días")
    print("🚀 Ejecución continua: 24/7 sin pausas")
    print("⚡ Pausas mínimas: Solo entre tribunales y por errores")
    print("🔄 Recuperación automática: Sí")
    print("📊 Monitoreo en tiempo real: Sí")
    print("=" * 60)

def mostrar_opciones():
    """Mostrar opciones de ejecución"""
    print("\n📋 OPCIONES DE EJECUCIÓN:")
    print("1. 🚀 Iniciar descarga completa (5 días)")
    print("2. 📊 Solo monitorear progreso")
    print("3. 🔄 Continuar descarga interrumpida")
    print("4. 🧪 Probar con un tribunal pequeño")
    print("5. ❌ Cancelar")
    
    while True:
        try:
            opcion = input("\nSelecciona una opción (1-5): ").strip()
            if opcion in ['1', '2', '3', '4', '5']:
                return opcion
            else:
                print("❌ Opción inválida. Selecciona 1-5.")
        except KeyboardInterrupt:
            print("\n👋 Cancelado por usuario")
            return '5'

def ejecutar_descarga_completa():
    """Ejecutar descarga completa con scheduler"""
    print("\n🚀 INICIANDO DESCARGA COMPLETA")
    print("⚠️  El sistema se ejecutará durante 5 días CONTINUOS")
    print("⚠️  Sin pausas nocturnas - ejecución 24/7")
    print("⚠️  Presiona Ctrl+C para detener de forma segura")
    print("⚠️  El estado se guarda automáticamente")
    
    try:
        # Ejecutar scheduler
        subprocess.run([sys.executable, "scheduler_5_dias.py"])
    except KeyboardInterrupt:
        print("\n⏹️ Descarga detenida por usuario")
        print("💾 Estado guardado - puedes continuar más tarde")

def ejecutar_monitor():
    """Ejecutar solo el monitor"""
    print("\n📊 INICIANDO MONITOR")
    print("💡 Presiona Ctrl+C para salir del monitor")
    
    try:
        subprocess.run([sys.executable, "monitor_descarga_universo.py"])
    except KeyboardInterrupt:
        print("\n👋 Monitor detenido")

def continuar_descarga():
    """Continuar descarga interrumpida"""
    print("\n🔄 CONTINUANDO DESCARGA INTERRUMPIDA")
    
    # Verificar si hay estado guardado
    estado_file = Path("output/universo_completo/scheduler_estado.json")
    if not estado_file.exists():
        print("❌ No se encontró estado guardado")
        print("💡 Inicia una nueva descarga con la opción 1")
        return
    
    print("✅ Estado encontrado - continuando...")
    try:
        subprocess.run([sys.executable, "scheduler_5_dias.py"])
    except KeyboardInterrupt:
        print("\n⏹️ Descarga detenida por usuario")

def probar_tribunal_pequeno():
    """Probar con un tribunal pequeño (Cobranza)"""
    print("\n🧪 PROBANDO CON TRIBUNAL PEQUEÑO (Cobranza)")
    print("📊 ~26,000 sentencias - tiempo estimado: 30 minutos")
    
    try:
        # Ejecutar descarga solo de Cobranza
        subprocess.run([
            sys.executable, 
            "descarga_universo_completo.py",
            "--tribunal", "Cobranza"
        ])
    except KeyboardInterrupt:
        print("\n⏹️ Prueba detenida por usuario")

def main():
    """Función principal"""
    print("🌍 DESCARGA UNIVERSO COMPLETO - 5 DÍAS")
    print("=" * 50)
    
    # Verificar requisitos
    if not verificar_requisitos():
        print("\n❌ Requisitos no cumplidos")
        return
    
    # Mostrar información
    mostrar_informacion()
    
    # Mostrar opciones
    opcion = mostrar_opciones()
    
    if opcion == '1':
        ejecutar_descarga_completa()
    elif opcion == '2':
        ejecutar_monitor()
    elif opcion == '3':
        continuar_descarga()
    elif opcion == '4':
        probar_tribunal_pequeno()
    elif opcion == '5':
        print("👋 Hasta luego!")
    else:
        print("❌ Opción inválida")

if __name__ == "__main__":
    main()
