#!/usr/bin/env python3
"""
Script para ejecutar el workflow con carga automática a Supabase
"""

import os
import sys
import subprocess
from datetime import datetime, timedelta

def ejecutar_workflow_con_supabase(fecha=None, cargar_supabase=True):
    """Ejecuta el workflow con carga automática a Supabase"""
    
    if not fecha:
        # Usar la fecha de ayer por defecto
        fecha = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"🚀 EJECUTANDO WORKFLOW CON SUPABASE")
    print("=" * 50)
    print(f"📅 Fecha: {fecha}")
    print(f"🔄 Cargar a Supabase: {'Sí' if cargar_supabase else 'No'}")
    print()
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('.github/workflows/descargar-sentencias-supabase.yml'):
        print("❌ No se encontró el workflow de Supabase")
        print("   Asegúrate de estar en el directorio correcto")
        return False
    
    # Verificar que tenemos git configurado
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ No se encontró repositorio git")
            return False
    except FileNotFoundError:
        print("❌ Git no está instalado")
        return False
    
    # Hacer commit de cambios si los hay
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', f'🔄 Actualización automática - {fecha}'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("✅ Cambios sincronizados con GitHub")
    except subprocess.CalledProcessError:
        print("ℹ️  No hay cambios para sincronizar")
    
    # Ejecutar el workflow usando GitHub CLI si está disponible
    try:
        cmd = [
            'gh', 'workflow', 'run', 'descargar-sentencias-supabase.yml',
            '-f', f'fecha={fecha}',
            '-f', f'cargar_supabase={str(cargar_supabase).lower()}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Workflow ejecutado exitosamente")
            print(f"   Fecha: {fecha}")
            print(f"   Carga a Supabase: {'Habilitada' if cargar_supabase else 'Deshabilitada'}")
            print()
            print("📊 Monitorea el progreso en:")
            print("   https://github.com/ceo-exltk/descarga-sentencias-pjud/actions")
            return True
        else:
            print(f"❌ Error ejecutando workflow: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ GitHub CLI no está instalado")
        print("   Instala GitHub CLI o ejecuta el workflow manualmente")
        print("   https://github.com/ceo-exltk/descarga-sentencias-pjud/actions")
        return False

def mostrar_instrucciones_manuales():
    """Muestra instrucciones para ejecutar manualmente"""
    print("📋 INSTRUCCIONES MANUALES")
    print("=" * 50)
    print("1. Ve a https://github.com/ceo-exltk/descarga-sentencias-pjud/actions")
    print("2. Selecciona 'Descargar y Cargar a Supabase'")
    print("3. Click 'Run workflow'")
    print("4. Configura:")
    print("   - Fecha: YYYY-MM-DD")
    print("   - Cargar a Supabase: ✅ Marcado")
    print("5. Click 'Run workflow'")

def main():
    if len(sys.argv) >= 2:
        fecha = sys.argv[1]
    else:
        fecha = None
    
    if len(sys.argv) >= 3:
        cargar_supabase = sys.argv[2].lower() in ['true', '1', 'yes', 'si', 'sí']
    else:
        cargar_supabase = True
    
    success = ejecutar_workflow_con_supabase(fecha, cargar_supabase)
    
    if not success:
        print()
        mostrar_instrucciones_manuales()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
