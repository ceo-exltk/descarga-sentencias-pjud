#!/usr/bin/env python3
"""
Configurador de GitHub Actions
Script para configurar automáticamente el sistema cloud
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def verificar_github_cli():
    """Verificar que GitHub CLI esté instalado"""
    try:
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ GitHub CLI instalado")
            return True
        else:
            print("❌ GitHub CLI no encontrado")
            return False
    except FileNotFoundError:
        print("❌ GitHub CLI no encontrado")
        return False

def verificar_autenticacion():
    """Verificar autenticación con GitHub"""
    try:
        result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Autenticado con GitHub")
            return True
        else:
            print("❌ No autenticado con GitHub")
            print("💡 Ejecutar: gh auth login")
            return False
    except Exception as e:
        print(f"❌ Error verificando autenticación: {e}")
        return False

def configurar_secretos():
    """Configurar secretos en GitHub"""
    print("\n🔧 CONFIGURANDO SECRETOS DE GITHUB")
    print("=" * 50)
    
    # Secretos de Supabase
    supabase_url = "https://wluachczgiyrmrhdpcue.supabase.co"
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndsdWFjaGN6Z2l5cm1yaGRwY3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5MjA1NDcsImV4cCI6MjA3MjQ5NjU0N30.gXSqEYy_LFp951EnBhFxU_7RSf5VbJXRc2GlLn7OB7I"
    
    print("📝 Configurando secretos de Supabase...")
    
    try:
        # Configurar SUPABASE_URL
        result = subprocess.run([
            'gh', 'secret', 'set', 'SUPABASE_URL', 
            '--body', supabase_url
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SUPABASE_URL configurado")
        else:
            print(f"❌ Error configurando SUPABASE_URL: {result.stderr}")
            return False
        
        # Configurar SUPABASE_ANON_KEY
        result = subprocess.run([
            'gh', 'secret', 'set', 'SUPABASE_ANON_KEY',
            '--body', supabase_key
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SUPABASE_ANON_KEY configurado")
        else:
            print(f"❌ Error configurando SUPABASE_ANON_KEY: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando secretos: {e}")
        return False

def agregar_workflow():
    """Agregar workflow de GitHub Actions"""
    print("\n📄 AGREGANDO WORKFLOW DE GITHUB ACTIONS")
    print("=" * 50)
    
    # Crear directorio de workflows si no existe
    workflows_dir = Path(".github/workflows")
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    # Contenido del workflow
    workflow_content = '''name: Descarga Incremental de Sentencias

on:
  # Disparar manualmente con parámetros
  workflow_dispatch:
    inputs:
      tribunal_type:
        description: 'Tipo de tribunal'
        required: true
        default: 'Corte_Suprema'
        type: choice
        options:
          - Corte_Suprema
          - Corte_de_Apelaciones
          - Laborales
          - Penales
          - Familia
          - Civiles
          - Cobranza
      fecha_desde:
        description: 'Fecha desde (YYYY-MM-DD)'
        required: true
        default: '2024-01-01'
        type: string
      fecha_hasta:
        description: 'Fecha hasta (YYYY-MM-DD)'
        required: true
        default: '2024-12-31'
        type: string
      paginas_maximas:
        description: 'Páginas máximas a procesar'
        required: true
        default: '10'
        type: string
      workers_paralelos:
        description: 'Workers paralelos'
        required: true
        default: '3'
        type: string
  
  # Disparar automáticamente cada 6 horas
  schedule:
    - cron: '0 */6 * * *'
  
  # Disparar en push a main (para testing)
  push:
    branches: [ main ]
    paths: [ 'scripts/cloud/**' ]

jobs:
  descarga-incremental:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout código
      uses: actions/checkout@v4
    
    - name: Configurar Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Instalar dependencias
      run: |
        python -m pip install --upgrade pip
        pip install requests beautifulsoup4
    
    - name: Ejecutar descarga incremental
      env:
        SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
        SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
        TRIBUNAL_TYPE: ${{ inputs.tribunal_type || 'Corte_Suprema' }}
        FECHA_DESDE: ${{ inputs.fecha_desde || '2024-01-01' }}
        FECHA_HASTA: ${{ inputs.fecha_hasta || '2024-12-31' }}
        PAGINAS_MAXIMAS: ${{ inputs.paginas_maximas || '10' }}
        WORKERS_PARALELOS: ${{ inputs.workers_paralelos || '3' }}
      run: |
        python scripts/cloud/descarga_cloud_incremental.py
    
    - name: Subir logs (si hay errores)
      if: failure()
      uses: actions/upload-artifact@v3
      with:
        name: logs-error-${{ github.run_number }}
        path: |
          logs/
          *.log
        retention-days: 30
'''
    
    # Escribir archivo de workflow
    workflow_file = workflows_dir / "descarga-incremental.yml"
    with open(workflow_file, 'w', encoding='utf-8') as f:
        f.write(workflow_content)
    
    print("✅ Workflow creado")
    
    # Hacer commit y push
    try:
        subprocess.run(['git', 'add', '.github/workflows/descarga-incremental.yml'], check=True)
        subprocess.run(['git', 'commit', '-m', '➕ Agregar workflow de GitHub Actions'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("✅ Workflow subido a GitHub")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error subiendo workflow: {e}")
        return False

def configurar_variables_entorno():
    """Configurar variables de entorno locales"""
    print("\n🔧 CONFIGURANDO VARIABLES DE ENTORNO")
    print("=" * 50)
    
    # Obtener información del repositorio
    try:
        result = subprocess.run(['gh', 'repo', 'view', '--json', 'name,owner'], capture_output=True, text=True)
        if result.returncode == 0:
            repo_info = json.loads(result.stdout)
            repo_name = repo_info['name']
            repo_owner = repo_info['owner']['login']
            github_repo = f"{repo_owner}/{repo_name}"
        else:
            print("❌ Error obteniendo información del repositorio")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Crear archivo de configuración
    config = {
        "github_repo": github_repo,
        "supabase_url": "https://wluachczgiyrmrhdpcue.supabase.co",
        "supabase_anon_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndsdWFjaGN6Z2l5cm1yaGRwY3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5MjA1NDcsImV4cCI6MjA3MjQ5NjU0N30.gXSqEYy_LFp951EnBhFxU_7RSf5VbJXRc2GlLn7OB7I"
    }
    
    config_file = Path("config/github_actions_config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuración guardada en {config_file}")
    print(f"📝 Repositorio: {github_repo}")
    
    # Crear script de configuración de entorno
    env_script = """#!/bin/bash
# Configuración de variables de entorno para GitHub Actions

export GITHUB_REPO="{github_repo}"
export SUPABASE_URL="https://wluachczgiyrmrhdpcue.supabase.co"
export SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndsdWFjaGN6Z2l5cm1yaGRwY3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5MjA1NDcsImV4cCI6MjA3MjQ5NjU0N30.gXSqEYy_LFp951EnBhFxU_7RSf5VbJXRc2GlLn7OB7I"

echo "✅ Variables de entorno configuradas"
echo "📝 Repositorio: $GITHUB_REPO"
echo "🗄️ Supabase URL: $SUPABASE_URL"
""".format(github_repo=github_repo)
    
    env_file = Path("configurar_env.sh")
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_script)
    
    os.chmod(env_file, 0o755)
    print(f"✅ Script de configuración creado: {env_file}")
    
    return True

def probar_configuracion():
    """Probar la configuración"""
    print("\n🧪 PROBANDO CONFIGURACIÓN")
    print("=" * 50)
    
    try:
        # Probar orquestador
        print("🔍 Probando orquestador...")
        result = subprocess.run([
            'python3', 'scripts/cloud/orquestador_cloud.py', '--test'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Orquestador funcionando")
        else:
            print(f"⚠️ Orquestador con advertencias: {result.stderr}")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("⏰ Timeout en prueba del orquestador")
        return False
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 CONFIGURADOR DE GITHUB ACTIONS")
    print("=" * 60)
    print("Configurando sistema de descarga cloud...")
    print("=" * 60)
    
    # Verificar requisitos
    if not verificar_github_cli():
        print("\n💡 Instalar GitHub CLI:")
        print("   brew install gh")
        print("   gh auth login")
        return False
    
    if not verificar_autenticacion():
        print("\n💡 Autenticarse con GitHub:")
        print("   gh auth login")
        return False
    
    # Configurar sistema
    print("\n🔧 INICIANDO CONFIGURACIÓN")
    print("=" * 60)
    
    # 1. Configurar secretos
    if not configurar_secretos():
        print("❌ Error configurando secretos")
        return False
    
    # 2. Agregar workflow
    if not agregar_workflow():
        print("❌ Error agregando workflow")
        return False
    
    # 3. Configurar variables de entorno
    if not configurar_variables_entorno():
        print("❌ Error configurando variables")
        return False
    
    # 4. Probar configuración
    if not probar_configuracion():
        print("⚠️ Advertencias en prueba")
    
    print("\n🎉 CONFIGURACIÓN COMPLETADA")
    print("=" * 60)
    print("✅ Secretos configurados en GitHub")
    print("✅ Workflow agregado")
    print("✅ Variables de entorno configuradas")
    print("\n🚀 PRÓXIMOS PASOS:")
    print("1. Ejecutar: source configurar_env.sh")
    print("2. Probar: python3 scripts/cloud/orquestador_cloud.py")
    print("3. Ver workflows: gh run list")
    print("\n📚 Documentación: docs/CONFIGURACION_GITHUB_ACTIONS.md")

if __name__ == "__main__":
    main()
