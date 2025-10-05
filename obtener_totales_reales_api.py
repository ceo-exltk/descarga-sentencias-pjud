#!/usr/bin/env python3
"""
Script para obtener los totales reales de sentencias por tipo de tribunal
consultando directamente la API del PJUD (juris.pjud.cl)
"""

import requests
import json
import time
from datetime import datetime
import re

class PJUDApiClient:
    def __init__(self):
        self.base_url = "https://juris.pjud.cl"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-CL,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Tipos de tribunal como aparecen en la página oficial
        self.tipos_tribunal = {
            'Corte Suprema': 'Corte_Suprema',
            'Corte de Apelaciones': 'Corte_de_Apelaciones', 
            'Laborales': 'Laborales',
            'Familia': 'Familia',
            'Civiles': 'Civiles',
            'Penales': 'Penales',
            'Cobranza': 'Cobranza',
            'Salud CS': 'Salud_CS'
        }
    
    def obtener_csrf_token(self):
        """Obtiene el token CSRF de la página de búsqueda"""
        try:
            print("🔍 Obteniendo token CSRF...")
            response = self.session.get(f"{self.base_url}/busqueda")
            response.raise_for_status()
            
            # Buscar el token CSRF en el HTML
            csrf_match = re.search(r'name="csrf-token"\s+content="([^"]+)"', response.text)
            if csrf_match:
                token = csrf_match.group(1)
                print(f"✅ Token CSRF obtenido: {token[:20]}...")
                return token
            else:
                print("❌ No se encontró token CSRF")
                return None
                
        except Exception as e:
            print(f"❌ Error obteniendo CSRF token: {e}")
            return None
    
    def consultar_total_por_tipo(self, tipo_tribunal, csrf_token):
        """Consulta el total de sentencias para un tipo de tribunal específico"""
        try:
            print(f"📊 Consultando total para: {tipo_tribunal}")
            
            # URL de búsqueda específica para el tipo de tribunal
            url = f"{self.base_url}/busqueda?{self.tipos_tribunal[tipo_tribunal]}"
            
            # Realizar búsqueda sin filtros adicionales para obtener el total
            search_data = {
                'csrf-token': csrf_token,
                'tipo_tribunal': self.tipos_tribunal[tipo_tribunal],
                'fecha_desde': '',
                'fecha_hasta': '',
                'texto': '',
                'buscar': 'Buscar'
            }
            
            response = self.session.post(f"{self.base_url}/busqueda", data=search_data)
            response.raise_for_status()
            
            # Buscar el total en la respuesta HTML
            # Patrón común: "Se encontraron X resultados"
            total_match = re.search(r'Se encontraron\s+([\d,\.]+)\s+resultados?', response.text)
            if total_match:
                total_str = total_match.group(1).replace(',', '').replace('.', '')
                total = int(total_str)
                print(f"✅ {tipo_tribunal}: {total:,} resultados")
                return total
            
            # Patrón alternativo: buscar en elementos de paginación
            pagination_match = re.search(r'Total:\s*([\d,\.]+)', response.text)
            if pagination_match:
                total_str = pagination_match.group(1).replace(',', '').replace('.', '')
                total = int(total_str)
                print(f"✅ {tipo_tribunal}: {total:,} resultados (paginación)")
                return total
            
            # Si no encuentra el total, intentar contar páginas
            pages_match = re.findall(r'página\s+\d+\s+de\s+(\d+)', response.text)
            if pages_match:
                total_pages = int(pages_match[0])
                # Estimación: 20 resultados por página (valor típico)
                estimated_total = total_pages * 20
                print(f"✅ {tipo_tribunal}: ~{estimated_total:,} resultados (estimado por páginas)")
                return estimated_total
            
            print(f"⚠️ No se pudo determinar el total para {tipo_tribunal}")
            return 0
            
        except Exception as e:
            print(f"❌ Error consultando {tipo_tribunal}: {e}")
            return 0
    
    def obtener_todos_los_totales(self):
        """Obtiene los totales para todos los tipos de tribunal"""
        print("🚀 INICIANDO CONSULTA DE TOTALES REALES")
        print("=" * 50)
        
        # Obtener token CSRF
        csrf_token = self.obtener_csrf_token()
        if not csrf_token:
            print("❌ No se pudo obtener token CSRF. Abortando.")
            return {}
        
        resultados = {}
        total_general = 0
        
        for tipo_tribunal in self.tipos_tribunal.keys():
            try:
                total = self.consultar_total_por_tipo(tipo_tribunal, csrf_token)
                resultados[tipo_tribunal] = total
                total_general += total
                
                # Pausa para evitar rate limiting
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error procesando {tipo_tribunal}: {e}")
                resultados[tipo_tribunal] = 0
        
        print("\n" + "=" * 50)
        print("📊 RESUMEN DE TOTALES REALES")
        print("=" * 50)
        
        for tipo, total in resultados.items():
            print(f"{tipo:20} | {total:>10,} sentencias")
        
        print("-" * 50)
        print(f"{'TOTAL GENERAL':20} | {total_general:>10,} sentencias")
        
        return resultados

def main():
    """Función principal"""
    print("🔍 CONSULTANDO TOTALES REALES DEL PJUD")
    print("=" * 50)
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        client = PJUDApiClient()
        resultados = client.obtener_todos_los_totales()
        
        # Guardar resultados en archivo JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"totales_reales_pjud_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'totales_por_tribunal': resultados,
                'total_general': sum(resultados.values()),
                'fuente': 'API oficial PJUD (juris.pjud.cl)'
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: {filename}")
        print("✅ Consulta completada exitosamente")
        
        return resultados
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return {}

if __name__ == "__main__":
    main()
