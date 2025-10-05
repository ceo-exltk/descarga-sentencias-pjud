#!/usr/bin/env python3
"""
Descarga Cloud Incremental - GitHub Actions
Sistema de descarga con IPs dinámicas para carga incremental por fecha y tribunal
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

# Configuración de Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

# Parámetros de entrada (desde GitHub Actions)
TRIBUNAL_TYPE = os.getenv('TRIBUNAL_TYPE', 'Corte_Suprema')
FECHA_DESDE = os.getenv('FECHA_DESDE', '2024-01-01')
FECHA_HASTA = os.getenv('FECHA_HASTA', '2024-12-31')
PAGINAS_MAXIMAS = int(os.getenv('PAGINAS_MAXIMAS', '10'))
WORKERS_PARALELOS = int(os.getenv('WORKERS_PARALELOS', '3'))

class DescargaCloudIncremental:
    """Sistema de descarga incremental para GitHub Actions"""
    
    def __init__(self):
        self.base_url = "https://juris.pjud.cl"
        self.tribunal_type = TRIBUNAL_TYPE
        self.fecha_desde = FECHA_DESDE
        self.fecha_hasta = FECHA_HASTA
        self.paginas_maximas = PAGINAS_MAXIMAS
        self.workers_paralelos = WORKERS_PARALELOS
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Configurar sesión HTTP
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        # Estadísticas
        self.stats = {
            'sentencias_descargadas': 0,
            'sentencias_procesadas': 0,
            'sentencias_cargadas': 0,
            'errores': 0,
            'inicio': datetime.now()
        }
    
    def obtener_token_csrf(self) -> Optional[str]:
        """Obtener token CSRF del servidor"""
        try:
            response = self.session.get(f"{self.base_url}/busqueda?{self.tribunal_type}")
            if response.status_code == 200:
                # Buscar token en meta tags
                import re
                token_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', response.text)
                if token_match:
                    token = token_match.group(1)
                    self.session.headers['X-CSRF-TOKEN'] = token
                    return token
            return None
        except Exception as e:
            self.logger.error(f"Error obteniendo token CSRF: {e}")
            return None
    
    def buscar_sentencias_pagina(self, pagina: int) -> List[Dict[str, Any]]:
        """Buscar sentencias en una página específica"""
        try:
            # Obtener token CSRF
            token = self.obtener_token_csrf()
            if not token:
                self.logger.warning("No se pudo obtener token CSRF")
                return []
            
            # URL de búsqueda
            search_url = f"{self.base_url}/busqueda/buscar_sentencias"
            
            # Datos del POST
            post_data = {
                'pagina': str(pagina),
                'cantidad_registros': '10',
                'fecha_desde': self.fecha_desde,
                'fecha_hasta': self.fecha_hasta
            }
            
            # Añadir filtro específico del tribunal
            if self.tribunal_type == 'Corte_Suprema':
                post_data['corte_suprema'] = 'true'
            elif self.tribunal_type == 'Corte_de_Apelaciones':
                post_data['corte_apelaciones'] = 'true'
            elif self.tribunal_type == 'Laborales':
                post_data['laborales'] = 'true'
            elif self.tribunal_type == 'Penales':
                post_data['penales'] = 'true'
            elif self.tribunal_type == 'Familia':
                post_data['familia'] = 'true'
            elif self.tribunal_type == 'Civiles':
                post_data['civiles'] = 'true'
            elif self.tribunal_type == 'Cobranza':
                post_data['cobranza'] = 'true'
            
            # Headers específicos
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/busqueda?{self.tribunal_type}',
                'Origin': self.base_url
            }
            
            # Realizar petición
            response = self.session.post(search_url, data=post_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                sentencias = data.get('sentencias', data.get('results', []))
                self.logger.info(f"Página {pagina}: {len(sentencias)} sentencias encontradas")
                return sentencias
            elif response.status_code == 419:
                self.logger.error("🚨 BLOQUEO DETECTADO: HTTP 419")
                return []
            else:
                self.logger.warning(f"Error HTTP {response.status_code} en página {pagina}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error en página {pagina}: {e}")
            self.stats['errores'] += 1
            return []
    
    def procesar_sentencia(self, sentencia: Dict[str, Any]) -> Dict[str, Any]:
        """Procesar una sentencia individual"""
        try:
            # Extraer datos básicos
            rol_numero = sentencia.get('rol_numero', '')
            caratulado = sentencia.get('caratulado', '')
            fecha_sentencia = sentencia.get('fecha_sentencia', '')
            texto_completo = sentencia.get('texto_completo', '')
            
            # Procesar fecha
            fecha_procesada = self._procesar_fecha(fecha_sentencia)
            
            # Crear registro para Supabase
            registro = {
                'rol_numero': rol_numero,
                'rol_completo': rol_numero,
                'caratulado': caratulado,
                'caratulado_anonimizado': caratulado,
                'fallo_anonimizado': texto_completo,
                'fecha_sentencia': fecha_procesada,
                'fecha_actualizacion': datetime.now().date().isoformat(),
                'corte': self.tribunal_type,
                'tribunal_type': self.tribunal_type,
                'texto_completo': texto_completo,
                'url_acceso': sentencia.get('url_acceso', ''),
                'fecha_descarga': datetime.now().isoformat(),
                'origen': 'github_actions_cloud'
            }
            
            return registro
            
        except Exception as e:
            self.logger.error(f"Error procesando sentencia: {e}")
            return {}
    
    def _procesar_fecha(self, fecha_str: str) -> Optional[str]:
        """Procesar y normalizar fecha"""
        if not fecha_str:
            return None
        
        try:
            # Intentar diferentes formatos
            formatos = ['%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']
            for formato in formatos:
                try:
                    fecha_obj = datetime.strptime(fecha_str, formato)
                    return fecha_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            return fecha_str
        except:
            return fecha_str
    
    def cargar_a_supabase(self, sentencias: List[Dict[str, Any]]) -> bool:
        """Cargar sentencias a Supabase"""
        if not sentencias:
            return True
        
        try:
            # Filtrar sentencias válidas
            sentencias_validas = [s for s in sentencias if s.get('rol_numero')]
            
            if not sentencias_validas:
                self.logger.warning("No hay sentencias válidas para cargar")
                return True
            
            # Headers para Supabase
            headers = {
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            }
            
            # URL de Supabase
            url = f"{SUPABASE_URL}/rest/v1/sentencias"
            
            # Cargar en lotes de 50
            batch_size = 50
            for i in range(0, len(sentencias_validas), batch_size):
                lote = sentencias_validas[i:i + batch_size]
                
                response = self.session.post(url, json=lote, headers=headers, timeout=30)
                
                if response.status_code in [200, 201]:
                    self.logger.info(f"Lote cargado exitosamente: {len(lote)} sentencias")
                    self.stats['sentencias_cargadas'] += len(lote)
                else:
                    self.logger.error(f"Error cargando lote: {response.status_code} - {response.text}")
                    return False
                
                # Pausa entre lotes
                time.sleep(1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error cargando a Supabase: {e}")
            return False
    
    def ejecutar_descarga_incremental(self):
        """Ejecutar descarga incremental completa"""
        self.logger.info("🚀 INICIANDO DESCARGA INCREMENTAL CLOUD")
        self.logger.info("=" * 60)
        self.logger.info(f"🏛️ Tribunal: {self.tribunal_type}")
        self.logger.info(f"📅 Fecha desde: {self.fecha_desde}")
        self.logger.info(f"📅 Fecha hasta: {self.fecha_hasta}")
        self.logger.info(f"📄 Páginas máximas: {self.paginas_maximas}")
        self.logger.info(f"👥 Workers paralelos: {self.workers_paralelos}")
        self.logger.info("=" * 60)
        
        sentencias_totales = []
        
        # Procesar páginas secuencialmente (para evitar bloqueos)
        for pagina in range(1, self.paginas_maximas + 1):
            try:
                self.logger.info(f"🔍 Procesando página {pagina}/{self.paginas_maximas}")
                
                # Buscar sentencias en la página
                sentencias_pagina = self.buscar_sentencias_pagina(pagina)
                
                if not sentencias_pagina:
                    self.logger.warning(f"Página {pagina} sin sentencias - deteniendo")
                    break
                
                # Procesar sentencias
                sentencias_procesadas = []
                for sentencia in sentencias_pagina:
                    procesada = self.procesar_sentencia(sentencia)
                    if procesada:
                        sentencias_procesadas.append(procesada)
                
                sentencias_totales.extend(sentencias_procesadas)
                self.stats['sentencias_descargadas'] += len(sentencias_pagina)
                self.stats['sentencias_procesadas'] += len(sentencias_procesadas)
                
                self.logger.info(f"✅ Página {pagina}: {len(sentencias_procesadas)} sentencias procesadas")
                
                # Cargar a Supabase cada 5 páginas
                if len(sentencias_totales) >= 50 or pagina % 5 == 0:
                    if self.cargar_a_supabase(sentencias_totales):
                        self.logger.info(f"📤 {len(sentencias_totales)} sentencias cargadas a Supabase")
                        sentencias_totales = []  # Limpiar lista
                    else:
                        self.logger.error("Error cargando a Supabase")
                        return False
                
                # Pausa entre páginas
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error en página {pagina}: {e}")
                self.stats['errores'] += 1
                continue
        
        # Cargar sentencias restantes
        if sentencias_totales:
            if self.cargar_a_supabase(sentencias_totales):
                self.logger.info(f"📤 {len(sentencias_totales)} sentencias finales cargadas")
            else:
                self.logger.error("Error cargando sentencias finales")
                return False
        
        # Mostrar estadísticas finales
        self.mostrar_estadisticas_finales()
        
        return True
    
    def mostrar_estadisticas_finales(self):
        """Mostrar estadísticas finales"""
        duracion = datetime.now() - self.stats['inicio']
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📊 ESTADÍSTICAS FINALES")
        self.logger.info("=" * 60)
        self.logger.info(f"⏱️ Duración: {duracion}")
        self.logger.info(f"📄 Sentencias descargadas: {self.stats['sentencias_descargadas']}")
        self.logger.info(f"🔧 Sentencias procesadas: {self.stats['sentencias_procesadas']}")
        self.logger.info(f"📤 Sentencias cargadas: {self.stats['sentencias_cargadas']}")
        self.logger.info(f"❌ Errores: {self.stats['errores']}")
        self.logger.info(f"🏛️ Tribunal: {self.tribunal_type}")
        self.logger.info(f"📅 Período: {self.fecha_desde} a {self.fecha_hasta}")
        self.logger.info("=" * 60)

def main():
    """Función principal"""
    # Verificar variables de entorno
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("❌ Error: Variables de entorno SUPABASE_URL y SUPABASE_ANON_KEY requeridas")
        sys.exit(1)
    
    # Crear y ejecutar descarga
    descarga = DescargaCloudIncremental()
    exito = descarga.ejecutar_descarga_incremental()
    
    if exito:
        print("✅ Descarga incremental completada exitosamente")
        sys.exit(0)
    else:
        print("❌ Error en descarga incremental")
        sys.exit(1)

if __name__ == "__main__":
    main()
