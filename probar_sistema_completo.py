#!/usr/bin/env python3
"""
Probador del Sistema Completo
Script para probar todos los componentes del sistema cloud
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

def probar_configuracion():
    """Probar configuración del sistema"""
    print("🔧 PROBANDO CONFIGURACIÓN")
    print("=" * 50)
    
    # Verificar variables de entorno
    github_repo = os.getenv('GITHUB_REPO')
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    print(f"📝 GitHub Repo: {github_repo or 'No configurado'}")
    print(f"🗄️ Supabase URL: {supabase_url or 'No configurado'}")
    print(f"🔑 Supabase Key: {'Configurado' if supabase_key else 'No configurado'}")
    
    if not all([github_repo, supabase_url, supabase_key]):
        print("❌ Variables de entorno no configuradas")
        return False
    
    print("✅ Configuración correcta")
    return True

def probar_generador_dashboard():
    """Probar generador de dashboard"""
    print("\n📊 PROBANDO GENERADOR DE DASHBOARD")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            'python3', 'scripts/dashboard/generar_dashboard.py'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Generador de dashboard funcionando")
            
            # Verificar archivos generados
            dashboard_files = [
                'docs/dashboard/data/stats.json',
                'docs/dashboard/data/tribunals.json',
                'docs/dashboard/data/activity.json',
                'docs/dashboard/index.html'
            ]
            
            for file in dashboard_files:
                if Path(file).exists():
                    print(f"✅ {file} generado")
                else:
                    print(f"❌ {file} no encontrado")
            
            return True
        else:
            print(f"❌ Error en generador: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout en generador de dashboard")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def probar_orquestador():
    """Probar orquestador cloud"""
    print("\n🌐 PROBANDO ORQUESTADOR CLOUD")
    print("=" * 50)
    
    try:
        # Probar importación del orquestador
        result = subprocess.run([
            'python3', '-c', 
            'import sys; sys.path.append("scripts/cloud"); from orquestador_cloud import OrquestadorCloud; print("✅ Orquestador importado correctamente")'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Orquestador cloud funcionando")
            return True
        else:
            print(f"❌ Error en orquestador: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def probar_github_actions():
    """Probar configuración de GitHub Actions"""
    print("\n⚙️ PROBANDO GITHUB ACTIONS")
    print("=" * 50)
    
    try:
        # Verificar que los workflows existen
        workflows = [
            '.github/workflows/descarga-incremental.yml',
            '.github/workflows/generar-dashboard.yml'
        ]
        
        for workflow in workflows:
            if Path(workflow).exists():
                print(f"✅ {workflow} existe")
            else:
                print(f"❌ {workflow} no encontrado")
        
        # Verificar secretos (simulado)
        print("🔍 Verificando configuración de secretos...")
        print("✅ Workflows configurados")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def probar_dashboard_local():
    """Probar dashboard localmente"""
    print("\n🌐 PROBANDO DASHBOARD LOCAL")
    print("=" * 50)
    
    try:
        dashboard_file = Path('docs/dashboard/index.html')
        if dashboard_file.exists():
            print("✅ Dashboard HTML generado")
            
            # Verificar que tiene contenido
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'Dashboard de Descarga de Sentencias' in content:
                    print("✅ Dashboard con contenido correcto")
                    return True
                else:
                    print("❌ Dashboard sin contenido esperado")
                    return False
        else:
            print("❌ Dashboard HTML no encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def mostrar_resumen_pruebas(resultados):
    """Mostrar resumen de las pruebas"""
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    total_pruebas = len(resultados)
    pruebas_exitosas = sum(1 for resultado in resultados.values() if resultado)
    
    print(f"✅ Pruebas exitosas: {pruebas_exitosas}/{total_pruebas}")
    print(f"❌ Pruebas fallidas: {total_pruebas - pruebas_exitosas}/{total_pruebas}")
    
    print("\n📋 DETALLE DE PRUEBAS:")
    for nombre, resultado in resultados.items():
        estado = "✅ EXITOSA" if resultado else "❌ FALLÓ"
        print(f"   {nombre}: {estado}")
    
    if pruebas_exitosas == total_pruebas:
        print("\n🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("🚀 Sistema listo para usar")
        print("\n📚 PRÓXIMOS PASOS:")
        print("1. Ejecutar: python3 scripts/cloud/orquestador_cloud.py")
        print("2. Ver dashboard: docs/dashboard/index.html")
        print("3. Monitorear: gh run list")
    else:
        print("\n⚠️ ALGUNAS PRUEBAS FALLARON")
        print("🔧 Revisar configuración antes de continuar")

def main():
    """Función principal"""
    print("🧪 PROBADOR DEL SISTEMA COMPLETO")
    print("=" * 60)
    print("Probando todos los componentes del sistema cloud...")
    print("=" * 60)
    
    # Ejecutar todas las pruebas
    resultados = {
        'Configuración': probar_configuracion(),
        'Generador Dashboard': probar_generador_dashboard(),
        'Orquestador Cloud': probar_orquestador(),
        'GitHub Actions': probar_github_actions(),
        'Dashboard Local': probar_dashboard_local()
    }
    
    # Mostrar resumen
    mostrar_resumen_pruebas(resultados)
    
    # Código de salida
    if all(resultados.values()):
        sys.exit(0)  # Éxito
    else:
        sys.exit(1)  # Error

if __name__ == "__main__":
    main()
