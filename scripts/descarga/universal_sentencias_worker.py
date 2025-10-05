#!/usr/bin/env python3
"""
Worker Universal para Descarga de Sentencias de Todos los Tribunales
Sistema optimizado con workers máximos para descarga completa
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('universal_sentencias_worker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UniversalSentenciasWorker:
    """Worker universal para descarga de sentencias de todos los tribunales"""
    
    def __init__(self, worker_id: int, tribunal_type: str, max_workers: int = 50):
        self.worker_id = worker_id
        self.tribunal_type = tribunal_type
        self.max_workers = max_workers
        self.base_url = "https://juris.pjud.cl"
        self.session = requests.Session()
        
        # Headers optimizados
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': f'https://juris.pjud.cl/busqueda?{tribunal_type}',
            'Origin': 'https://juris.pjud.cl',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        # Configuración de tribunales
        self.tribunal_configs = {
            'Corte_Suprema': {
                'url': 'https://juris.pjud.cl/busqueda/buscar_sentencias',
                'total_pages': 2615,  # Basado en análisis previo
                'sentencias_por_pagina': 10,
                'filters': {'Corte_Suprema': 'Corte Suprema'}
            },
            'Corte_de_Apelaciones': {
                'url': 'https://juris.pjud.cl/busqueda/buscar_sentencias',
                'total_pages': 150989,  # 1,509,885 resultados / 10 por página
                'sentencias_por_pagina': 10,
                'filters': {'Corte_de_Apelaciones': 'Corte de Apelaciones'}
            },
            'Laborales': {
                'url': 'https://juris.pjud.cl/busqueda/buscar_sentencias',
                'total_pages': 17396,  # 173,955 consultas / 10 por página
                'sentencias_por_pagina': 10,
                'filters': {'Laborales': 'Laborales'}
            },
            'Penales': {
                'url': 'https://juris.pjud.cl/busqueda/buscar_sentencias',
                'total_pages': 22801,  # 228,008 consultas / 10 por página
                'sentencias_por_pagina': 10,
                'filters': {'Penales': 'Penales'}
            },
            'Familia': {
                'url': 'https://juris.pjud.cl/busqueda/buscar_sentencias',
                'total_pages': 11335,  # 113,349 consultas / 10 por página
                'sentencias_por_pagina': 10,
                'filters': {'Familia': 'Familia'}
            },
            'Civiles': {
                'url': 'https://juris.pjud.cl/busqueda/buscar_sentencias',
                'total_pages': 33313,  # 333,128 consultas / 10 por página
                'sentencias_por_pagina': 10,
                'filters': {'Civiles': 'Civiles'}
            },
            'Cobranza': {
                'url': 'https://juris.pjud.cl/busqueda/buscar_sentencias',
                'total_pages': 2613,  # 26,124 resultados / 10 por página
                'sentencias_por_pagina': 10,
                'filters': {'Cobranza': 'Cobranza'}
            }
        }
        
        self.config = self.tribunal_configs.get(tribunal_type, {})
        if not self.config:
            raise ValueError(f"Tipo de tribunal no soportado: {tribunal_type}")
    
    def _get_sentencias_page(self, page_num: int) -> List[Dict[str, Any]]:
        """Obtiene sentencias de una página específica"""
        try:
            # Parámetros de búsqueda
            search_params = {
                'page': page_num,
                'limit': self.config['sentencias_por_pagina'],
                'order': 'fecha_sentencia',
                'order_direction': 'desc'
            }
            
            # Añadir filtros específicos del tribunal
            search_params.update(self.config['filters'])
            
            # Realizar búsqueda
            response = self.session.post(
                self.config['url'],
                data=search_params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'sentencias' in data:
                    return data['sentencias']
                elif 'results' in data:
                    return data['results']
                else:
                    logger.warning(f"Worker {self.worker_id} página {page_num}: Formato de respuesta inesperado")
                    return []
            else:
                logger.error(f"Worker {self.worker_id} página {page_num}: Error HTTP {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Worker {self.worker_id} página {page_num}: Error de conexión: {e}")
            return []
        except Exception as e:
            logger.error(f"Worker {self.worker_id} página {page_num}: Error inesperado: {e}")
            return []
    
    def _process_sentencia(self, sentencia_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa una sentencia individual"""
        try:
            # Extraer datos básicos
            rol_numero = sentencia_data.get('rol_numero', '')
            caratulado = sentencia_data.get('caratulado', '')
            corte = sentencia_data.get('corte', '')
            sala = sentencia_data.get('sala', '')
            materias = sentencia_data.get('materias', '')
            descriptores = sentencia_data.get('descriptores', '')
            fecha_sentencia = sentencia_data.get('fecha_sentencia', '')
            url_acceso = sentencia_data.get('url_acceso', '')
            texto_completo = sentencia_data.get('texto_completo', '')
            
            # Procesar fecha de sentencia
            fecha_procesada = self._process_fecha_sentencia(fecha_sentencia)
            
            # Crear metadata procesada
            processed = {
                'id': f"{self.tribunal_type}_{rol_numero}_{page_num}",
                'rol_numero': rol_numero,
                'caratulado': caratulado,
                'corte': corte,
                'sala': sala,
                'materias': materias,
                'descriptores': descriptores,
                'fecha_sentencia': fecha_procesada,
                'fecha_sentencia_original': fecha_sentencia,
                'url_acceso': url_acceso,
                'texto_completo': texto_completo,
                'tribunal_type': self.tribunal_type,
                'worker_id': self.worker_id,
                'fecha_descarga': datetime.now().isoformat(),
                'tiene_texto': bool(texto_completo and len(texto_completo.strip()) > 50),
                'tiene_roles': bool(rol_numero and len(rol_numero.strip()) > 0)
            }
            
            return processed
            
        except Exception as e:
            logger.error(f"Worker {self.worker_id}: Error procesando sentencia: {e}")
            return {}
    
    def _process_fecha_sentencia(self, fecha_str: str) -> str:
        """Procesa y normaliza la fecha de sentencia"""
        if not fecha_str:
            return ""
        
        try:
            # Intentar diferentes formatos de fecha
            formatos_fecha = [
                '%d-%m-%Y',
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%Y/%m/%d',
                '%d-%m-%y',
                '%d/%m/%y'
            ]
            
            for formato in formatos_fecha:
                try:
                    fecha_obj = datetime.strptime(fecha_str, formato)
                    return fecha_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # Si no se puede parsear, devolver original
            return fecha_str
            
        except Exception as e:
            logger.warning(f"Worker {self.worker_id}: Error procesando fecha '{fecha_str}': {e}")
            return fecha_str
    
    def descargar_sentencias_pagina(self, page_num: int) -> Dict[str, Any]:
        """Descarga sentencias de una página específica"""
        try:
            logger.info(f"Worker {self.worker_id} ({self.tribunal_type}): Descargando página {page_num}")
            
            # Obtener sentencias de la página
            sentencias = self._get_sentencias_page(page_num)
            
            if not sentencias:
                return {'page': page_num, 'sentencias': 0, 'error': None}
            
            # Procesar sentencias
            sentencias_procesadas = []
            for sentencia_data in sentencias:
                processed = self._process_sentencia(sentencia_data)
                if processed:
                    sentencias_procesadas.append(processed)
            
            logger.info(f"Worker {self.worker_id} ({self.tribunal_type}): Página {page_num} - {len(sentencias_procesadas)} sentencias procesadas")
            
            return {
                'page': page_num,
                'sentencias': len(sentencias_procesadas),
                'sentencias_data': sentencias_procesadas,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Worker {self.worker_id} ({self.tribunal_type}): Error en página {page_num}: {e}")
            return {'page': page_num, 'sentencias': 0, 'error': str(e)}

def procesar_tribunal_worker(args):
    """Función para procesar un tribunal con múltiples workers"""
    tribunal_type, worker_id, page_range, output_dir = args
    
    try:
        worker = UniversalSentenciasWorker(worker_id, tribunal_type)
        
        # Crear directorio de salida
        tribunal_dir = output_dir / f"{tribunal_type}_worker_{worker_id:03d}"
        tribunal_dir.mkdir(parents=True, exist_ok=True)
        
        total_sentencias = 0
        total_con_texto = 0
        total_con_roles = 0
        
        for page_num in page_range:
            try:
                result = worker.descargar_sentencias_pagina(page_num)
                
                if result['sentencias'] > 0:
                    # Guardar lote de sentencias
                    batch_file = tribunal_dir / f"batch_{page_num:06d}.json"
                    with open(batch_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            'tribunal_type': tribunal_type,
                            'worker_id': worker_id,
                            'page': page_num,
                            'fecha_descarga': datetime.now().isoformat(),
                            'total_sentencias': result['sentencias'],
                            'sentencias': result['sentencias_data']
                        }, f, ensure_ascii=False, indent=2)
                    
                    total_sentencias += result['sentencias']
                    
                    # Contar sentencias con texto y roles
                    for sentencia in result['sentencias_data']:
                        if sentencia.get('tiene_texto', False):
                            total_con_texto += 1
                        if sentencia.get('tiene_roles', False):
                            total_con_roles += 1
                
                # Pequeña pausa para no sobrecargar el servidor
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Worker {worker_id} ({tribunal_type}): Error en página {page_num}: {e}")
                continue
        
        # Guardar resumen del worker
        resumen_file = tribunal_dir / "resumen_worker.json"
        with open(resumen_file, 'w', encoding='utf-8') as f:
            json.dump({
                'tribunal_type': tribunal_type,
                'worker_id': worker_id,
                'total_sentencias': total_sentencias,
                'total_con_texto': total_con_texto,
                'total_con_roles': total_con_roles,
                'fecha_fin': datetime.now().isoformat(),
                'paginas_procesadas': len(page_range)
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Worker {worker_id} ({tribunal_type}) completado: {total_sentencias} sentencias")
        return {
            'tribunal_type': tribunal_type,
            'worker_id': worker_id,
            'total_sentencias': total_sentencias,
            'total_con_texto': total_con_texto,
            'total_con_roles': total_con_roles
        }
        
    except Exception as e:
        logger.error(f"❌ Error en worker {worker_id} ({tribunal_type}): {e}")
        return {
            'tribunal_type': tribunal_type,
            'worker_id': worker_id,
            'total_sentencias': 0,
            'total_con_texto': 0,
            'total_con_roles': 0,
            'error': str(e)
        }

if __name__ == "__main__":
    print("🚀 Worker Universal de Sentencias - Sistema de Descarga Completa")
    print("=" * 70)







