#!/usr/bin/env python3
"""
Descarga Masiva Máquina 2 - Páginas 901-1500 con 100 Workers
Sistema optimizado para máxima paralelización
Workers: 1-100 (100 workers)
Páginas: 901-1500 (600 páginas)
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

# Reutilizar la clase exitosa de la Fase 3
from enhanced_text_worker_correcto import EnhancedTextWorkerCorrecto

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('descarga_maquina2_100workers.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def load_config():
    """Cargar configuración para máquina 2 - páginas 901-1500 con 100 workers"""
    return {
        'output_path': 'output/descarga_corte_suprema_fase3_100workers',
        'max_workers': 100,  # 100 workers para máxima paralelización
        'sentencias_por_pagina': 100,
        'fecha_desde': '2005-01-01',
        'fecha_hasta': '2025-12-31',
        'start_page': 901,  # Páginas 901-1500
        'end_page': 1500,   # Sin colisión con máquina 1
        'retry_attempts': 3,
        'delay_between_requests': 0.1,  # Delay reducido para mayor velocidad
        'machine_id': 'maquina2_100workers'  # Identificador de máquina
    }

def create_worker_directories(config, logger):
    """Crear directorios para 100 workers"""
    output_dir = config['output_path']
    os.makedirs(output_dir, exist_ok=True)
    
    # Crear directorios para workers 1-100
    for i in range(1, 101):  # Workers 1-100
        worker_dir = os.path.join(output_dir, f"worker_{i:03d}")
        os.makedirs(worker_dir, exist_ok=True)
    
    logger.info(f"✅ Directorios preparados para {config['max_workers']} workers (1-100)")

def calculate_page_ranges(config):
    """Calcular rangos de páginas para 100 workers"""
    start_page = config['start_page']
    end_page = config['end_page']
    max_workers = config['max_workers']
    
    total_pages = end_page - start_page + 1
    pages_per_worker = total_pages // max_workers
    
    page_ranges = []
    current_page = start_page
    
    for worker_id in range(1, max_workers + 1):  # Workers 1-100
        if current_page > end_page:
            break
            
        # El último worker toma las páginas restantes
        if worker_id == max_workers:
            worker_end_page = end_page
        else:
            worker_end_page = min(current_page + pages_per_worker - 1, end_page)
        
        page_ranges.append({
            'worker_id': worker_id,
            'start_page': current_page,
            'end_page': worker_end_page,
            'total_pages': worker_end_page - current_page + 1
        })
        
        current_page = worker_end_page + 1
    
    return page_ranges

def worker_task(worker_id, config, page_range, logger):
    """Tarea de un worker - MÉTODO EXITOSO DE FASE 3"""
    worker_config = {
        'output_path': config['output_path'],
        'worker_id': f"worker_{worker_id:03d}",
        'sentencias_por_pagina': config['sentencias_por_pagina'],
        'fecha_desde': config['fecha_desde'],
        'fecha_hasta': config['fecha_hasta'],
        'retry_attempts': config['retry_attempts'],
        'delay_between_requests': config['delay_between_requests']
    }
    
    worker = EnhancedTextWorkerCorrecto(
        worker_id=f"worker_{worker_id:03d}",
        config=worker_config
    )
    
    start_page = page_range['start_page']
    end_page = page_range['end_page']
    
    logger.info(f"🚀 Worker {worker_id:03d} iniciando: páginas {start_page}-{end_page}")
    
    total_sentencias = 0
    total_con_texto = 0
    total_con_roles = 0
    
    try:
        for page in range(start_page, end_page + 1):
            logger.info(f"🔍 Worker {worker_id:03d} procesando página {page}")
            
            # Obtener sentencias de la página usando el método exitoso
            sentencias = worker._get_sentencias_page(page)
            
            if not sentencias:
                logger.warning(f"⚠️ Worker {worker_id:03d} página {page}: No se encontraron sentencias")
                continue
            
            logger.info(f"✅ Worker {worker_id:03d} página {page}: {len(sentencias)} sentencias encontradas")
            
            # Procesar sentencias usando el método exitoso de la Fase 3
            processed_sentencias = worker._process_sentencias(sentencias)
            
            if processed_sentencias:
                # Contar estadísticas
                for sentencia in processed_sentencias:
                    total_sentencias += 1
                    if sentencia.get('has_full_text', False):
                        total_con_texto += 1
                    if sentencia.get('roles_adicionales'):
                        total_con_roles += 1
                
                # Guardar lote
                batch_data = {
                    'machine_id': config['machine_id'],
                    'worker_id': f"worker_{worker_id:03d}",
                    'page': page,
                    'count': len(processed_sentencias),
                    'sentencias': processed_sentencias,
                    'timestamp': datetime.now().isoformat()
                }
                
                batch_file = os.path.join(
                    config['output_path'], 
                    f"worker_{worker_id:03d}", 
                    f"batch_{page:06d}.json"
                )
                
                with open(batch_file, 'w', encoding='utf-8') as f:
                    json.dump(batch_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"✅ Worker {worker_id:03d} página {page}: {len(processed_sentencias)} sentencias guardadas")
    
    except Exception as e:
        logger.error(f"❌ Worker {worker_id:03d}: Error general: {str(e)}")
    
    logger.info(f"🎉 Worker {worker_id:03d} completado: {total_sentencias} sentencias, {total_con_texto} con texto, {total_con_roles} con roles")
    
    return {
        'worker_id': worker_id,
        'total_sentencias': total_sentencias,
        'total_con_texto': total_con_texto,
        'total_con_roles': total_con_roles,
        'pages_processed': end_page - start_page + 1
    }

def main():
    """Función principal para máquina 2 con 100 workers"""
    logger = setup_logging()
    config = load_config()
    
    logger.info("🚀 INICIANDO DESCARGA MÁQUINA 2 - PÁGINAS 901-1500 CON 100 WORKERS")
    logger.info(f"📊 Configuración: {config['max_workers']} workers, páginas {config['start_page']}-{config['end_page']}")
    logger.info("⚡ MÁXIMA PARALELIZACIÓN: 100 workers simultáneos")
    
    # Crear directorios
    create_worker_directories(config, logger)
    
    # Calcular rangos de páginas
    page_ranges = calculate_page_ranges(config)
    logger.info(f"📊 Rangos calculados: {len(page_ranges)} workers activos")
    
    # Mostrar distribución (solo primeros y últimos 5)
    logger.info("📋 Distribución de workers:")
    for i, pr in enumerate(page_ranges[:5]):
        logger.info(f"   Worker {pr['worker_id']:03d}: páginas {pr['start_page']}-{pr['end_page']} ({pr['total_pages']} páginas)")
    if len(page_ranges) > 10:
        logger.info("   ... (workers intermedios omitidos) ...")
    for pr in page_ranges[-5:]:
        logger.info(f"   Worker {pr['worker_id']:03d}: páginas {pr['start_page']}-{pr['end_page']} ({pr['total_pages']} páginas)")
    
    start_time = time.time()
    
    # Ejecutar workers en paralelo
    with ThreadPoolExecutor(max_workers=config['max_workers']) as executor:
        # Enviar tareas
        future_to_worker = {
            executor.submit(worker_task, pr['worker_id'], config, pr, logger): pr['worker_id'] 
            for pr in page_ranges
        }
        
        # Monitorear progreso
        completed_workers = 0
        total_sentencias = 0
        total_con_texto = 0
        total_con_roles = 0
        
        for future in as_completed(future_to_worker):
            worker_id = future_to_worker[future]
            try:
                result = future.result()
                completed_workers += 1
                total_sentencias += result['total_sentencias']
                total_con_texto += result['total_con_texto']
                total_con_roles += result['total_con_roles']
                
                # Log cada 10 workers completados
                if completed_workers % 10 == 0 or completed_workers == len(page_ranges):
                    logger.info(f"⏰ {datetime.now().strftime('%H:%M:%S')} - {completed_workers}/{len(page_ranges)} workers completados")
                    logger.info(f"📊 Total: {total_sentencias:,} sentencias, {total_con_texto:,} con texto, {total_con_roles:,} con roles")
                
            except Exception as e:
                logger.error(f"❌ Worker {worker_id:03d}: Error: {str(e)}")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Resumen final
    logger.info("")
    logger.info("📊 RESUMEN FINAL - MÁQUINA 2 (100 WORKERS):")
    logger.info(f"   ⏱️ Tiempo total: {total_time:.2f} segundos ({total_time/60:.1f} minutos)")
    logger.info(f"   📄 Total sentencias: {total_sentencias:,}")
    logger.info(f"   ✅ Con texto completo: {total_con_texto:,}")
    logger.info(f"   🏛️ Con roles adicionales: {total_con_roles:,}")
    logger.info(f"   📊 Tasa de éxito texto: {(total_con_texto/total_sentencias*100):.2f}%" if total_sentencias > 0 else "   📊 Tasa de éxito texto: 0%")
    logger.info(f"   📊 Tasa de éxito roles: {(total_con_roles/total_sentencias*100):.2f}%" if total_sentencias > 0 else "   📊 Tasa de éxito roles: 0%")
    logger.info(f"   ⚡ Velocidad: {total_sentencias/(total_time/60):.0f} sentencias/minuto")
    logger.info("🎉 Máquina 2 con 100 workers completada!")

if __name__ == "__main__":
    main()







