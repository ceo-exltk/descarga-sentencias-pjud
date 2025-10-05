#!/usr/bin/env python3
"""
Script Final de Migración Corregido
Maneja la estructura real de datos y evita duplicados
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime
from pathlib import Path
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
            logging.FileHandler('migrate_final_corrected.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Limpiar texto de caracteres problemáticos"""
    if not text:
        return ""
    # Remover caracteres de control y normalizar espacios
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_date_from_text(text: str) -> Optional[str]:
    """Extraer fecha del texto completo de la sentencia"""
    if not text:
        return None
    
    # Patrones de fecha en el texto
    date_patterns = [
        r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})',
        r'(\d{1,2})/(\d{1,2})/(\d{4})',
        r'(\d{1,2})-(\d{1,2})-(\d{4})',
    ]
    
    month_map = {
        'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
        'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
        'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
    }
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                if len(match) == 3:
                    day, month, year = match
                    
                    # Convertir mes de texto a número
                    if month.lower() in month_map:
                        month = month_map[month.lower()]
                    
                    # Crear fecha en formato YYYY-MM-DD
                    date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                    
                    # Validar que sea una fecha válida
                    datetime.strptime(date_str, "%Y-%m-%d")
                    return date_str
            except ValueError:
                continue
    
    return None

def process_sentencia(sentencia: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Procesar una sentencia individual con la estructura correcta"""
    try:
        # Usar rol_era_sup_s como rol_numero
        rol_numero = clean_text(sentencia.get('rol_era_sup_s', ''))
        if not rol_numero:
            return None
        
        # Usar caratulado_s si existe, sino caratulado
        caratulado = clean_text(sentencia.get('caratulado_s', sentencia.get('caratulado', '')))
        if not caratulado:
            return None
        
        # Extraer fecha del texto completo si no existe
        fecha_sentencia = sentencia.get('fecha_sentencia', '')
        if not fecha_sentencia:
            texto_completo = sentencia.get('texto_completo', '')
            fecha_sentencia = extract_date_from_text(texto_completo)
        
        # Usar gls_corte_s si existe, sino corte
        corte = clean_text(sentencia.get('gls_corte_s', sentencia.get('corte', '')))
        
        processed = {
            'rol_numero': rol_numero,
            'caratulado': caratulado,
            'fecha_sentencia': fecha_sentencia,
            'corte': corte,
            'sala': clean_text(sentencia.get('sala', '')),
            'materias': [],  # No hay materias en esta estructura
            'texto_completo': clean_text(sentencia.get('texto_completo', '')),
            'url_acceso': sentencia.get('url_acceso', ''),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        return processed
        
    except Exception as e:
        print(f"Error procesando sentencia: {e}")
        return None

def check_duplicate(rol_numero: str, logger: logging.Logger) -> bool:
    """Verificar si ya existe una sentencia con este ROL"""
    try:
        headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/sentencias?rol_numero=eq.{rol_numero}&select=id",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return len(data) > 0
        else:
            logger.warning(f"Error verificando duplicado para ROL {rol_numero}: {response.status_code}")
            return False
            
    except Exception as e:
        logger.warning(f"Excepción verificando duplicado para ROL {rol_numero}: {e}")
        return False

def insert_sentencias_batch(sentencias: List[Dict[str, Any]], logger: logging.Logger) -> tuple:
    """Insertar un lote de sentencias evitando duplicados"""
    if not sentencias:
        return 0, 0
    
    # Filtrar duplicados
    unique_sentencias = []
    duplicates_found = 0
    
    for sentencia in sentencias:
        rol_numero = sentencia.get('rol_numero')
        if rol_numero and not check_duplicate(rol_numero, logger):
            unique_sentencias.append(sentencia)
        else:
            duplicates_found += 1
    
    if not unique_sentencias:
        logger.info(f"Todas las {len(sentencias)} sentencias son duplicados")
        return 0, len(sentencias)
    
    # Insertar en lotes de 5 para evitar timeouts
    batch_size = 5
    total_inserted = 0
    total_errors = 0
    
    for i in range(0, len(unique_sentencias), batch_size):
        batch = unique_sentencias[i:i + batch_size]
        
        try:
            headers = {
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
                'Content-Type': 'application/json',
                'Prefer': 'resolution=merge-duplicates'
            }
            
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/sentencias",
                headers=headers,
                json=batch,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                total_inserted += len(batch)
                logger.info(f"✅ Lote de {len(batch)} sentencias insertado exitosamente")
            else:
                total_errors += len(batch)
                logger.error(f"❌ Error insertando lote: {response.status_code} - {response.text}")
                
        except Exception as e:
            total_errors += len(batch)
            logger.error(f"❌ Excepción insertando lote: {e}")
        
        # Pausa entre lotes
        time.sleep(2)
    
    return total_inserted, total_errors + duplicates_found

def process_file(file_path: Path, logger: logging.Logger) -> tuple:
    """Procesar un archivo JSON individual"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        sentencias = data.get('sentencias', [])
        if not sentencias:
            logger.warning(f"⚠️ Archivo vacío: {file_path}")
            return 0, 0
        
        logger.info(f"📄 Procesando {len(sentencias)} sentencias de {file_path.name}")
        
        # Procesar sentencias
        processed_sentencias = []
        for sentencia in sentencias:
            processed = process_sentencia(sentencia)
            if processed:
                processed_sentencias.append(processed)
        
        if not processed_sentencias:
            logger.warning(f"⚠️ No se pudieron procesar sentencias de {file_path.name}")
            return 0, len(sentencias)
        
        logger.info(f"📊 Procesadas {len(processed_sentencias)} sentencias válidas de {len(sentencias)}")
        
        # Insertar en lotes pequeños
        total_inserted, total_errors = insert_sentencias_batch(processed_sentencias, logger)
        
        logger.info(f"✅ Archivo completado: {total_inserted} insertadas, {total_errors} errores")
        return total_inserted, total_errors
        
    except Exception as e:
        logger.error(f"❌ Error procesando archivo {file_path}: {e}")
        return 0, 1

def main():
    logger = setup_logging()
    logger.info("🚀 Iniciando migración final corregida...")
    
    # Directorio de archivos batch
    batch_dir = Path("output/descarga_corte_suprema_fase3_100workers")
    
    if not batch_dir.exists():
        logger.error(f"❌ Directorio no encontrado: {batch_dir}")
        return
    
    # Encontrar todos los archivos batch
    batch_files = list(batch_dir.glob("**/batch_*.json"))
    logger.info(f"📁 Encontrados {len(batch_files)} archivos batch")
    
    if not batch_files:
        logger.warning("⚠️ No se encontraron archivos batch para procesar")
        return
    
    # Estadísticas
    total_files = len(batch_files)
    total_inserted = 0
    total_errors = 0
    files_processed = 0
    
    # Procesar archivos uno por uno
    for file_path in batch_files:
        try:
            inserted, errors = process_file(file_path, logger)
            total_inserted += inserted
            total_errors += errors
            files_processed += 1
            
            # Pausa entre archivos
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"❌ Error procesando archivo {file_path}: {e}")
            total_errors += 1
            files_processed += 1
    
    # Estadísticas finales
    logger.info("=" * 60)
    logger.info("ESTADÍSTICAS FINALES DE MIGRACIÓN CORREGIDA")
    logger.info("=" * 60)
    logger.info(f"Total de archivos: {total_files}")
    logger.info(f"Archivos procesados: {files_processed}")
    logger.info(f"Total sentencias insertadas: {total_inserted}")
    logger.info(f"Total sentencias con errores: {total_errors}")
    logger.info(f"Tasa de éxito: {(total_inserted / (total_inserted + total_errors) * 100):.1f}%")
    logger.info("🎉 Migración final completada")

if __name__ == "__main__":
    main()







