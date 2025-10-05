#!/usr/bin/env python3
"""
Migración Corregida de Sentencias a Supabase
Procesa correctamente los archivos JSON que contienen arrays de sentencias
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import requests
from typing import List, Dict, Any, Optional
import re

# Configuración de Supabase
SUPABASE_URL = "https://wluachczgiyrmrhdpcue.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndsdWFjaGN6Z2l5cm1yaGRwY3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5MjA1NDcsImV4cCI6MjA3MjQ5NjU0N30.gXSqEYy_LFp951EnBhFxU_7RSf5VbJXRc2GlLn7OB7I"

def setup_logging():
    """Configurar logging detallado"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('migrate_sentencias_corrected.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def extract_metadata_from_text(texto_completo: str) -> Dict[str, Any]:
    """Extraer metadatos del texto completo de la sentencia"""
    if not texto_completo:
        return {}
    
    # Patrones para extraer información
    patterns = {
        'ministros': r'(?:Ministros?|Ministra):\s*([^\n]+)',
        'redactor': r'(?:Redactor|Redactora):\s*([^\n]+)',
        'relator': r'(?:Relator|Relatora):\s*([^\n]+)',
        'materias': r'(?:Materias?|Materia):\s*([^\n]+)',
        'descriptores': r'(?:Descriptores?|Descriptor):\s*([^\n]+)',
        'normas': r'(?:Normas?|Norma):\s*([^\n]+)'
    }
    
    metadata = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, texto_completo, re.IGNORECASE | re.MULTILINE)
        if match:
            value = match.group(1).strip()
            if key in ['materias', 'descriptores', 'normas']:
                # Convertir a array
                metadata[key] = [item.strip() for item in value.split(',') if item.strip()]
            else:
                metadata[key] = value
    
    return metadata

def process_sentencia(sentencia_data: Dict[str, Any]) -> Dict[str, Any]:
    """Procesar una sentencia individual y convertirla al formato de la base de datos"""
    
    # Extraer metadatos del texto completo
    texto_completo = sentencia_data.get('texto_completo', '')
    metadata = extract_metadata_from_text(texto_completo)
    
    # Mapear campos del formato original al formato de la base de datos
    processed = {
        'rol_numero': sentencia_data.get('rol_era_sup_s', '') or sentencia_data.get('rol_era_ape_s', ''),
        'rol_completo': sentencia_data.get('rol_era_sup_s', '') or sentencia_data.get('rol_era_ape_s', ''),
        'correlativo': sentencia_data.get('rol_corte_i'),
        'caratulado': sentencia_data.get('caratulado', ''),
        'caratulado_anonimizado': sentencia_data.get('caratulado_s', ''),
        'fallo_anonimizado': texto_completo,  # Usar texto completo como fallo
        'fecha_sentencia': sentencia_data.get('fecha_sentencia') if sentencia_data.get('fecha_sentencia') and sentencia_data.get('fecha_sentencia') != '' else None,
        'fecha_actualizacion': datetime.now().date().isoformat(),
        'era': sentencia_data.get('era_corte_i'),
        'corte': sentencia_data.get('corte', ''),
        'codigo_corte': sentencia_data.get('rol_corte_i'),
        'sala': sentencia_data.get('sala', ''),
        'juzgado': sentencia_data.get('juzgado', ''),
        'tipo_recurso': None,  # No disponible en el formato original
        'resultado_recurso': None,  # No disponible en el formato original
        'libro': None,  # No disponible en el formato original
        'ministros': metadata.get('ministros', []),
        'redactor': metadata.get('redactor'),
        'id_redactor': None,  # No disponible en el formato original
        'relator': metadata.get('relator'),
        'materias': metadata.get('materias', []),
        'descriptores': metadata.get('descriptores', []),
        'normas': metadata.get('normas', []),
        'condicion_publicacion': None,  # No disponible en el formato original
        'publicacion_original': None,  # No disponible en el formato original
        'url_acceso': sentencia_data.get('url_acceso', ''),
        'url_corta': None,  # No disponible en el formato original
        'texto_completo': texto_completo
    }
    
    return processed

def process_json_file(file_path: Path) -> List[Dict[str, Any]]:
    """Procesar un archivo JSON y extraer todas las sentencias"""
    logger = logging.getLogger(__name__)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Verificar si es un archivo de batch
        if 'sentencias' in data and isinstance(data['sentencias'], list):
            sentencias = data['sentencias']
            logger.info(f"Procesando archivo {file_path.name}: {len(sentencias)} sentencias")
            
            processed_sentencias = []
            for sentencia in sentencias:
                try:
                    processed = process_sentencia(sentencia)
                    processed_sentencias.append(processed)
                except Exception as e:
                    logger.error(f"Error procesando sentencia en {file_path.name}: {e}")
                    continue
            
            return processed_sentencias
        else:
            logger.warning(f"Formato de archivo no reconocido: {file_path.name}")
            return []
            
    except Exception as e:
        logger.error(f"Error procesando archivo {file_path.name}: {e}")
        return []

def insert_sentencias_batch(sentencias: List[Dict[str, Any]]) -> bool:
    """Insertar un lote de sentencias en Supabase"""
    logger = logging.getLogger(__name__)
    
    if not sentencias:
        return True
    
    try:
        # Preparar datos para inserción masiva
        headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
        # Insertar en lotes de 100 para evitar límites de tamaño
        batch_size = 100
        for i in range(0, len(sentencias), batch_size):
            batch = sentencias[i:i + batch_size]
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/sentencias",
                headers=headers,
                json=batch
            )
            
            if response.status_code not in [200, 201]:
                logger.error(f"Error insertando lote {i//batch_size + 1}: {response.status_code} - {response.text}")
                return False
            
            logger.info(f"Insertado lote {i//batch_size + 1}: {len(batch)} sentencias")
        
        return True
        
    except Exception as e:
        logger.error(f"Error insertando sentencias: {e}")
        return False

def migrate_sentencias():
    """Función principal de migración"""
    logger = setup_logging()
    
    # Directorio de archivos JSON
    input_path = Path("output")
    
    if not input_path.exists():
        logger.error("Directorio 'output' no encontrado")
        return False
    
    # Encontrar todos los archivos JSON
    json_files = list(input_path.rglob("*.json"))
    logger.info(f"Encontrados {len(json_files)} archivos JSON")
    
    if not json_files:
        logger.error("No se encontraron archivos JSON para procesar")
        return False
    
    # Procesar archivos en paralelo
    all_sentencias = []
    processed_files = 0
    failed_files = 0
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Enviar tareas
        future_to_file = {
            executor.submit(process_json_file, file_path): file_path 
            for file_path in json_files
        }
        
        # Procesar resultados
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                sentencias = future.result()
                if sentencias:
                    all_sentencias.extend(sentencias)
                    processed_files += 1
                    logger.info(f"Procesado {file_path.name}: {len(sentencias)} sentencias")
                else:
                    failed_files += 1
                    logger.warning(f"No se pudieron procesar sentencias de {file_path.name}")
            except Exception as e:
                failed_files += 1
                logger.error(f"Error procesando {file_path.name}: {e}")
    
    logger.info(f"Procesamiento completado:")
    logger.info(f"  - Archivos procesados: {processed_files}")
    logger.info(f"  - Archivos fallidos: {failed_files}")
    logger.info(f"  - Total de sentencias: {len(all_sentencias)}")
    
    if not all_sentencias:
        logger.error("No se procesaron sentencias válidas")
        return False
    
    # Insertar en la base de datos
    logger.info("Iniciando inserción en Supabase...")
    success = insert_sentencias_batch(all_sentencias)
    
    if success:
        logger.info(f"Migración completada exitosamente: {len(all_sentencias)} sentencias insertadas")
    else:
        logger.error("Error durante la inserción en Supabase")
    
    return success

if __name__ == "__main__":
    success = migrate_sentencias()
    sys.exit(0 if success else 1)
