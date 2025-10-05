#!/usr/bin/env python3
"""
Script de actualización automática del dashboard
Ejecuta el script paralelo y actualiza GitHub Pages
"""

import subprocess
import sys
import os
from datetime import datetime

def actualizar_dashboard():
    """Ejecutar script paralelo y actualizar dashboard"""
    print(f"🔄 Actualizando dashboard automáticamente - {datetime.now()}")
    
    try:
        # 1. Ejecutar script paralelo
        print("📊 Ejecutando script paralelo...")
        result = subprocess.run([
            sys.executable, "dashboard_paralelo.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ Script paralelo ejecutado exitosamente")
            
            # 2. Hacer commit y push automático
            print("📤 Actualizando GitHub Pages...")
            
            # Git add
            subprocess.run(["git", "add", "docs/dashboard_data.json"], check=True)
            
            # Git commit
            commit_msg = f"🤖 Actualización automática - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            
            # Git push
            subprocess.run(["git", "push", "origin", "main"], check=True)
            
            print("✅ Dashboard actualizado en GitHub Pages")
            return True
            
        else:
            print(f"❌ Error ejecutando script paralelo: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error en actualización automática: {e}")
        return False

def main():
    """Función principal"""
    print("🤖 ACTUALIZACIÓN AUTOMÁTICA DEL DASHBOARD")
    print("=" * 50)
    
    success = actualizar_dashboard()
    
    if success:
        print("\n✅ Actualización completada exitosamente!")
        print("🌐 Dashboard disponible en: https://ceo-exltk.github.io/descarga-sentencias-pjud/")
    else:
        print("\n❌ Error en la actualización automática")
        sys.exit(1)

if __name__ == "__main__":
    main()
