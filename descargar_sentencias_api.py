#!/usr/bin/env python3
"""
Sistema de Descarga de Sentencias usando la API oficial PJUD
Basado en la misma API que usamos para obtener totales
"""

import requests
import json
import re
import time
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

# Configuración de buscadores (id y cabecera) - IDs CORRECTOS
BUSCADORES = {
    "Corte_Suprema": ("528", "Buscador_Jurisprudencial_de_la_Corte_Suprema"),
    "Corte_de_Apelaciones": ("168", "Buscador_Jurisprudencial_de_Cortes_de_Apelaciones"),
    "Laborales": ("271", "Buscador_Jurisprudencial_de_Tribunales_Laborales"),
    "Penales": ("268", "Buscador_Jurisprudencial_de_Tribunales_Penales"),
    "Familia": ("270", "Buscador_Jurisprudencial_de_Tribunales_de_Familia"),
    "Civiles": ("328", "Buscador_Jurisprudencial_de_Tribunales_Civiles"),
    "Cobranza": ("269", "Buscador_Jurisprudencial_de_Tribunales_de_Cobranza"),
}

class DescargadorSentencias:
    def __init__(self, output_dir="output/descarga_api", fecha_desde=None, fecha_hasta=None):
        self.output_dir = output_dir
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept-Language": "es-CL,es;q=0.9,en-US;q=0.8,en;q=0.7"
        })
        self.token = None
        self.estadisticas = {
            "inicio": datetime.now(),
            "total_descargado": 0,
            "total_errores": 0,
            "tribunales_completados": 0,
            "tribunales_totales": len(BUSCADORES),
            "filtros_fecha": {
                "fecha_desde": fecha_desde,
                "fecha_hasta": fecha_hasta
            }
        }
        
        # Crear directorio de salida
        os.makedirs(self.output_dir, exist_ok=True)
        
    def obtener_token(self):
        """Visita la página principal y extrae el token CSRF"""
        print("🔑 Obteniendo token CSRF...")
        try:
            resp = self.session.get("https://juris.pjud.cl/", timeout=30)
            resp.raise_for_status()
            m = re.search(r'name="_token"\s+value="([^"]+)"', resp.text)
            if m:
                self.token = m.group(1)
                print(f"✅ Token CSRF obtenido: {self.token[:20]}...")
                return True
            else:
                raise ValueError("Token CSRF no encontrado en la página principal.")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al obtener token CSRF: {e}")
            return False

    def establecer_contexto(self):
        """Establece el contexto de la sesión visitando la página de búsqueda"""
        print("🌐 Estableciendo contexto...")
        try:
            resp = self.session.get("https://juris.pjud.cl/busqueda", timeout=30)
            resp.raise_for_status()
            print("✅ Contexto establecido")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al establecer contexto: {e}")
            return False

    def obtener_total_tribunal(self, id_buscador, cabecera, nombre_tribunal):
        """Obtiene el total de sentencias de un tribunal"""
        url = "https://juris.pjud.cl/busqueda/buscar_sentencias"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
            "busqueda": cabecera,
            "Content-Type": "application/json",
            "Referer": f"https://juris.pjud.cl/busqueda?{nombre_tribunal}",
        }
        
        # Construir filtros con fechas si están definidas
        filtros = {
            "rol": "", "era": "", 
            "fec_desde": self.fecha_desde or "", 
            "fec_hasta": self.fecha_hasta or "", 
            "tipo_norma": "", "num_norma": "", "num_art": "", "num_inciso": "", 
            "todas": "", "algunas": "", "excluir": "", "literal": "", 
            "proximidad": "", "distancia": "", "analisis_s": "", "submaterias": "", 
            "facetas_seleccionadas": [], "filtros_omnibox": [], "ids_comunas_seleccionadas_mapa": []
        }
        
        filtros_json = json.dumps(filtros)

        payload = {
            "_token": self.token,
            "id_buscador": id_buscador,
            "filtros": filtros_json,
            "numero_filas_paginacion": "1",
            "offset_paginacion": "0",
            "orden": "rel"
        }

        try:
            resp = self.session.post(url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            if 'response' in data and 'numFound' in data['response']:
                total = data['response']['numFound']
                print(f"✅ {nombre_tribunal}: {total:,} sentencias")
                return total
            else:
                print(f"❌ {nombre_tribunal}: No se encontró 'numFound' en la respuesta")
                return 0
        except Exception as e:
            print(f"❌ Error consultando {nombre_tribunal}: {e}")
            return 0

    def descargar_sentencias_tribunal(self, nombre_tribunal, id_buscador, cabecera, limite=None):
        """Descarga todas las sentencias de un tribunal específico"""
        print(f"\n🏛️ Descargando sentencias de {nombre_tribunal}...")
        
        # Crear directorio para el tribunal
        tribunal_dir = os.path.join(self.output_dir, nombre_tribunal)
        os.makedirs(tribunal_dir, exist_ok=True)
        
        # Obtener total primero
        total = self.obtener_total_tribunal(id_buscador, cabecera, nombre_tribunal)
        if total == 0:
            print(f"❌ No se pudo obtener total para {nombre_tribunal}")
            return 0
        
        # Aplicar límite si se especifica
        if limite and limite < total:
            total = limite
            print(f"📊 Limitando descarga a {limite:,} sentencias")
        
        sentencias_descargadas = 0
        offset = 0
        batch_size = 100  # Descargar de 100 en 100
        batch_num = 0
        
        url = "https://juris.pjud.cl/busqueda/buscar_sentencias"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
            "busqueda": cabecera,
            "Content-Type": "application/json",
            "Referer": f"https://juris.pjud.cl/busqueda?{nombre_tribunal}",
        }
        
        # Construir filtros con fechas si están definidas
        filtros = {
            "rol": "", "era": "", 
            "fec_desde": self.fecha_desde or "", 
            "fec_hasta": self.fecha_hasta or "", 
            "tipo_norma": "", "num_norma": "", "num_art": "", "num_inciso": "", 
            "todas": "", "algunas": "", "excluir": "", "literal": "", 
            "proximidad": "", "distancia": "", "analisis_s": "", "submaterias": "", 
            "facetas_seleccionadas": [], "filtros_omnibox": [], "ids_comunas_seleccionadas_mapa": []
        }
        
        filtros_json = json.dumps(filtros)

        while sentencias_descargadas < total:
            try:
                payload = {
                    "_token": self.token,
                    "id_buscador": id_buscador,
                    "filtros": filtros_json,
                    "numero_filas_paginacion": str(batch_size),
                    "offset_paginacion": str(offset),
                    "orden": "rel"
                }

                resp = self.session.post(url, headers=headers, json=payload, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                
                if 'response' in data and 'docs' in data['response']:
                    sentencias = data['response']['docs']
                    if not sentencias:
                        print(f"✅ No hay más sentencias para {nombre_tribunal}")
                        break
                    
                    # Guardar batch
                    batch_num += 1
                    batch_file = os.path.join(tribunal_dir, f"batch_{batch_num:06d}.json")
                    
                    with open(batch_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            "tribunal": nombre_tribunal,
                            "batch": batch_num,
                            "offset": offset,
                            "total_sentencias": len(sentencias),
                            "timestamp": datetime.now().isoformat(),
                            "sentencias": sentencias
                        }, f, ensure_ascii=False, indent=2, default=str)
                    
                    sentencias_descargadas += len(sentencias)
                    offset += batch_size
                    
                    # Mostrar progreso
                    porcentaje = (sentencias_descargadas / total) * 100
                    print(f"📊 {nombre_tribunal}: {sentencias_descargadas:,}/{total:,} ({porcentaje:.1f}%) - Batch {batch_num}")
                    
                    # Pequeña pausa para no saturar el servidor
                    time.sleep(0.5)
                    
                else:
                    print(f"❌ Error en respuesta para {nombre_tribunal}: {data}")
                    break
                    
            except Exception as e:
                print(f"❌ Error descargando batch de {nombre_tribunal}: {e}")
                self.estadisticas["total_errores"] += 1
                break
        
        print(f"✅ {nombre_tribunal} completado: {sentencias_descargadas:,} sentencias descargadas")
        self.estadisticas["total_descargado"] += sentencias_descargadas
        self.estadisticas["tribunales_completados"] += 1
        
        return sentencias_descargadas

    def descargar_todos_tribunales(self, limite_por_tribunal=None, max_workers=3):
        """Descarga sentencias de todos los tribunales en paralelo"""
        print("🚀 INICIANDO DESCARGA MASIVA DE SENTENCIAS")
        print("=" * 60)
        
        # Configurar sesión
        if not self.obtener_token():
            return False
        if not self.establecer_contexto():
            return False
        
        print(f"\n📊 Descargando de {len(BUSCADORES)} tribunales...")
        if limite_por_tribunal:
            print(f"📋 Límite por tribunal: {limite_por_tribunal:,} sentencias")
        print(f"⚡ Workers paralelos: {max_workers}")
        print("-" * 60)
        
        # Ejecutar descargas en paralelo
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for nombre, (id_buscador, cabecera) in BUSCADORES.items():
                future = executor.submit(
                    self.descargar_sentencias_tribunal,
                    nombre, id_buscador, cabecera, limite_por_tribunal
                )
                futures.append((nombre, future))
            
            # Procesar resultados
            for nombre, future in futures:
                try:
                    sentencias = future.result()
                    print(f"✅ {nombre}: {sentencias:,} sentencias descargadas")
                except Exception as e:
                    print(f"❌ Error en {nombre}: {e}")
                    self.estadisticas["total_errores"] += 1
        
        # Generar resumen final
        self.generar_resumen()
        return True

    def generar_resumen(self):
        """Genera un resumen de la descarga"""
        fin = datetime.now()
        duracion = fin - self.estadisticas["inicio"]
        
        resumen = {
            "timestamp_inicio": self.estadisticas["inicio"].isoformat(),
            "timestamp_fin": fin.isoformat(),
            "duracion_segundos": duracion.total_seconds(),
            "duracion_humanizada": str(duracion).split('.')[0],
            "estadisticas": self.estadisticas,
            "directorio_salida": self.output_dir,
            "metodo": "API oficial PJUD (misma API de totales)",
            "fuente": "https://juris.pjud.cl/busqueda/buscar_sentencias"
        }
        
        # Guardar resumen
        resumen_file = os.path.join(self.output_dir, "resumen_descarga.json")
        with open(resumen_file, 'w', encoding='utf-8') as f:
            json.dump(resumen, f, ensure_ascii=False, indent=2, default=str)
        
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE DESCARGA")
        print("=" * 60)
        print(f"⏱️  Duración: {duracion}")
        print(f"📁 Directorio: {self.output_dir}")
        print(f"📊 Total descargado: {self.estadisticas['total_descargado']:,} sentencias")
        print(f"🏛️ Tribunales completados: {self.estadisticas['tribunales_completados']}/{self.estadisticas['tribunales_totales']}")
        print(f"❌ Errores: {self.estadisticas['total_errores']}")
        print(f"💾 Resumen guardado en: {resumen_file}")
        print("=" * 60)

def main():
    """Función principal"""
    print("🏛️ SISTEMA DE DESCARGA DE SENTENCIAS - API OFICIAL PJUD")
    print("=" * 60)
    
    # Configuración
    limite_por_tribunal = None  # None = sin límite, o poner número como 1000
    max_workers = 3  # Número de tribunales a procesar en paralelo
    
    # Parámetros de fecha (opcionales)
    fecha_desde = None  # Formato: "2024-01-01"
    fecha_hasta = None  # Formato: "2024-12-31"
    
    # Verificar argumentos de línea de comandos para fechas
    if len(sys.argv) >= 3:
        fecha_desde = sys.argv[1]
        fecha_hasta = sys.argv[2]
        print(f"📅 Filtros por fecha activados:")
        print(f"   Desde: {fecha_desde}")
        print(f"   Hasta: {fecha_hasta}")
    else:
        print("💡 Para filtrar por fecha, usa: python3 descargar_sentencias_api.py YYYY-MM-DD YYYY-MM-DD")
        print("📅 Descargando todas las sentencias (sin filtro de fecha)")
    
    # Crear descargador con filtros de fecha
    descargador = DescargadorSentencias(
        output_dir="output/descarga_api",
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta
    )
    
    # Iniciar descarga
    try:
        descargador.descargar_todos_tribunales(
            limite_por_tribunal=limite_por_tribunal,
            max_workers=max_workers
        )
        print("\n✅ Descarga completada exitosamente!")
        return True
    except KeyboardInterrupt:
        print("\n⏹️ Descarga interrumpida por el usuario")
        return False
    except Exception as e:
        print(f"\n❌ Error en la descarga: {e}")
        return False

if __name__ == "__main__":
    main()
