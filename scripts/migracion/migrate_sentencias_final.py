#!/usr/bin/env python3
"""
Migración Final de Sentencias a Supabase
Usa las credenciales obtenidas via MCP para migración directa
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

# Configuración de Supabase obtenida via MCP
SUPABASE_URL = "https://wluachczgiyrmrhdpcue.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndsdWFjaGN6Z2l5cm1yaGRwY3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5MjA1NDcsImV4cCI6MjA3MjQ5NjU0N30.gXSqEYy_LFp951EnBhFxU_7RSf5VbJXRc2GlLn7OB7I"

def setup_logging():
    """Configurar logging detallado"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('migrate_sentencias_final.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

class SupabaseMigrator:
    def __init__(self):
        self.logger = setup_logging()
        self.session = requests.Session()
        self.session.headers.update({
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        })
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'successful_inserts': 0,
            'failed_inserts': 0,
            'errors': []
        }

    def extract_metadata_from_text(self, text: str) -> Dict[str, Any]:
        """Extraer metadatos inteligentemente del texto"""
        metadata = {
            'caratulado': '',
            'caratulado_anonimizado': '',
            'fallo_anonimizado': '',
            'fecha_sentencia': None,
            'corte': '',
            'sala': '',
            'juzgado': '',
            'tipo_recurso': '',
            'resultado_recurso': '',
            'ministros': [],
            'redactor': '',
            'relator': '',
            'materias': [],
            'descriptores': [],
            'normas': []
        }

        # Extraer fecha de sentencia
        fecha_patterns = [
            r'(\d{1,2}[\s/]\d{1,2}[\s/]\d{4})',
            r'(\d{4}[\s/]\d{1,2}[\s/]\d{1,2})',
            r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})'
        ]
        
        for pattern in fecha_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    fecha_str = match.group(1)
                    # Intentar parsear la fecha
                    if '/' in fecha_str:
                        parts = fecha_str.split('/')
                        if len(parts) == 3:
                            if len(parts[0]) == 4:  # YYYY/MM/DD
                                metadata['fecha_sentencia'] = f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                            else:  # DD/MM/YYYY
                                metadata['fecha_sentencia'] = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
                    break
                except:
                    continue

        # Extraer corte
        cortes = ['Corte Suprema', 'Corte de Apelaciones', 'Tribunal Constitucional']
        for corte in cortes:
            if corte.lower() in text.lower():
                metadata['corte'] = corte
                break

        # Extraer sala
        sala_patterns = [
            r'Sala\s+(\w+)',
            r'Sala\s+(\d+)',
            r'Primera\s+Sala',
            r'Segunda\s+Sala',
            r'Tercera\s+Sala'
        ]
        
        for pattern in sala_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata['sala'] = match.group(0)
                break

        # Extraer tipo de recurso
        recursos = ['Recurso de Protección', 'Recurso de Amparo', 'Recurso de Casación', 'Recurso de Apelación']
        for recurso in recursos:
            if recurso.lower() in text.lower():
                metadata['tipo_recurso'] = recurso
                break

        # Extraer ministros
        ministro_pattern = r'Ministr[oa]s?\s+([A-Z][a-záéíóúñ\s]+)'
        ministros = re.findall(ministro_pattern, text)
        metadata['ministros'] = [m.strip() for m in ministros if len(m.strip()) > 3]

        # Extraer materias (palabras clave legales)
        materias_keywords = [
            'derecho civil', 'derecho penal', 'derecho laboral', 'derecho administrativo',
            'derecho constitucional', 'derecho comercial', 'derecho tributario',
            'derecho de familia', 'derecho procesal', 'derecho internacional'
        ]
        
        for materia in materias_keywords:
            if materia in text.lower():
                metadata['materias'].append(materia.title())

        return metadata

    def process_sentencia_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Procesar un archivo de sentencia individual"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extraer metadatos del texto
            texto_completo = data.get('texto', '')
            metadata = self.extract_metadata_from_text(texto_completo)
            
            # Preparar datos para Supabase
            sentencia_data = {
                'rol_numero': data.get('rol_numero', ''),
                'rol_completo': data.get('rol_completo', ''),
                'correlativo': data.get('correlativo', ''),
                'caratulado': metadata['caratulado'] or data.get('caratulado', ''),
                'caratulado_anonimizado': metadata['caratulado_anonimizado'] or data.get('caratulado_anonimizado', ''),
                'fallo_anonimizado': metadata['fallo_anonimizado'] or data.get('fallo_anonimizado', ''),
                'fecha_sentencia': metadata['fecha_sentencia'] or data.get('fecha_sentencia'),
                'fecha_actualizacion': data.get('fecha_actualizacion'),
                'era': data.get('era', ''),
                'corte': metadata['corte'] or data.get('corte', ''),
                'codigo_corte': data.get('codigo_corte', ''),
                'sala': metadata['sala'] or data.get('sala', ''),
                'juzgado': metadata['juzgado'] or data.get('juzgado', ''),
                'tipo_recurso': metadata['tipo_recurso'] or data.get('tipo_recurso', ''),
                'resultado_recurso': metadata['resultado_recurso'] or data.get('resultado_recurso', ''),
                'libro': data.get('libro', ''),
                'ministros': metadata['ministros'] or data.get('ministros', []),
                'redactor': metadata['redactor'] or data.get('redactor', ''),
                'id_redactor': data.get('id_redactor'),
                'relator': metadata['relator'] or data.get('relator', ''),
                'materias': metadata['materias'] or data.get('materias', []),
                'descriptores': metadata['descriptores'] or data.get('descriptores', []),
                'normas': metadata['normas'] or data.get('normas', []),
                'condicion_publicacion': data.get('condicion_publicacion', ''),
                'publicacion_original': data.get('publicacion_original', ''),
                'url_acceso': data.get('url_acceso', ''),
                'url_corta': data.get('url_corta', ''),
                'texto_completo': texto_completo
            }
            
            return sentencia_data
            
        except Exception as e:
            self.logger.error(f"Error procesando archivo {file_path}: {str(e)}")
            self.stats['errors'].append(f"Error en {file_path}: {str(e)}")
            return None

    def insert_sentencias_batch(self, sentencias: List[Dict[str, Any]]) -> bool:
        """Insertar un lote de sentencias en Supabase"""
        try:
            url = f"{SUPABASE_URL}/rest/v1/sentencias"
            
            response = self.session.post(
                url,
                json=sentencias,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                self.stats['successful_inserts'] += len(sentencias)
                return True
            else:
                self.logger.error(f"Error insertando lote: {response.status_code} - {response.text}")
                self.stats['failed_inserts'] += len(sentencias)
                return False
                
        except Exception as e:
            self.logger.error(f"Error en inserción de lote: {str(e)}")
            self.stats['failed_inserts'] += len(sentencias)
            return False

    def migrate_sentencias(self, input_dir: str, batch_size: int = 50):
        """Migrar todas las sentencias del directorio"""
        input_path = Path(input_dir)
        
        if not input_path.exists():
            self.logger.error(f"Directorio no encontrado: {input_dir}")
            return
        
        # Encontrar todos los archivos JSON recursivamente
        json_files = list(input_path.rglob("*.json"))
        self.stats['total_files'] = len(json_files)
        
        self.logger.info(f"Iniciando migración de {len(json_files)} archivos")
        
        # Procesar archivos en lotes
        batch = []
        processed_count = 0
        
        for file_path in json_files:
            try:
                sentencia_data = self.process_sentencia_file(file_path)
                
                if sentencia_data:
                    batch.append(sentencia_data)
                    
                    # Insertar cuando el lote esté lleno
                    if len(batch) >= batch_size:
                        if self.insert_sentencias_batch(batch):
                            self.logger.info(f"Lote insertado exitosamente: {len(batch)} sentencias")
                        else:
                            self.logger.error(f"Error insertando lote de {len(batch)} sentencias")
                        
                        batch = []
                        processed_count += batch_size
                        self.logger.info(f"Progreso: {processed_count}/{len(json_files)} archivos procesados")
                
                self.stats['processed_files'] += 1
                
            except Exception as e:
                self.logger.error(f"Error procesando {file_path}: {str(e)}")
                self.stats['errors'].append(f"Error en {file_path}: {str(e)}")
        
        # Insertar el último lote si no está vacío
        if batch:
            if self.insert_sentencias_batch(batch):
                self.logger.info(f"Último lote insertado exitosamente: {len(batch)} sentencias")
            else:
                self.logger.error(f"Error insertando último lote de {len(batch)} sentencias")
        
        # Mostrar estadísticas finales
        self.print_final_stats()

    def print_final_stats(self):
        """Mostrar estadísticas finales"""
        self.logger.info("=" * 50)
        self.logger.info("ESTADÍSTICAS FINALES DE MIGRACIÓN")
        self.logger.info("=" * 50)
        self.logger.info(f"Total de archivos: {self.stats['total_files']}")
        self.logger.info(f"Archivos procesados: {self.stats['processed_files']}")
        self.logger.info(f"Inserciones exitosas: {self.stats['successful_inserts']}")
        self.logger.info(f"Inserciones fallidas: {self.stats['failed_inserts']}")
        self.logger.info(f"Errores encontrados: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            self.logger.info("\nErrores detallados:")
            for error in self.stats['errors'][:10]:  # Mostrar solo los primeros 10
                self.logger.info(f"  - {error}")
            if len(self.stats['errors']) > 10:
                self.logger.info(f"  ... y {len(self.stats['errors']) - 10} errores más")

def main():
    """Función principal"""
    logger = setup_logging()
    
    # Configuración
    input_directory = "/Users/alexispena/Documents/descarga_sentencias/output"
    batch_size = 50  # Tamaño del lote para inserción
    
    logger.info("Iniciando migración de sentencias a Supabase")
    logger.info(f"Directorio de entrada: {input_directory}")
    logger.info(f"Tamaño de lote: {batch_size}")
    
    # Crear migrador y ejecutar
    migrator = SupabaseMigrator()
    migrator.migrate_sentencias(input_directory, batch_size)
    
    logger.info("Migración completada")

if __name__ == "__main__":
    main()
