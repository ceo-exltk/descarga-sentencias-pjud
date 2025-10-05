#!/usr/bin/env python3
"""
Orquestador Cloud - Control de GitHub Actions
Sistema para disparar y monitorear descargas en la nube
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

class OrquestadorCloud:
    """Orquestador para controlar descargas en la nube"""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repo = os.getenv('GITHUB_REPO', 'tu-usuario/descarga_sentencias')
        self.github_owner = self.github_repo.split('/')[0]
        self.github_repo_name = self.github_repo.split('/')[1]
        
        if not self.github_token:
            print("❌ Error: GITHUB_TOKEN requerido")
            print("💡 Configurar: export GITHUB_TOKEN='tu_token'")
            sys.exit(1)
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'OrquestadorCloud/1.0'
        })
    
    def disparar_descarga_incremental(self, tribunal_type: str, fecha_desde: str, fecha_hasta: str, paginas_maximas: int = 10):
        """Disparar descarga incremental en GitHub Actions"""
        print(f"🚀 Disparando descarga incremental...")
        print(f"   🏛️ Tribunal: {tribunal_type}")
        print(f"   📅 Período: {fecha_desde} a {fecha_hasta}")
        print(f"   📄 Páginas: {paginas_maximas}")
        
        # URL de la API de GitHub Actions
        url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo_name}/actions/workflows/descarga-incremental.yml/dispatches"
        
        # Datos del dispatch
        data = {
            'ref': 'main',
            'inputs': {
                'tribunal_type': tribunal_type,
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
                'paginas_maximas': str(paginas_maximas),
                'workers_paralelos': '3'
            }
        }
        
        try:
            response = self.session.post(url, json=data)
            
            if response.status_code == 204:
                print("✅ Descarga disparada exitosamente")
                return True
            else:
                print(f"❌ Error disparando descarga: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def disparar_descarga_historica(self, tribunal_type: str):
        """Disparar descarga histórica completa"""
        print(f"🚀 Disparando descarga histórica para {tribunal_type}...")
        
        # Usar fechas amplias para descarga histórica
        fecha_desde = '2000-01-01'
        fecha_hasta = '2024-12-31'
        paginas_maximas = 100
        
        return self.disparar_descarga_incremental(tribunal_type, fecha_desde, fecha_hasta, paginas_maximas)
    
    def obtener_estado_workflows(self) -> List[Dict[str, Any]]:
        """Obtener estado de workflows ejecutándose"""
        try:
            url = f"https://api.github.com/repos/{self.github_owner}/{self.github_repo_name}/actions/runs"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('workflow_runs', [])
            else:
                print(f"❌ Error obteniendo workflows: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def monitorear_workflows(self):
        """Monitorear workflows en ejecución"""
        print("🔍 Monitoreando workflows...")
        
        workflows = self.obtener_estado_workflows()
        
        if not workflows:
            print("📭 No hay workflows ejecutándose")
            return
        
        print(f"📊 Workflows encontrados: {len(workflows)}")
        print("-" * 60)
        
        for workflow in workflows[:5]:  # Mostrar últimos 5
            nombre = workflow.get('name', 'N/A')
            estado = workflow.get('status', 'N/A')
            conclusion = workflow.get('conclusion', 'N/A')
            created_at = workflow.get('created_at', 'N/A')
            html_url = workflow.get('html_url', '')
            
            # Determinar emoji según estado
            if estado == 'completed':
                if conclusion == 'success':
                    emoji = "✅"
                else:
                    emoji = "❌"
            elif estado == 'in_progress':
                emoji = "🔄"
            elif estado == 'queued':
                emoji = "⏳"
            else:
                emoji = "❓"
            
            print(f"{emoji} {nombre}")
            print(f"   Estado: {estado}")
            print(f"   Conclusión: {conclusion}")
            print(f"   Creado: {created_at}")
            print(f"   URL: {html_url}")
            print()
    
    def programar_descarga_diaria(self, tribunal_type: str):
        """Programar descarga diaria para un tribunal"""
        print(f"📅 Programando descarga diaria para {tribunal_type}...")
        
        # Fecha de ayer
        fecha_ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        
        return self.disparar_descarga_incremental(
            tribunal_type=tribunal_type,
            fecha_desde=fecha_ayer,
            fecha_hasta=fecha_hoy,
            paginas_maximas=20
        )
    
    def ejecutar_descarga_completa_historica(self):
        """Ejecutar descarga histórica completa de todos los tribunales"""
        tribunales = [
            'Corte_Suprema',
            'Corte_de_Apelaciones', 
            'Laborales',
            'Penales',
            'Familia',
            'Civiles',
            'Cobranza'
        ]
        
        print("🚀 Iniciando descarga histórica completa...")
        print(f"🏛️ Tribunales: {len(tribunales)}")
        
        for i, tribunal in enumerate(tribunales, 1):
            print(f"\n📋 Procesando {i}/{len(tribunales)}: {tribunal}")
            
            exito = self.disparar_descarga_historica(tribunal)
            
            if exito:
                print(f"✅ {tribunal} disparado exitosamente")
            else:
                print(f"❌ Error disparando {tribunal}")
            
            # Pausa entre disparos
            if i < len(tribunales):
                print("⏸️ Esperando 30 segundos antes del siguiente...")
                time.sleep(30)
        
        print("\n🎉 Descarga histórica completa disparada")

def mostrar_menu():
    """Mostrar menú principal"""
    print("🌐 ORQUESTADOR CLOUD - CONTROL DE GITHUB ACTIONS")
    print("=" * 60)
    print("1. 🔍 Monitorear workflows")
    print("2. 📥 Descarga incremental (por fecha)")
    print("3. 📚 Descarga histórica (un tribunal)")
    print("4. 🏛️ Descarga histórica completa (todos los tribunales)")
    print("5. 📅 Programar descarga diaria")
    print("6. 🚪 Salir")
    print("=" * 60)

def main():
    """Función principal"""
    orquestador = OrquestadorCloud()
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("Seleccione una opción (1-6): ").strip()
            
            if opcion == "1":
                orquestador.monitorear_workflows()
            
            elif opcion == "2":
                print("\n📥 DESCARGA INCREMENTAL")
                tribunal = input("Tipo de tribunal: ").strip() or "Corte_Suprema"
                fecha_desde = input("Fecha desde (YYYY-MM-DD): ").strip() or "2024-01-01"
                fecha_hasta = input("Fecha hasta (YYYY-MM-DD): ").strip() or "2024-12-31"
                paginas = int(input("Páginas máximas: ").strip() or "10")
                
                orquestador.disparar_descarga_incremental(tribunal, fecha_desde, fecha_hasta, paginas)
            
            elif opcion == "3":
                print("\n📚 DESCARGA HISTÓRICA")
                tribunal = input("Tipo de tribunal: ").strip() or "Corte_Suprema"
                orquestador.disparar_descarga_historica(tribunal)
            
            elif opcion == "4":
                print("\n🏛️ DESCARGA HISTÓRICA COMPLETA")
                confirmar = input("¿Ejecutar descarga de todos los tribunales? (s/n): ").strip().lower()
                if confirmar == 's':
                    orquestador.ejecutar_descarga_completa_historica()
                else:
                    print("❌ Operación cancelada")
            
            elif opcion == "5":
                print("\n📅 DESCARGA DIARIA")
                tribunal = input("Tipo de tribunal: ").strip() or "Corte_Suprema"
                orquestador.programar_descarga_diaria(tribunal)
            
            elif opcion == "6":
                print("👋 ¡Hasta luego!")
                break
            
            else:
                print("❌ Opción inválida")
            
            if opcion in ["1", "2", "3", "4", "5"]:
                input("\n⏸️ Presione Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n👋 Orquestador detenido")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\n⏸️ Presione Enter para continuar...")

if __name__ == "__main__":
    main()
