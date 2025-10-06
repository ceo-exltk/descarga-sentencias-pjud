#!/usr/bin/env python3
"""
Script de prueba para verificar que el sistema de 5 días funciona correctamente
"""

import subprocess
import sys
import time
from datetime import datetime

def probar_sistema():
    """Probar el sistema de descarga"""
    print("🧪 PROBANDO SISTEMA DE DESCARGA 5 DÍAS")
    print("=" * 50)
    
    # Verificar archivos
    archivos_requeridos = [
        "descarga_universo_completo.py",
        "monitor_descarga_universo.py", 
        "scheduler_5_dias.py",
        "descargar_sentencias_api.py",
        "preparar_para_supabase.py",
        "cargar_a_supabase.py"
    ]
    
    print("🔍 Verificando archivos...")
    for archivo in archivos_requeridos:
        try:
            with open(archivo, 'r') as f:
                print(f"✅ {archivo}")
        except FileNotFoundError:
            print(f"❌ {archivo} - NO ENCONTRADO")
            return False
    
    # Crear directorio de output
    import os
    os.makedirs("output/universo_completo/logs", exist_ok=True)
    print("✅ Directorio de output creado")
    
    # Probar descarga de un tribunal pequeño
    print("\n🧪 Probando descarga de tribunal pequeño (Cobranza)...")
    print("⏰ Esto tomará aproximadamente 2-3 minutos...")
    
    try:
        # Ejecutar descarga de prueba
        result = subprocess.run([
            sys.executable, 
            "descarga_universo_completo.py",
            "--tribunal", "Cobranza"
        ], capture_output=True, text=True, timeout=300)  # 5 minutos máximo
        
        if result.returncode == 0:
            print("✅ Prueba de descarga exitosa")
            print("📊 Output:")
            print(result.stdout[-500:])  # Últimas 500 caracteres
        else:
            print("❌ Error en prueba de descarga")
            print("📊 Error:")
            print(result.stderr[-500:])
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Prueba interrumpida por timeout")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando prueba: {e}")
        return False
    
    # Verificar archivos generados
    print("\n🔍 Verificando archivos generados...")
    import glob
    archivos_generados = glob.glob("output/universo_completo/Cobranza/*.json")
    
    if archivos_generados:
        print(f"✅ Se generaron {len(archivos_generados)} archivos")
        print("📁 Archivos:")
        for archivo in archivos_generados[:5]:  # Mostrar primeros 5
            print(f"  - {archivo}")
        if len(archivos_generados) > 5:
            print(f"  ... y {len(archivos_generados) - 5} más")
    else:
        print("❌ No se generaron archivos")
        return False
    
    # Verificar estado
    print("\n🔍 Verificando estado...")
    try:
        import json
        with open("output/universo_completo/estado_descarga.json", 'r') as f:
            estado = json.load(f)
        
        print("✅ Estado guardado correctamente")
        print(f"📊 Total descargado: {estado.get('total_descargado', 0):,}")
        print(f"🏛️ Tribunales: {len(estado.get('tribunales', {}))}")
        
    except Exception as e:
        print(f"❌ Error leyendo estado: {e}")
        return False
    
    print("\n🎉 ¡SISTEMA FUNCIONANDO CORRECTAMENTE!")
    print("=" * 50)
    print("✅ Todos los componentes verificados")
    print("✅ Descarga de prueba exitosa")
    print("✅ Archivos generados correctamente")
    print("✅ Estado guardado correctamente")
    print("")
    print("🚀 El sistema está listo para ejecutar durante 5 días")
    print("💡 Usa 'python3 iniciar_descarga_5_dias.py' para iniciar")
    
    return True

def main():
    """Función principal"""
    print("🧪 PRUEBA DEL SISTEMA DE DESCARGA 5 DÍAS")
    print("=" * 60)
    print("⚠️  Esta prueba descargará ~26,000 sentencias de Cobranza")
    print("⚠️  Tiempo estimado: 2-3 minutos")
    print("⚠️  Presiona Ctrl+C para cancelar")
    print("=" * 60)
    
    respuesta = input("\n¿Continuar con la prueba? (s/N): ").lower()
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Prueba cancelada")
        return
    
    exito = probar_sistema()
    
    if exito:
        print("\n🎯 PRÓXIMOS PASOS:")
        print("1. Ejecutar: python3 iniciar_descarga_5_dias.py")
        print("2. Seleccionar opción 1 (Descarga completa)")
        print("3. Confirmar con 's'")
        print("4. Dejar ejecutando durante 5 días")
        print("5. Monitorear con: python3 monitor_descarga_universo.py")
    else:
        print("\n❌ PRUEBA FALLIDA")
        print("Revisa los errores anteriores antes de continuar")

if __name__ == "__main__":
    main()
