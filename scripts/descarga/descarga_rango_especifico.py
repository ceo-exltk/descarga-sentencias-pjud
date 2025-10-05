#!/usr/bin/env python3
"""
Descarga Completa de Sentencias - Páginas 1501-2615
Sistema optimizado con migración automática a Supabase
Workers: 1-100 (100 workers)
Páginas: 1501-2615 (1115 páginas)
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import Queue
import threading
from pathlib import Path
import requests
from typing import List, Dict, Any, Optional
import re

# Importar la clase del worker
from enhanced_text_worker_correcto import EnhancedTextWorkerCorrecto

# Configuración de Supabase
SUPABASE_URL = "https://wluachczgiyrmrhdpcue.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndsdWFjaGN6Z2l5cm1yaGRwY3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5MjA1NDcsImV4cCI6MjA3MjQ5NjU0N30.gXSqEYy_LFp951EnBhFxU_7RSf5VbJXRc2GlLn7OB7I"

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('descarga_completa_1501_2615.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def get_supabase_client():
    """Inicializa y devuelve el cliente de Supabase."""
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        return supabase
    except ImportError:
        logger.error("La librería 'supabase' no está instalada. Instálala con 'pip install supabase'.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error al inicializar el cliente de Supabase: {e}")
        sys.exit(1)

supabase = get_supabase_client()

def extract_metadata(sentencia_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extrae y limpia metadatos de una sentencia individual."""
    def clean_array(arr):
        return [item.strip() for item in arr if isinstance(item, str) and item.strip()] if isinstance(arr, list) else []

    def clean_text(text):
        return text.strip() if isinstance(text, str) else None

    metadata = {
        'rol_numero': clean_text(sentencia_data.get('rol_numero')),
        'rol_completo': clean_text(sentencia_data.get('rol_completo')),
        'correlativo': clean_text(sentencia_data.get('correlativo')),
        'caratulado': clean_text(sentencia_data.get('caratulado')),
        'caratulado_anonimizado': clean_text(sentencia_data.get('caratulado_anonimizado')),
        'fallo_anonimizado': clean_text(sentencia_data.get('fallo_anonimizado')),
        'fecha_sentencia': sentencia_data.get('fecha_sentencia') if sentencia_data.get('fecha_sentencia') and sentencia_data.get('fecha_sentencia') != '' else None,
        'fecha_actualizacion': datetime.now().date().isoformat(),
        'era': clean_text(sentencia_data.get('era')),
        'corte': clean_text(sentencia_data.get('corte')),
        'codigo_corte': clean_text(sentencia_data.get('codigo_corte')),
        'sala': clean_text(sentencia_data.get('sala')),
        'juzgado': clean_text(sentencia_data.get('juzgado')),
        'tipo_recurso': clean_text(sentencia_data.get('tipo_recurso')),
        'resultado_recurso': clean_text(sentencia_data.get('resultado_recurso')),
        'libro': clean_text(sentencia_data.get('libro')),
        'ministros': clean_array(sentencia_data.get('ministros')),
        'redactor': clean_text(sentencia_data.get('redactor')),
        'id_redactor': clean_text(sentencia_data.get('id_redactor')),
        'relator': clean_text(sentencia_data.get('relator')),
        'materias': clean_array(sentencia_data.get('materias')),
        'descriptores': clean_array(sentencia_data.get('descriptores')),
        'normas': clean_array(sentencia_data.get('normas')),
        'condicion_publicacion': clean_text(sentencia_data.get('condicion_publicacion')),
        'publicacion_original': clean_text(sentencia_data.get('publicacion_original')),
        'url_acceso': clean_text(sentencia_data.get('url_acceso')),
        'url_corta': clean_text(sentencia_data.get('url_corta')),
        'texto_completo': clean_text(sentencia_data.get('texto_completo')),
    }

    for key in ['ministros', 'materias', 'descriptores', 'normas']:
        if metadata[key] is None:
            metadata[key] = []

    return metadata

def insert_sentencias_batch(batch: List[Dict[str, Any]]):
    """Inserta un lote de sentencias en Supabase."""
    try:
        response = supabase.from_('sentencias').insert(batch).execute()
        if response.data:
            logger.info(f"✅ Insertado lote de {len(response.data)} sentencias en Supabase")
        elif response.error:
            logger.error(f"❌ Error insertando lote: {response.error.code} - {response.error.message}")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error de conexión al insertar lote: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Error inesperado al insertar lote: {e}")
        raise

def worker_process(worker_id: int, page_queue: Queue, output_path: Path, supabase_client):
    """Proceso worker que descarga páginas y migra automáticamente a Supabase."""
    # Configuración para el worker
    config = {
        'output_path': str(output_path),
        'max_workers': 100,
        'start_page': 1501,
        'end_page': 2615,
        'fecha_desde': '2020-01-01',
        'fecha_hasta': '2024-12-31'
    }
    
    worker = EnhancedTextWorkerCorrecto(str(worker_id), config)
    worker_output_path = output_path / f"worker_{worker_id:03d}"
    worker_output_path.mkdir(parents=True, exist_ok=True)
    
    sentencias_buffer = []
    batch_size = 50  # Migrar cada 50 sentencias
    total_sentencias = 0
    sentencias_con_texto = 0
    sentencias_con_roles = 0
    
    logger.info(f"🚀 Worker {worker_id:03d} iniciado")
    
    while True:
        try:
            page_num = page_queue.get(timeout=30)
            if page_num is None:  # Señal de finalización
                break
                
            logger.info(f"📄 Worker {worker_id:03d} procesando página {page_num}")
            
            # Descargar sentencias de la página
            sentencias = worker.descargar_sentencias_pagina(page_num)
            
            if not sentencias:
                logger.warning(f"⚠️ Worker {worker_id:03d} página {page_num}: Sin sentencias")
                continue
                
            # Procesar cada sentencia
            for sentencia_data in sentencias:
                try:
                    metadata = extract_metadata(sentencia_data)
                    sentencias_buffer.append(metadata)
                    total_sentencias += 1
                    
                    if metadata.get('texto_completo'):
                        sentencias_con_texto += 1
                    if metadata.get('rol_numero'):
                        sentencias_con_roles += 1
                        
                    # Migrar a Supabase cuando el buffer esté lleno
                    if len(sentencias_buffer) >= batch_size:
                        try:
                            insert_sentencias_batch(sentencias_buffer)
                            sentencias_buffer = []
                        except Exception as e:
                            logger.error(f"❌ Worker {worker_id:03d} error migrando lote: {e}")
                            # Guardar en archivo como respaldo
                            _guardar_sentencias_respaldo(worker_output_path, sentencias_buffer, page_num)
                            sentencias_buffer = []
                            
                except Exception as e:
                    logger.error(f"❌ Worker {worker_id:03d} error procesando sentencia: {e}")
                    continue
            
            # Guardar archivo JSON como respaldo
            _guardar_sentencias_json(worker_output_path, sentencias, page_num)
            
            logger.info(f"✅ Worker {worker_id:03d} página {page_num}: {len(sentencias)} sentencias guardadas")
            
        except Exception as e:
            logger.error(f"❌ Worker {worker_id:03d} error en página {page_num}: {e}")
            continue
    
    # Migrar sentencias restantes del buffer
    if sentencias_buffer:
        try:
            insert_sentencias_batch(sentencias_buffer)
        except Exception as e:
            logger.error(f"❌ Worker {worker_id:03d} error migrando buffer final: {e}")
            # Guardar como respaldo
            _guardar_sentencias_respaldo(worker_output_path, sentencias_buffer, "final")
    
    logger.info(f"🎉 Worker {worker_id:03d} completado: {total_sentencias} sentencias, {sentencias_con_texto} con texto, {sentencias_con_roles} con roles")

def _guardar_sentencias_json(output_path: Path, sentencias: List[Dict], page_num: int):
    """Guarda sentencias en archivo JSON como respaldo."""
    try:
        filename = f"batch_{page_num:06d}.json"
        filepath = output_path / filename
        
        data = {
            'pagina': page_num,
            'fecha_descarga': datetime.now().isoformat(),
            'total_sentencias': len(sentencias),
            'sentencias': sentencias
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        logger.error(f"❌ Error guardando JSON respaldo: {e}")

def _guardar_sentencias_respaldo(output_path: Path, sentencias: List[Dict], page_num: str):
    """Guarda sentencias como respaldo en caso de error de migración."""
    try:
        filename = f"respaldo_{page_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_path / filename
        
        data = {
            'pagina': page_num,
            'fecha_respaldo': datetime.now().isoformat(),
            'total_sentencias': len(sentencias),
            'sentencias': sentencias
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"💾 Respaldo guardado: {filename}")
        
    except Exception as e:
        logger.error(f"❌ Error guardando respaldo: {e}")

def main():
    """Función principal de descarga completa."""
    # Configuración
    start_page = 1501
    end_page = 2615
    max_workers = 100
    output_path = Path('output/descarga_completa_1501_2615')
    
    logger.info("🚀 Iniciando descarga completa de sentencias")
    logger.info(f"📊 Configuración: Páginas {start_page}-{end_page}, {max_workers} workers")
    
    # Crear directorio de salida
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Crear cola de páginas
    page_queue = Queue()
    for page in range(start_page, end_page + 1):
        page_queue.put(page)
    
    # Agregar señales de finalización
    for _ in range(max_workers):
        page_queue.put(None)
    
    # Iniciar workers
    logger.info(f"👥 Iniciando {max_workers} workers...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for worker_id in range(1, max_workers + 1):
            future = executor.submit(worker_process, worker_id, page_queue, output_path, supabase)
            futures.append(future)
        
        # Esperar a que todos los workers terminen
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"❌ Error en worker: {e}")
    
    logger.info("🎉 Descarga completa finalizada")

if __name__ == "__main__":
    main()
