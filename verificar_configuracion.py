#!/usr/bin/env python3
"""
Script para verificar la configuración completa del sistema
"""

import os
import sys
import json
from pathlib import Path

def verificar_archivos():
    """Verifica que todos los archivos necesarios existan"""
    archivos_requeridos = [
        'descargar_sentencias_api.py',
        'preparar_para_supabase.py', 
        'cargar_a_supabase.py',
        '.github/workflows/descargar-sentencias-supabase.yml'
    ]
    
    print("🔍 Verificando archivos del sistema...")
    todos_presentes = True
    
    for archivo in archivos_requeridos:
        if Path(archivo).exists():
            print(f"  ✅ {archivo}")
        else:
            print(f"  ❌ {archivo} - FALTANTE")
            todos_presentes = False
    
    return todos_presentes

def verificar_workflow():
    """Verifica la configuración del workflow"""
    print("\n🔍 Verificando configuración del workflow...")
    
    workflow_path = '.github/workflows/descargar-sentencias-supabase.yml'
    if not Path(workflow_path).exists():
        print("  ❌ Workflow no encontrado")
        return False
    
    with open(workflow_path, 'r') as f:
        content = f.read()
    
    # Verificar elementos clave
    elementos_clave = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY', 
        'cargar_a_supabase.py',
        'preparar_para_supabase.py',
        'descargar_sentencias_api.py'
    ]
    
    todos_presentes = True
    for elemento in elementos_clave:
        if elemento in content:
            print(f"  ✅ {elemento}")
        else:
            print(f"  ❌ {elemento} - NO ENCONTRADO")
            todos_presentes = False
    
    return todos_presentes

def verificar_scripts():
    """Verifica que los scripts tengan la configuración correcta"""
    print("\n🔍 Verificando configuración de scripts...")
    
    # Verificar cargar_a_supabase.py
    with open('cargar_a_supabase.py', 'r') as f:
        cargar_content = f.read()
    
    if 'supabase_url' in cargar_content and 'supabase_key' in cargar_content:
        print("  ✅ cargar_a_supabase.py configurado correctamente")
    else:
        print("  ❌ cargar_a_supabase.py no está configurado correctamente")
        return False
    
    # Verificar preparar_para_supabase.py
    if Path('preparar_para_supabase.py').exists():
        print("  ✅ preparar_para_supabase.py presente")
    else:
        print("  ❌ preparar_para_supabase.py no encontrado")
        return False
    
    return True

def mostrar_instrucciones_secrets():
    """Muestra las instrucciones para configurar secrets"""
    print("\n" + "="*60)
    print("🔧 CONFIGURACIÓN DE GITHUB SECRETS")
    print("="*60)
    print("Para que el workflow funcione, necesitas configurar estos secrets en GitHub:")
    print()
    print("1. Ve a tu repositorio en GitHub")
    print("2. Settings → Secrets and variables → Actions")
    print("3. Click 'New repository secret'")
    print("4. Agrega estos secrets:")
    print()
    print("   SUPABASE_URL:")
    print("   - Valor: https://tu-proyecto-id.supabase.co")
    print()
    print("   SUPABASE_ANON_KEY:")
    print("   - Valor: tu-anon-key-de-supabase")
    print()
    print("⚠️  IMPORTANTE:")
    print("   Estos secrets deben estar configurados para que el workflow")
    print("   pueda cargar datos automáticamente a Supabase.")
    print("="*60)

def main():
    print("🚀 VERIFICACIÓN DEL SISTEMA DE DESCARGA Y SUPABASE")
    print("="*60)
    
    # Verificar archivos
    archivos_ok = verificar_archivos()
    
    # Verificar workflow
    workflow_ok = verificar_workflow()
    
    # Verificar scripts
    scripts_ok = verificar_scripts()
    
    print("\n" + "="*60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*60)
    
    if archivos_ok and workflow_ok and scripts_ok:
        print("✅ SISTEMA COMPLETAMENTE CONFIGURADO")
        print()
        print("🎯 PRÓXIMOS PASOS:")
        print("1. Configurar GitHub Secrets (SUPABASE_URL y SUPABASE_ANON_KEY)")
        print("2. Ejecutar el workflow desde GitHub Actions")
        print("3. ¡El sistema automático de Supabase hará el resto!")
        print()
        print("🚀 El workflow 'Descargar y Cargar a Supabase' está listo para usar.")
    else:
        print("❌ CONFIGURACIÓN INCOMPLETA")
        print("   Revisa los elementos marcados con ❌ arriba.")
    
    mostrar_instrucciones_secrets()

if __name__ == "__main__":
    main()
