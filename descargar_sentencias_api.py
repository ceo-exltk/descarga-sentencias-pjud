#!/usr/bin/env python3
"""
Script para descargar sentencias por fecha específica
Usado por GitHub Actions workflow
Formato actualizado basado en la investigación con Playwright
"""

import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

class DescargadorSentencias:
    """Descargador de sentencias para GitHub Actions"""
    
    def __init__(self):
        self.base_url = "https://juris.pjud.cl"
        self.session = requests.Session()
        
        # Headers correctos
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.31 Safari/537.36',
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://juris.pjud.cl',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        })
        
        # Configuración de tribunales
        self.tribunales = {
            'Corte_Suprema': {'id': '528', 'descripcion': 'Corte Suprema'},
            'Corte_de_Apelaciones': {'id': '168', 'descripcion': 'Cortes de Apelaciones'},
            'Laborales': {'id': '271', 'descripcion': 'Tribunales Laborales'},
            'Penales': {'id': '268', 'descripcion': 'Tribunales Penales'},
            'Familia': {'id': '270', 'descripcion': 'Tribunales de Familia'},
            'Civiles': {'id': '328', 'descripcion': 'Tribunales Civiles'},
            'Cobranza': {'id': '269', 'descripcion': 'Tribunales de Cobranza'}
        }
    
    def _get_token(self):
        """Obtener token CSRF"""
        try:
            response = self.session.get(f"{self.base_url}/busqueda/lista_buscadores")
            soup = BeautifulSoup(response.text, 'html.parser')
            token_meta = soup.find('meta', {'name': 'csrf-token'})
            
            if token_meta and 'content' in token_meta.attrs:
                return token_meta['content']
            
            return None
        except Exception as e:
            print(f"⚠️ Error obteniendo token: {e}")
            return None
    
    def _establish_context(self, tribunal_name):
        """Establecer contexto del tribunal"""
        try:
            response = self.session.get(f"{self.base_url}/busqueda?{tribunal_name}")
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️ Error estableciendo contexto: {e}")
            return False
    
    def descargar_sentencias_fecha(self, fecha_desde, fecha_hasta):
        """Descargar sentencias para un rango de fechas específico"""
        print(f"📅 Descargando sentencias: {fecha_desde} a {fecha_hasta}")
        print("=" * 60)
        
        todas_sentencias = []
        total_por_tribunal = {}
        
        for tribunal_name, tribunal_config in self.tribunales.items():
            print(f"\n🏛️ {tribunal_config['descripcion']}...")
            
            try:
                # Obtener token
                token = self._get_token()
                if not token:
                    print(f"❌ No se pudo obtener token")
                    continue
                
                # Establecer contexto
                if not self._establish_context(tribunal_name):
                    print(f"❌ No se pudo establecer contexto")
                    continue
                
                # Formato correcto: multipart/form-data
                data = {
                    '_token': token,
                    'id_buscador': tribunal_config['id'],
                    'filtros': json.dumps({
                        "rol": "",
                        "era": "",
                        "fec_desde": fecha_desde,
                        "fec_hasta": fecha_hasta,
                        "tipo_norma": "",
                        "num_norma": "",
                        "num_art": "",
                        "num_inciso": "",
                        "todas": "",
                        "algunas": "",
                        "excluir": "",
                        "literal": "",
                        "proximidad": "",
                        "distancia": "",
                        "analisis_s": "",
                        "submaterias": "",
                        "facetas_seleccionadas": [],
                        "filtros_omnibox": [],
                        "ids_comunas_seleccionadas_mapa": []
                    }),
                    'numero_filas_paginacion': '100',
                    'offset_paginacion': '0',
                    'orden': 'recientes',
                    'personalizacion': 'false'
                }
                
                headers = {
                    'Referer': f'https://juris.pjud.cl/busqueda?{tribunal_name}',
                    'Accept': 'text/html, */*; q=0.01'
                }
                
                response = self.session.post(
                    f"{self.base_url}/busqueda/buscar_sentencias",
                    data=data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if 'response' in result:
                        num_found = result['response'].get('numFound', 0)
                        docs = result['response'].get('docs', [])
                        
                        print(f"   📊 Encontradas: {num_found}")
                        print(f"   📄 Descargadas: {len(docs)}")
                        
                        if len(docs) > 0:
                            todas_sentencias.extend(docs)
                            total_por_tribunal[tribunal_name] = {
                                'total': num_found,
                                'descargadas': len(docs),
                                'tribunal': tribunal_config['descripcion']
                            }
                
                time.sleep(1)  # Delay entre tribunales
                
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
        
        return todas_sentencias, total_por_tribunal
    
    def guardar_resultados(self, sentencias, total_por_tribunal, fecha_desde, fecha_hasta):
        """Guardar resultados en formato JSON"""
        output_dir = Path("output/descarga_api")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar sentencias
        fecha_str = fecha_desde.replace('-', '')
        sentencias_file = output_dir / f"sentencias_{fecha_str}.json"
        
        with open(sentencias_file, 'w', encoding='utf-8') as f:
            json.dump(sentencias, f, ensure_ascii=False, indent=2)
        
        # Guardar para Supabase (formato compatible)
        supabase_file = output_dir / "sentencias_para_supabase.json"
        with open(supabase_file, 'w', encoding='utf-8') as f:
            json.dump(sentencias, f, ensure_ascii=False, indent=2)
        
        # Guardar resumen
        resumen = {
            'fecha_ejecucion': datetime.now().isoformat(),
            'rango_fechas': {
                'desde': fecha_desde,
                'hasta': fecha_hasta
            },
            'total_sentencias': len(sentencias),
            'por_tribunal': total_por_tribunal,
            'archivo_sentencias': str(sentencias_file),
            'archivo_supabase': str(supabase_file)
        }
        
        resumen_file = output_dir / f"resumen_{fecha_str}.json"
        with open(resumen_file, 'w', encoding='utf-8') as f:
            json.dump(resumen, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Archivos guardados:")
        print(f"   - {sentencias_file}")
        print(f"   - {supabase_file}")
        print(f"   - {resumen_file}")
        
        return sentencias_file, supabase_file, resumen_file

def main():
    """Función principal"""
    if len(sys.argv) < 3:
        print("Uso: python descargar_sentencias_api.py FECHA_DESDE FECHA_HASTA")
        print("Ejemplo: python descargar_sentencias_api.py 2025-03-01 2025-03-01")
        sys.exit(1)
    
    fecha_desde = sys.argv[1]
    fecha_hasta = sys.argv[2]
    
    # Validar formato de fecha
    try:
        datetime.strptime(fecha_desde, '%Y-%m-%d')
        datetime.strptime(fecha_hasta, '%Y-%m-%d')
    except ValueError:
        print("❌ Error: Las fechas deben estar en formato YYYY-MM-DD")
        sys.exit(1)
    
    print("🚀 DESCARGADOR DE SENTENCIAS PJUD")
    print("Formato actualizado con investigación Playwright")
    print("=" * 60)
    
    descargador = DescargadorSentencias()
    sentencias, total_por_tribunal = descargador.descargar_sentencias_fecha(fecha_desde, fecha_hasta)
    
    if sentencias:
        archivos = descargador.guardar_resultados(sentencias, total_por_tribunal, fecha_desde, fecha_hasta)
        
        print("\n" + "=" * 60)
        print(f"✅ DESCARGA COMPLETADA")
        print(f"📊 Total de sentencias: {len(sentencias)}")
        print("\n📋 POR TRIBUNAL:")
        for tribunal, info in total_por_tribunal.items():
            print(f"   {info['tribunal']}: {info['descargadas']} de {info['total']}")
    else:
        print("\n⚠️ No se encontraron sentencias para el rango especificado")
        sys.exit(1)

if __name__ == "__main__":
    main()
