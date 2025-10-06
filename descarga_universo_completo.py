#!/usr/bin/env python3
"""
Sistema de descarga completa del universo de sentencias PJUD
Configurado para ejecutarse de forma segura durante 5 días
"""

import json
import os
import sys
import time
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class DescargadorUniversoCompleto:
    def __init__(self, output_dir="output/universo_completo"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuración de seguridad
        self.rate_limit_delay = 0.5  # 0.5 segundos entre requests
        self.max_retries = 5
        self.timeout = 30
        self.batch_size = 50  # Sentencias por batch
        
        # Configuración de workers
        self.max_workers = 3  # Conservador para evitar bloqueos
        self.workers_por_tribunal = {
            "Corte_de_Apelaciones": 3,
            "Civiles": 2,
            "Penales": 2,
            "Familia": 1,
            "Laborales": 1,
            "Corte_Suprema": 1,
            "Cobranza": 1
        }
        
        # Configuración de logging
        self.setup_logging()
        
        # Estado del sistema
        self.estado_file = self.output_dir / "estado_descarga.json"
        self.load_estado()
        
        # Configuración de tribunales
        self.tribunales = {
            "Corte_Suprema": {
                "id_buscador": "1",
                "cabecera": "Corte Suprema",
                "total_estimado": 261871,
                "prioridad": 1
            },
            "Corte_de_Apelaciones": {
                "id_buscador": "2", 
                "cabecera": "Corte de Apelaciones",
                "total_estimado": 1510429,
                "prioridad": 1
            },
            "Laborales": {
                "id_buscador": "3",
                "cabecera": "Tribunales Laborales", 
                "total_estimado": 233904,
                "prioridad": 2
            },
            "Penales": {
                "id_buscador": "4",
                "cabecera": "Tribunales Penales",
                "total_estimado": 862269,
                "prioridad": 2
            },
            "Familia": {
                "id_buscador": "5",
                "cabecera": "Tribunales de Familia",
                "total_estimado": 371320,
                "prioridad": 3
            },
            "Civiles": {
                "id_buscador": "6",
                "cabecera": "Tribunales Civiles",
                "total_estimado": 849956,
                "prioridad": 2
            },
            "Cobranza": {
                "id_buscador": "7",
                "cabecera": "Tribunales de Cobranza",
                "total_estimado": 26132,
                "prioridad": 3
            }
        }
        
        # Headers para requests
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json",
            "Referer": "https://juris.pjud.cl/busqueda",
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def setup_logging(self):
        """Configurar sistema de logging"""
        log_dir = self.output_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Logger principal
        self.logger = logging.getLogger('descarga_universo')
        self.logger.setLevel(logging.INFO)
        
        # Handler para archivo
        file_handler = logging.FileHandler(log_dir / f"descarga_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_handler.setLevel(logging.INFO)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def load_estado(self):
        """Cargar estado de descarga desde archivo"""
        if self.estado_file.exists():
            with open(self.estado_file, 'r') as f:
                self.estado = json.load(f)
        else:
            self.estado = {
                "inicio": datetime.now().isoformat(),
                "tribunales": {},
                "total_descargado": 0,
                "total_estimado": 4115881,
                "estado": "iniciando"
            }
            self.save_estado()
    
    def save_estado(self):
        """Guardar estado actual"""
        self.estado["ultima_actualizacion"] = datetime.now().isoformat()
        with open(self.estado_file, 'w') as f:
            json.dump(self.estado, f, indent=2)
    
    def obtener_total_tribunal(self, tribunal_name, id_buscador, cabecera):
        """Obtener total real de sentencias de un tribunal"""
        try:
            url = "https://juris.pjud.cl/busqueda/buscar_sentencias"
            headers = self.headers.copy()
            headers["busqueda"] = cabecera
            
            filtros = {
                "rol": "", "era": "", "fec_desde": "", "fec_hasta": "",
                "tipo_norma": "", "num_norma": "", "num_art": "", "num_inciso": "",
                "todas": "", "algunas": "", "excluir": "", "literal": "",
                "proximidad": "", "distancia": "", "analisis_s": "", "submaterias": "",
                "facetas_seleccionadas": [], "filtros_omnibox": [], "ids_comunas_seleccionadas_mapa": []
            }
            
            data = {
                "id_buscador": id_buscador,
                "filtros": json.dumps(filtros),
                "offset": 0,
                "limit": 1
            }
            
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            total = result.get("total", 0)
            
            self.logger.info(f"📊 {tribunal_name}: {total:,} sentencias encontradas")
            return total
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo total para {tribunal_name}: {e}")
            return self.tribunales[tribunal_name]["total_estimado"]
    
    def descargar_batch_sentencias(self, tribunal_name, offset, limit, batch_num):
        """Descargar un batch de sentencias"""
        tribunal_config = self.tribunales[tribunal_name]
        
        try:
            # Rate limiting
            time.sleep(self.rate_limit_delay + random.uniform(0, 0.5))
            
            url = "https://juris.pjud.cl/busqueda/buscar_sentencias"
            headers = self.headers.copy()
            headers["busqueda"] = tribunal_config["cabecera"]
            
            filtros = {
                "rol": "", "era": "", "fec_desde": "", "fec_hasta": "",
                "tipo_norma": "", "num_norma": "", "num_art": "", "num_inciso": "",
                "todas": "", "algunas": "", "excluir": "", "literal": "",
                "proximidad": "", "distancia": "", "analisis_s": "", "submaterias": "",
                "facetas_seleccionadas": [], "filtros_omnibox": [], "ids_comunas_seleccionadas_mapa": []
            }
            
            data = {
                "id_buscador": tribunal_config["id_buscador"],
                "filtros": json.dumps(filtros),
                "offset": offset,
                "limit": limit
            }
            
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            sentencias = result.get("sentencias", [])
            
            if sentencias:
                # Guardar batch
                tribunal_dir = self.output_dir / tribunal_name
                tribunal_dir.mkdir(exist_ok=True)
                
                batch_file = tribunal_dir / f"batch_{batch_num:06d}.json"
                with open(batch_file, 'w', encoding='utf-8') as f:
                    json.dump(sentencias, f, ensure_ascii=False, indent=2)
                
                self.logger.info(f"✅ {tribunal_name} - Batch {batch_num}: {len(sentencias)} sentencias")
                return len(sentencias)
            else:
                self.logger.warning(f"⚠️ {tribunal_name} - Batch {batch_num}: Sin sentencias")
                return 0
                
        except Exception as e:
            self.logger.error(f"❌ Error en batch {batch_num} de {tribunal_name}: {e}")
            return 0
    
    def descargar_tribunal(self, tribunal_name):
        """Descargar todas las sentencias de un tribunal"""
        tribunal_config = self.tribunales[tribunal_name]
        
        self.logger.info(f"🏛️ Iniciando descarga de {tribunal_name}...")
        
        # Obtener total real
        total = self.obtener_total_tribunal(
            tribunal_name, 
            tribunal_config["id_buscador"], 
            tribunal_config["cabecera"]
        )
        
        if total == 0:
            self.logger.error(f"❌ No se pudo obtener total para {tribunal_name}")
            return 0
        
        # Inicializar estado del tribunal
        if tribunal_name not in self.estado["tribunales"]:
            self.estado["tribunales"][tribunal_name] = {
                "total": total,
                "descargado": 0,
                "batch_actual": 0,
                "estado": "iniciando",
                "inicio": datetime.now().isoformat()
            }
        
        tribunal_estado = self.estado["tribunales"][tribunal_name]
        tribunal_estado["estado"] = "descargando"
        self.save_estado()
        
        # Calcular batches
        total_batches = (total + self.batch_size - 1) // self.batch_size
        batch_inicial = tribunal_estado.get("batch_actual", 0)
        
        self.logger.info(f"📊 {tribunal_name}: {total:,} sentencias en {total_batches:,} batches")
        self.logger.info(f"🔄 Continuando desde batch {batch_inicial}")
        
        sentencias_descargadas = 0
        
        # Descargar con workers limitados
        max_workers = min(self.workers_por_tribunal[tribunal_name], 3)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for batch_num in range(batch_inicial, total_batches):
                offset = batch_num * self.batch_size
                limit = min(self.batch_size, total - offset)
                
                future = executor.submit(
                    self.descargar_batch_sentencias,
                    tribunal_name, offset, limit, batch_num
                )
                futures.append(future)
                
                # Control de concurrencia
                if len(futures) >= max_workers * 2:
                    # Esperar a que completen algunos
                    for f in as_completed(futures[:max_workers]):
                        try:
                            batch_sentencias = f.result()
                            sentencias_descargadas += batch_sentencias
                            tribunal_estado["descargado"] += batch_sentencias
                            tribunal_estado["batch_actual"] = batch_num + 1
                            
                            # Guardar progreso cada 10 batches
                            if batch_num % 10 == 0:
                                self.save_estado()
                                
                        except Exception as e:
                            self.logger.error(f"❌ Error procesando batch: {e}")
                    
                    futures = futures[max_workers:]
            
            # Esperar batches restantes
            for f in as_completed(futures):
                try:
                    batch_sentencias = f.result()
                    sentencias_descargadas += batch_sentencias
                    tribunal_estado["descargado"] += batch_sentencias
                except Exception as e:
                    self.logger.error(f"❌ Error procesando batch final: {e}")
        
        tribunal_estado["estado"] = "completado"
        tribunal_estado["fin"] = datetime.now().isoformat()
        self.estado["total_descargado"] += sentencias_descargadas
        
        self.logger.info(f"✅ {tribunal_name} completado: {sentencias_descargadas:,} sentencias")
        self.save_estado()
        
        return sentencias_descargadas
    
    def ejecutar_descarga_completa(self):
        """Ejecutar descarga completa del universo"""
        self.logger.info("🚀 INICIANDO DESCARGA COMPLETA DEL UNIVERSO")
        self.logger.info(f"📊 Total estimado: {self.estado['total_estimado']:,} sentencias")
        self.logger.info(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.estado["estado"] = "ejecutando"
        self.save_estado()
        
        # Ordenar tribunales por prioridad
        tribunales_ordenados = sorted(
            self.tribunales.items(),
            key=lambda x: x[1]["prioridad"]
        )
        
        total_descargado = 0
        
        for tribunal_name, tribunal_config in tribunales_ordenados:
            try:
                self.logger.info(f"\n{'='*60}")
                self.logger.info(f"🏛️ PROCESANDO TRIBUNAL: {tribunal_name}")
                self.logger.info(f"{'='*60}")
                
                sentencias = self.descargar_tribunal(tribunal_name)
                total_descargado += sentencias
                
                # Pausa entre tribunales para evitar sobrecarga
                self.logger.info(f"⏸️ Pausa de 30 segundos antes del siguiente tribunal...")
                time.sleep(30)
                
            except KeyboardInterrupt:
                self.logger.info("⏹️ Descarga interrumpida por usuario")
                break
            except Exception as e:
                self.logger.error(f"❌ Error procesando {tribunal_name}: {e}")
                continue
        
        self.estado["estado"] = "completado"
        self.estado["fin"] = datetime.now().isoformat()
        self.save_estado()
        
        self.logger.info(f"\n🎉 DESCARGA COMPLETA FINALIZADA")
        self.logger.info(f"📊 Total descargado: {total_descargado:,} sentencias")
        self.logger.info(f"⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return total_descargado

def main():
    """Función principal"""
    print("🌍 DESCARGA COMPLETA DEL UNIVERSO DE SENTENCIAS")
    print("=" * 60)
    print("⚠️  ADVERTENCIA: Este proceso puede tomar varios días")
    print("⚠️  Asegúrate de tener conexión estable a internet")
    print("⚠️  El sistema se ejecutará de forma segura con rate limiting")
    print("=" * 60)
    
    # Confirmar ejecución
    respuesta = input("\n¿Continuar con la descarga completa? (s/N): ").lower()
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Descarga cancelada")
        return
    
    # Crear descargador
    descargador = DescargadorUniversoCompleto()
    
    try:
        # Ejecutar descarga
        total = descargador.ejecutar_descarga_completa()
        print(f"\n✅ Descarga completada: {total:,} sentencias")
        
    except KeyboardInterrupt:
        print("\n⏹️ Descarga interrumpida por usuario")
        print("💾 Estado guardado - puedes continuar más tarde")
    except Exception as e:
        print(f"\n❌ Error durante la descarga: {e}")
        print("💾 Estado guardado - revisa los logs")

if __name__ == "__main__":
    main()
