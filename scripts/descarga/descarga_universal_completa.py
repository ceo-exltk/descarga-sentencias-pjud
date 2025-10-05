#!/usr/bin/env python3
"""
Script Maestro para Descarga Universal de Sentencias
Descarga completa de todos los tribunales con workers máximos
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from universal_sentencias_worker import procesar_tribunal_worker

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('descarga_universal_completa.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DescargaUniversalCompleta:
    """Sistema de descarga universal de sentencias"""
    
    def __init__(self, max_workers_por_tribunal: int = 50):
        self.max_workers_por_tribunal = max_workers_por_tribunal
        self.output_dir = Path("output/descarga_universal_completa")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuración de tribunales con estimaciones realistas
        self.tribunales_config = {
            'Corte_Suprema': {
                'total_pages': 2615,
                'max_workers': max_workers_por_tribunal,
                'descripcion': 'Corte Suprema de Chile'
            },
            'Corte_de_Apelaciones': {
                'total_pages': 150989,  # 1,509,885 resultados estimados
                'max_workers': max_workers_por_tribunal,
                'descripcion': 'Cortes de Apelaciones'
            },
            'Laborales': {
                'total_pages': 17396,  # 173,955 consultas estimadas
                'max_workers': max_workers_por_tribunal,
                'descripcion': 'Tribunales Laborales'
            },
            'Penales': {
                'total_pages': 22801,  # 228,008 consultas estimadas
                'max_workers': max_workers_por_tribunal,
                'descripcion': 'Tribunales Penales'
            },
            'Familia': {
                'total_pages': 11335,  # 113,349 consultas estimadas
                'max_workers': max_workers_por_tribunal,
                'descripcion': 'Tribunales de Familia'
            },
            'Civiles': {
                'total_pages': 33313,  # 333,128 consultas estimadas
                'max_workers': max_workers_por_tribunal,
                'descripcion': 'Tribunales Civiles'
            },
            'Cobranza': {
                'total_pages': 2613,  # 26,124 resultados estimados
                'max_workers': max_workers_por_tribunal,
                'descripcion': 'Tribunales de Cobranza'
            }
        }
        
        # Calcular totales
        self.total_pages_universo = sum(config['total_pages'] for config in self.tribunales_config.values())
        self.total_workers_universo = sum(config['max_workers'] for config in self.tribunales_config.values())
    
    def distribuir_paginas_workers(self, tribunal_type: str, total_pages: int, max_workers: int) -> list:
        """Distribuye las páginas entre los workers de manera óptima"""
        pages_per_worker = total_pages // max_workers
        remainder = total_pages % max_workers
        
        page_ranges = []
        start_page = 1
        
        for worker_id in range(1, max_workers + 1):
            # Calcular páginas para este worker
            if worker_id <= remainder:
                pages_for_worker = pages_per_worker + 1
            else:
                pages_for_worker = pages_per_worker
            
            end_page = start_page + pages_for_worker - 1
            
            page_ranges.append({
                'worker_id': worker_id,
                'start_page': start_page,
                'end_page': end_page,
                'total_pages': pages_for_worker,
                'page_range': range(start_page, end_page + 1)
            })
            
            start_page = end_page + 1
        
        return page_ranges
    
    def ejecutar_descarga_tribunal(self, tribunal_type: str) -> dict:
        """Ejecuta la descarga completa de un tribunal específico"""
        logger.info(f"🚀 Iniciando descarga de {tribunal_type}")
        
        config = self.tribunales_config[tribunal_type]
        total_pages = config['total_pages']
        max_workers = config['max_workers']
        
        # Crear directorio del tribunal
        tribunal_dir = self.output_dir / tribunal_type
        tribunal_dir.mkdir(parents=True, exist_ok=True)
        
        # Distribuir páginas entre workers
        worker_configs = self.distribuir_paginas_workers(tribunal_type, total_pages, max_workers)
        
        logger.info(f"📊 {tribunal_type}: {total_pages:,} páginas distribuidas en {max_workers} workers")
        
        # Ejecutar workers en paralelo
        resultados_workers = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Preparar argumentos para cada worker
            futures = []
            for worker_config in worker_configs:
                args = (
                    tribunal_type,
                    worker_config['worker_id'],
                    worker_config['page_range'],
                    tribunal_dir
                )
                future = executor.submit(procesar_tribunal_worker, args)
                futures.append(future)
            
            # Recopilar resultados
            for future in as_completed(futures):
                try:
                    resultado = future.result()
                    resultados_workers.append(resultado)
                    logger.info(f"✅ Worker completado: {resultado}")
                except Exception as e:
                    logger.error(f"❌ Error en worker: {e}")
        
        # Calcular estadísticas del tribunal
        total_sentencias = sum(r.get('total_sentencias', 0) for r in resultados_workers)
        total_con_texto = sum(r.get('total_con_texto', 0) for r in resultados_workers)
        total_con_roles = sum(r.get('total_con_roles', 0) for r in resultados_workers)
        
        # Guardar resumen del tribunal
        resumen_tribunal = {
            'tribunal_type': tribunal_type,
            'descripcion': config['descripcion'],
            'total_pages': total_pages,
            'max_workers': max_workers,
            'total_sentencias': total_sentencias,
            'total_con_texto': total_con_texto,
            'total_con_roles': total_con_roles,
            'fecha_inicio': datetime.now().isoformat(),
            'fecha_fin': datetime.now().isoformat(),
            'workers_completados': len(resultados_workers),
            'tasa_exito_texto': (total_con_texto / total_sentencias * 100) if total_sentencias > 0 else 0,
            'tasa_exito_roles': (total_con_roles / total_sentencias * 100) if total_sentencias > 0 else 0
        }
        
        resumen_file = tribunal_dir / "resumen_tribunal.json"
        with open(resumen_file, 'w', encoding='utf-8') as f:
            json.dump(resumen_tribunal, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ {tribunal_type} completado: {total_sentencias:,} sentencias")
        return resumen_tribunal
    
    def ejecutar_descarga_universal(self):
        """Ejecuta la descarga universal de todos los tribunales"""
        logger.info("🌍 INICIANDO DESCARGA UNIVERSAL DE SENTENCIAS")
        logger.info("=" * 70)
        
        inicio_total = datetime.now()
        resultados_tribunales = []
        
        # Ejecutar descarga de cada tribunal secuencialmente para evitar sobrecarga
        for tribunal_type, config in self.tribunales_config.items():
            try:
                logger.info(f"\n🏛️ Procesando {tribunal_type} - {config['descripcion']}")
                logger.info(f"📊 Páginas estimadas: {config['total_pages']:,}")
                logger.info(f"👥 Workers asignados: {config['max_workers']}")
                
                resultado = self.ejecutar_descarga_tribunal(tribunal_type)
                resultados_tribunales.append(resultado)
                
                # Pausa entre tribunales para no sobrecargar el servidor
                logger.info("⏸️ Pausa de 30 segundos antes del siguiente tribunal...")
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Error procesando {tribunal_type}: {e}")
                continue
        
        # Calcular estadísticas finales
        fin_total = datetime.now()
        duracion_total = fin_total - inicio_total
        
        total_sentencias_universo = sum(r.get('total_sentencias', 0) for r in resultados_tribunales)
        total_con_texto_universo = sum(r.get('total_con_texto', 0) for r in resultados_tribunales)
        total_con_roles_universo = sum(r.get('total_con_roles', 0) for r in resultados_tribunales)
        
        # Crear resumen final
        resumen_final = {
            'fecha_inicio': inicio_total.isoformat(),
            'fecha_fin': fin_total.isoformat(),
            'duracion_total_horas': duracion_total.total_seconds() / 3600,
            'total_tribunales': len(self.tribunales_config),
            'total_workers_universo': self.total_workers_universo,
            'total_pages_universo': self.total_pages_universo,
            'total_sentencias_universo': total_sentencias_universo,
            'total_con_texto_universo': total_con_texto_universo,
            'total_con_roles_universo': total_con_roles_universo,
            'tasa_exito_texto_universo': (total_con_texto_universo / total_sentencias_universo * 100) if total_sentencias_universo > 0 else 0,
            'tasa_exito_roles_universo': (total_con_roles_universo / total_sentencias_universo * 100) if total_sentencias_universo > 0 else 0,
            'tribunales_procesados': resultados_tribunales
        }
        
        # Guardar resumen final
        resumen_final_file = self.output_dir / "resumen_final_universo.json"
        with open(resumen_final_file, 'w', encoding='utf-8') as f:
            json.dump(resumen_final, f, ensure_ascii=False, indent=2)
        
        # Mostrar resumen final
        self.mostrar_resumen_final(resumen_final)
        
        return resumen_final
    
    def mostrar_resumen_final(self, resumen: dict):
        """Muestra el resumen final de la descarga"""
        print("\n" + "=" * 70)
        print("🎉 DESCARGA UNIVERSAL DE SENTENCIAS COMPLETADA")
        print("=" * 70)
        print(f"⏱️  Duración total: {resumen['duracion_total_horas']:.2f} horas")
        print(f"🏛️  Tribunales procesados: {resumen['total_tribunales']}")
        print(f"👥 Total workers utilizados: {resumen['total_workers_universo']:,}")
        print(f"📄 Total páginas procesadas: {resumen['total_pages_universo']:,}")
        print(f"📚 Total sentencias descargadas: {resumen['total_sentencias_universo']:,}")
        print(f"📝 Sentencias con texto: {resumen['total_con_texto_universo']:,} ({resumen['tasa_exito_texto_universo']:.2f}%)")
        print(f"🔢 Sentencias con roles: {resumen['total_con_roles_universo']:,} ({resumen['tasa_exito_roles_universo']:.2f}%)")
        print("\n📊 RESUMEN POR TRIBUNAL:")
        print("-" * 70)
        
        for tribunal in resumen['tribunales_procesados']:
            print(f"🏛️  {tribunal['tribunal_type']}: {tribunal['total_sentencias']:,} sentencias")
            print(f"   📝 Con texto: {tribunal['total_con_texto']:,} ({tribunal['tasa_exito_texto']:.2f}%)")
            print(f"   🔢 Con roles: {tribunal['total_con_roles']:,} ({tribunal['tasa_exito_roles']:.2f}%)")
            print()
        
        print("=" * 70)

def main():
    """Función principal"""
    print("🌍 SISTEMA DE DESCARGA UNIVERSAL DE SENTENCIAS")
    print("=" * 70)
    print("Descarga completa de todos los tribunales del Poder Judicial")
    print("Con workers máximos y procesamiento optimizado de fechas")
    print("=" * 70)
    
    # Configuración
    max_workers_por_tribunal = 50  # Workers máximos por tribunal
    
    try:
        # Crear sistema de descarga
        descarga_sistema = DescargaUniversalCompleta(max_workers_por_tribunal)
        
        # Mostrar configuración
        print(f"\n⚙️  CONFIGURACIÓN:")
        print(f"   👥 Workers por tribunal: {max_workers_por_tribunal}")
        print(f"   🏛️  Total tribunales: {len(descarga_sistema.tribunales_config)}")
        print(f"   👥 Total workers universo: {descarga_sistema.total_workers_universo:,}")
        print(f"   📄 Total páginas universo: {descarga_sistema.total_pages_universo:,}")
        
        # Confirmar inicio
        # Auto-iniciar sin interacción del usuario
        logger.info("🚀 Iniciando descarga universal automáticamente...")
        respuesta = 's'
        
        # Ejecutar descarga universal
        resultado = descarga_sistema.ejecutar_descarga_universal()
        
        print(f"\n✅ Descarga universal completada exitosamente!")
        print(f"📁 Archivos guardados en: {descarga_sistema.output_dir}")
        
    except KeyboardInterrupt:
        print("\n❌ Descarga interrumpida por el usuario")
    except Exception as e:
        logger.error(f"❌ Error en descarga universal: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
