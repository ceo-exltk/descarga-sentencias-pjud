#!/usr/bin/env python3
"""
Worker mejorado que extrae roles usando los campos específicos confirmados por el socio
"""

import json
import time
import logging
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Optional, Dict, Any

class EnhancedTextWorkerCorrecto:
    """Worker que extrae texto completo Y roles usando campos específicos de la API"""
    
    def __init__(self, worker_id: str, config: Dict[str, Any]):
        self.worker_id = worker_id
        self.config = config
        self.base_url = "https://juris.pjud.cl"
        
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f'worker_{worker_id}')
        
        # Configurar sesión HTTP
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://juris.pjud.cl/busqueda?Corte_Suprema',
            'Origin': 'https://juris.pjud.cl',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
        
        self.logger.info(f"🚀 Worker {worker_id} inicializado con extracción de roles usando campos específicos")
    
    def _get_token(self) -> Optional[str]:
        """Obtener token CSRF usando la secuencia confirmada"""
        try:
            # 1. Obtener token y establecer sesión
            response = self.session.get(f"{self.base_url}/busqueda/lista_buscadores")
            response.raise_for_status()
            
            # 2. Obtener token del meta tag
            soup = BeautifulSoup(response.text, 'html.parser')
            token_meta = soup.find('meta', {'name': 'csrf-token'})
            
            if token_meta and 'content' in token_meta.attrs:
                token = token_meta['content']
                self.session.headers['X-CSRF-TOKEN'] = token
                return token
            
            # Fallback: buscar en inputs
            token_input = soup.find('input', {'name': '_token'})
            if token_input and 'value' in token_input.attrs:
                token = token_input['value']
                self.session.headers['X-CSRF-TOKEN'] = token
                return token
                
            return None
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error obteniendo token: {e}")
            return None
    
    def _establish_context(self) -> bool:
        """Establecer contexto Corte Suprema"""
        try:
            response = self.session.get(f"{self.base_url}/busqueda?Corte_Suprema")
            response.raise_for_status()
            return True
        except Exception as e:
            self.logger.warning(f"⚠️ Error estableciendo contexto: {e}")
            return False
    
    def _get_full_text_and_roles(self, rol_era_sup_s: str) -> Optional[Dict[str, Any]]:
        """
        Obtener texto completo y roles usando los campos específicos confirmados
        """
        if not rol_era_sup_s:
            return None
        
        try:
            # Obtener token
            token = self._get_token()
            if not token:
                self.logger.warning(f"⚠️ No se pudo obtener token para {rol_era_sup_s}")
                return None
            
            # Establecer contexto
            if not self._establish_context():
                self.logger.warning(f"⚠️ No se pudo establecer contexto para {rol_era_sup_s}")
                return None
            
            # Usar el endpoint que funciona
            URL_GET_SENTENCES = "https://juris.pjud.cl/busqueda/buscar_sentencias"
            
            rol, era = rol_era_sup_s.split("-")
            
            # Payload exacto como en el código que funciona
            payload = {
                '_token': token,
                'id_buscador': '528',  # Corte Suprema
                'filtros': json.dumps({
                    "rol": rol,
                    "era": era,
                    "fec_desde": "",
                    "fec_hasta": "",
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
                'numero_filas_paginacion': '1',
                'offset_paginacion': '0',
                'orden': 'rel'
            }
            
            headers = {
                'busqueda': 'Buscador_Jurisprudencial_de_la_Corte_Suprema',
                'Content-Type': 'application/json'
            }
            
            # Realizar request
            response = self.session.post(URL_GET_SENTENCES, json=payload, headers=headers)
            
            if response.status_code != 200:
                self.logger.warning(f"⚠️ Error obteniendo datos para {rol_era_sup_s}: {response.status_code}")
                return None
            
            # Parsear respuesta
            response_data = response.json()
            docs = response_data.get("response", {}).get("docs", [])
            
            if not docs:
                self.logger.warning(f"⚠️ No se encontraron documentos para {rol_era_sup_s}")
                return None
            
            # Extraer datos del primer documento
            doc = docs[0]
            
            # Extraer texto completo
            texto_completo = doc.get('texto_sentencia', '')
            
            # Extraer roles usando los campos específicos confirmados
            roles_data = {
                'texto_completo': texto_completo,
                'has_full_text': bool(texto_completo and len(texto_completo) > 100),
                
                # Campos básicos
                'caratulado_s': doc.get('caratulado_s', ''),
                'gls_corte_s': doc.get('gls_corte_s', ''),
                
                # Roles relacionados (CAMPOS PRINCIPALES)
                'rol_era_ape_s': doc.get('rol_era_ape_s', ''),  # Rol completo en Corte de Apelaciones
                'rol_corte_i': doc.get('rol_corte_i', ''),     # Número de rol en Corte de Apelaciones
                'era_corte_i': doc.get('era_corte_i', ''),     # Era en Corte de Apelaciones
                'rol_juz_i': doc.get('rol_juz_i', ''),         # Número de rol en Juzgado
                'era_juz_i': doc.get('era_juz_i', ''),         # Era en Juzgado
                
                # Campos adicionales
                'rol_era_sup_s': doc.get('rol_era_sup_s', ''),
                'fecha_sentencia': doc.get('fecha_sentencia', ''),
                'sala': doc.get('sala', ''),
                'juzgado': doc.get('juzgado', ''),
                'url_acceso': doc.get('url_acceso', '')
            }
            
            # Log de roles encontrados
            roles_encontrados = []
            if roles_data['rol_era_ape_s']:
                roles_encontrados.append(f"Apelaciones: {roles_data['rol_era_ape_s']}")
            if roles_data['rol_corte_i'] and roles_data['era_corte_i']:
                roles_encontrados.append(f"Corte I: {roles_data['rol_corte_i']}-{roles_data['era_corte_i']}")
            if roles_data['rol_juz_i'] and roles_data['era_juz_i']:
                roles_encontrados.append(f"Juzgado: {roles_data['rol_juz_i']}-{roles_data['era_juz_i']}")
            
            if roles_encontrados:
                self.logger.info(f"✅ Roles encontrados para {rol_era_sup_s}: {', '.join(roles_encontrados)}")
            else:
                self.logger.warning(f"⚠️ No se encontraron roles adicionales para {rol_era_sup_s}")
            
            if roles_data['has_full_text']:
                self.logger.info(f"✅ Texto completo obtenido para {rol_era_sup_s} ({len(texto_completo)} chars)")
            else:
                self.logger.warning(f"⚠️ Texto no disponible para {rol_era_sup_s}")
            
            return roles_data
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error al obtener datos de {rol_era_sup_s}: {e}")
            return None
    
    def _process_sentencias(self, sentencias: list) -> list:
        """Procesar sentencias y extraer texto completo + roles"""
        processed = []
        
        for sentencia in sentencias:
            try:
                # Obtener datos completos
                rol_era_sup_s = sentencia.get('rol_era_sup_s', '')
                datos_completos = self._get_full_text_and_roles(rol_era_sup_s)
                
                # Crear sentencia procesada
                sentencia_procesada = sentencia.copy()
                
                if datos_completos:
                    # Actualizar con datos extraídos
                    sentencia_procesada.update(datos_completos)
                else:
                    # Marcar como sin datos
                    sentencia_procesada['has_full_text'] = False
                    sentencia_procesada['texto_completo'] = ''
                
                processed.append(sentencia_procesada)
                
            except Exception as e:
                self.logger.error(f"❌ Error procesando sentencia: {e}")
                processed.append(sentencia)
        
        return processed
    
    def process_batch(self, batch_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Procesar un batch de sentencias"""
        try:
            self.logger.info(f"🚀 Procesando batch {batch_id}...")
            
            # Simular obtención de sentencias (aquí iría la lógica real)
            # Por ahora, crear sentencias de prueba
            sentencias_ejemplo = [
                {
                    'id': '254450',
                    'rol_era_sup_s': '2774-2007',
                    'caratulado': 'INMOBILIARIA MALL VIÑA DEL MAR CON BARRERA MONROY IVAN',
                    'fecha_sentencia': '2007-08-28',
                    'sala': 'PRIMERA, CIVIL',
                    'corte': 'C.A. de Valparaíso',
                    'juzgado': '2 JUZGADO CIVIL DE VIÑA DEL MAR'
                }
            ]
            
            # Procesar sentencias
            sentencias_procesadas = self._process_sentencias(sentencias_ejemplo)
            
            # Guardar resultado
            output_file = f"{config['output_path']}/batch_{batch_id}.json"
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            
            resultado = {
                'batch_id': batch_id,
                'worker_id': self.worker_id,
                'timestamp': time.strftime('%Y-%d-%mT%H:%M:%S'),
                'config': config,
                'count': len(sentencias_procesadas),
                'sentencias': sentencias_procesadas
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2)
            
            # Estadísticas
            con_texto = sum(1 for s in sentencias_procesadas if s.get('has_full_text', False))
            con_roles_adicionales = sum(1 for s in sentencias_procesadas if any(s.get(k) for k in ['rol_era_ape_s', 'rol_corte_i', 'rol_juz_i']))
            
            self.logger.info(f"✅ Batch {batch_id} completado: {con_texto}/{len(sentencias_procesadas)} con texto, {con_roles_adicionales} con roles adicionales")
            
            return {
                'success': True,
                'count': len(sentencias_procesadas),
                'full_text_count': con_texto,
                'roles_count': con_roles_adicionales,
                'output_file': output_file
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error procesando batch {batch_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'count': 0,
                'full_text_count': 0,
                'roles_count': 0
            }
    
    def _get_sentencias_page(self, page: int) -> list:
        """Obtener sentencias de una página específica"""
        try:
            # Obtener token
            token = self._get_token()
            if not token:
                return []
            
            # Establecer contexto Corte Suprema
            self.session.get(f"{self.base_url}/busqueda?Corte_Suprema")
            
            # Calcular offset
            offset = (page - 1) * self.config.get('sentencias_por_pagina', 100)
            
            # Buscar sentencias de la página
            payload = {
                '_token': token,
                'id_buscador': '528',
                'filtros': json.dumps({
                    "rol": "",
                    "era": "",
                    "fec_desde": self.config.get('fecha_desde', '2005-01-01'),
                    "fec_hasta": self.config.get('fecha_hasta', '2025-09-24'),
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
                'numero_filas_paginacion': str(self.config.get('sentencias_por_pagina', 100)),
                'offset_paginacion': str(offset),
                'orden': 'rel'
            }
            
            headers = {
                'busqueda': 'Buscador_Jurisprudencial_de_la_Corte_Suprema',
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': token
            }
            
            response = self.session.post(
                f"{self.base_url}/busqueda/buscar_sentencias",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            docs = data.get('response', {}).get('docs', [])
            
            # Convertir a formato esperado
            sentencias = []
            for doc in docs:
                sentencia = {
                    'id': doc.get('id', ''),
                    'rol_era_sup_s': doc.get('rol_era_sup_s', ''),
                    'caratulado': doc.get('caratulado_s', ''),
                    'fecha_sentencia': doc.get('fecha_sentencia', ''),
                    'sala': doc.get('sala', ''),
                    'corte': doc.get('gls_corte_s', ''),
                    'juzgado': doc.get('juzgado', ''),
                    'url_acceso': doc.get('url_acceso', '')
                }
                sentencias.append(sentencia)
            
            return sentencias
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo página {page}: {str(e)}")
            return []

if __name__ == "__main__":
    # Prueba del worker
    config = {
        'output_path': 'output/test_correcto',
        'state_path': 'output/test_correcto_state',
        'batch_delay': 1.0,
        'max_retries': 3,
        'timeout': 30
    }
    
    worker = EnhancedTextWorkerCorrecto('test_correcto_01', config)
    result = worker.process_batch('test_001', config)
    
    print(f"Resultado: {result}")
