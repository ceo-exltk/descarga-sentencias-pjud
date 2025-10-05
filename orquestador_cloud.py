#!/usr/bin/env python3
"""
Orquestador para el sistema cloud de descarga de sentencias
Permite ejecutar workflows de GitHub Actions desde local
"""

import subprocess
import json
import time
import requests
from datetime import datetime
from pathlib import Path

class CloudOrchestrator:
    def __init__(self):
        self.repo = "ceo-exltk/descarga-sentencias-pjud"
        self.workflow_name = "obtener-totales-reales.yml"
        
    def verificar_github_cli(self):
        """Verifica que GitHub CLI esté instalado y configurado"""
        try:
            result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ GitHub CLI instalado")
                return True
            else:
                print("❌ GitHub CLI no encontrado")
                return False
        except FileNotFoundError:
            print("❌ GitHub CLI no instalado")
            return False
    
    def verificar_autenticacion(self):
        """Verifica que esté autenticado con GitHub"""
        try:
            result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Autenticado con GitHub")
                return True
            else:
                print("❌ No autenticado con GitHub")
                return False
        except Exception as e:
            print(f"❌ Error verificando autenticación: {e}")
            return False
    
    def ejecutar_workflow_obtener_totales(self):
        """Ejecuta el workflow para obtener totales reales"""
        try:
            print("🚀 EJECUTANDO WORKFLOW: Obtener Totales Reales")
            print("=" * 50)
            
            # Ejecutar workflow
            cmd = [
                'gh', 'workflow', 'run', self.workflow_name,
                '--repo', self.repo
            ]
            
            print(f"📤 Ejecutando: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Workflow ejecutado exitosamente")
                print(f"📋 Salida: {result.stdout}")
                return True
            else:
                print(f"❌ Error ejecutando workflow: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error ejecutando workflow: {e}")
            return False
    
    def monitorear_workflow(self, timeout_minutes=10):
        """Monitorea el estado del workflow"""
        print(f"⏳ Monitoreando workflow (timeout: {timeout_minutes} min)")
        
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        
        while time.time() - start_time < timeout_seconds:
            try:
                # Obtener estado del workflow
                cmd = ['gh', 'run', 'list', '--repo', self.repo, '--limit', '1']
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:  # Skip header
                        status_line = lines[1]
                        if 'completed' in status_line:
                            print("✅ Workflow completado")
                            return True
                        elif 'in_progress' in status_line:
                            print("🔄 Workflow en progreso...")
                        elif 'queued' in status_line:
                            print("⏳ Workflow en cola...")
                        else:
                            print(f"📊 Estado: {status_line}")
                
                time.sleep(30)  # Verificar cada 30 segundos
                
            except Exception as e:
                print(f"⚠️ Error monitoreando: {e}")
                time.sleep(30)
        
        print("⏰ Timeout alcanzado")
        return False
    
    def verificar_resultados(self):
        """Verifica que los resultados estén disponibles en GitHub Pages"""
        try:
            print("🔍 VERIFICANDO RESULTADOS EN GITHUB PAGES")
            print("=" * 50)
            
            # URL del dashboard
            dashboard_url = f"https://{self.repo.split('/')[0]}.github.io/{self.repo.split('/')[1]}/dashboard_tribunales_final.html"
            
            print(f"🌐 Dashboard: {dashboard_url}")
            
            # Verificar que el dashboard esté disponible
            response = requests.get(dashboard_url, timeout=30)
            if response.status_code == 200:
                print("✅ Dashboard disponible")
                return True
            else:
                print(f"❌ Dashboard no disponible (HTTP {response.status_code})")
                return False
                
        except Exception as e:
            print(f"❌ Error verificando resultados: {e}")
            return False
    
    def ejecutar_sistema_completo(self):
        """Ejecuta el sistema completo de obtención de totales reales"""
        print("🌍 SISTEMA CLOUD DE OBTENCIÓN DE TOTALES REALES")
        print("=" * 60)
        print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Verificar dependencias
        if not self.verificar_github_cli():
            print("❌ Instala GitHub CLI: https://cli.github.com/")
            return False
        
        if not self.verificar_autenticacion():
            print("❌ Autentícate con: gh auth login")
            return False
        
        # Ejecutar workflow
        if not self.ejecutar_workflow_obtener_totales():
            print("❌ No se pudo ejecutar el workflow")
            return False
        
        # Monitorear ejecución
        if not self.monitorear_workflow():
            print("⚠️ Workflow no completado en el tiempo esperado")
            return False
        
        # Verificar resultados
        if not self.verificar_resultados():
            print("⚠️ Resultados no disponibles aún")
            return False
        
        print("\n🎉 SISTEMA CLOUD COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print("✅ Totales reales obtenidos desde GitHub Actions")
        print("✅ Dashboard actualizado con datos reales")
        print("✅ Sistema funcionando correctamente")
        
        return True

def main():
    """Función principal"""
    print("☁️ ORQUESTADOR CLOUD - SISTEMA DE TOTALES REALES")
    print("=" * 60)
    print("Este script ejecuta el sistema cloud para obtener")
    print("los totales reales de sentencias del PJUD")
    print("=" * 60)
    
    try:
        orchestrator = CloudOrchestrator()
        success = orchestrator.ejecutar_sistema_completo()
        
        if success:
            print("\n🌐 Dashboard disponible en:")
            print("https://ceo-exltk.github.io/descarga-sentencias-pjud/dashboard_tribunales_final.html")
        else:
            print("\n❌ Sistema cloud no completado exitosamente")
            
    except KeyboardInterrupt:
        print("\n❌ Sistema interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error en sistema cloud: {e}")

if __name__ == "__main__":
    main()
