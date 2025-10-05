#!/usr/bin/env python3
"""
Configurador Rápido para Descarga Universal de Sentencias
Permite configurar workers y tribunales antes de la descarga
"""

import json
import os
from pathlib import Path
from datetime import datetime

class ConfiguradorDescargaUniversal:
    """Configurador para la descarga universal de sentencias"""
    
    def __init__(self):
        self.config_file = Path("config_descarga_universal.json")
        self.config_default = {
            "max_workers_por_tribunal": 50,
            "pausa_entre_tribunales_segundos": 30,
            "timeout_requests_segundos": 30,
            "tribunales_habilitados": {
                "Corte_Suprema": {
                    "habilitado": True,
                    "max_workers": 50,
                    "total_pages_estimado": 2615,
                    "descripcion": "Corte Suprema de Chile"
                },
                "Corte_de_Apelaciones": {
                    "habilitado": True,
                    "max_workers": 50,
                    "total_pages_estimado": 150989,
                    "descripcion": "Cortes de Apelaciones"
                },
                "Laborales": {
                    "habilitado": True,
                    "max_workers": 50,
                    "total_pages_estimado": 17396,
                    "descripcion": "Tribunales Laborales"
                },
                "Penales": {
                    "habilitado": True,
                    "max_workers": 50,
                    "total_pages_estimado": 22801,
                    "descripcion": "Tribunales Penales"
                },
                "Familia": {
                    "habilitado": True,
                    "max_workers": 50,
                    "total_pages_estimado": 11335,
                    "descripcion": "Tribunales de Familia"
                },
                "Civiles": {
                    "habilitado": True,
                    "max_workers": 50,
                    "total_pages_estimado": 33313,
                    "descripcion": "Tribunales Civiles"
                },
                "Cobranza": {
                    "habilitado": True,
                    "max_workers": 50,
                    "total_pages_estimado": 2613,
                    "descripcion": "Tribunales de Cobranza"
                }
            },
            "configuracion_avanzada": {
                "usar_proxies": False,
                "retry_attempts": 3,
                "delay_entre_requests_ms": 100,
                "guardar_logs_detallados": True,
                "comprimir_archivos": False
            }
        }
    
    def cargar_configuracion(self):
        """Carga la configuración desde archivo"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error cargando configuración: {e}")
                return self.config_default
        return self.config_default
    
    def guardar_configuracion(self, config):
        """Guarda la configuración en archivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"✅ Configuración guardada en {self.config_file}")
        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")
    
    def mostrar_configuracion_actual(self, config):
        """Muestra la configuración actual"""
        print("\n" + "=" * 70)
        print("⚙️  CONFIGURACIÓN ACTUAL DE DESCARGA UNIVERSAL")
        print("=" * 70)
        
        print(f"\n👥 CONFIGURACIÓN GENERAL:")
        print(f"   Workers por tribunal: {config['max_workers_por_tribunal']}")
        print(f"   Pausa entre tribunales: {config['pausa_entre_tribunales_segundos']} segundos")
        print(f"   Timeout requests: {config['timeout_requests_segundos']} segundos")
        
        print(f"\n🏛️  TRIBUNALES CONFIGURADOS:")
        total_workers = 0
        total_pages = 0
        
        for tribunal, info in config['tribunales_habilitados'].items():
            status = "✅ HABILITADO" if info['habilitado'] else "❌ DESHABILITADO"
            print(f"   {tribunal}: {status}")
            print(f"      👥 Workers: {info['max_workers']}")
            print(f"      📄 Páginas estimadas: {info['total_pages_estimado']:,}")
            print(f"      📝 Descripción: {info['descripcion']}")
            
            if info['habilitado']:
                total_workers += info['max_workers']
                total_pages += info['total_pages_estimado']
        
        print(f"\n📊 RESUMEN TOTAL:")
        print(f"   👥 Total workers: {total_workers:,}")
        print(f"   📄 Total páginas: {total_pages:,}")
        print(f"   🏛️  Tribunales habilitados: {sum(1 for t in config['tribunales_habilitados'].values() if t['habilitado'])}")
        
        print(f"\n🔧 CONFIGURACIÓN AVANZADA:")
        for key, value in config['configuracion_avanzada'].items():
            print(f"   {key}: {value}")
    
    def configurar_workers_por_tribunal(self, config):
        """Configura el número de workers por tribunal"""
        print(f"\n👥 CONFIGURAR WORKERS POR TRIBUNAL")
        print("-" * 50)
        
        for tribunal, info in config['tribunales_habilitados'].items():
            if info['habilitado']:
                print(f"\n{tribunal} - {info['descripcion']}")
                print(f"Páginas estimadas: {info['total_pages_estimado']:,}")
                print(f"Workers actuales: {info['max_workers']}")
                
                try:
                    nuevo_max_workers = input(f"Ingrese nuevo número de workers (Enter para mantener {info['max_workers']}): ").strip()
                    if nuevo_max_workers:
                        nuevo_max_workers = int(nuevo_max_workers)
                        if nuevo_max_workers > 0:
                            info['max_workers'] = nuevo_max_workers
                            print(f"✅ Workers actualizados a {nuevo_max_workers}")
                        else:
                            print("⚠️ Número inválido, manteniendo valor actual")
                except ValueError:
                    print("⚠️ Valor inválido, manteniendo valor actual")
    
    def habilitar_deshabilitar_tribunales(self, config):
        """Permite habilitar/deshabilitar tribunales específicos"""
        print(f"\n🏛️  HABILITAR/DESHABILITAR TRIBUNALES")
        print("-" * 50)
        
        for tribunal, info in config['tribunales_habilitados'].items():
            status_actual = "HABILITADO" if info['habilitado'] else "DESHABILITADO"
            print(f"\n{tribunal} - {info['descripcion']}")
            print(f"Estado actual: {status_actual}")
            print(f"Páginas estimadas: {info['total_pages_estimado']:,}")
            
            respuesta = input(f"¿Habilitar este tribunal? (s/n/Enter para mantener): ").lower().strip()
            if respuesta == 's':
                info['habilitado'] = True
                print("✅ Tribunal habilitado")
            elif respuesta == 'n':
                info['habilitado'] = False
                print("❌ Tribunal deshabilitado")
            else:
                print("⏭️ Estado mantenido")
    
    def configurar_parametros_generales(self, config):
        """Configura parámetros generales"""
        print(f"\n⚙️  CONFIGURAR PARÁMETROS GENERALES")
        print("-" * 50)
        
        # Workers por tribunal
        try:
            nuevo_max_workers = input(f"Workers por tribunal (actual: {config['max_workers_por_tribunal']}): ").strip()
            if nuevo_max_workers:
                config['max_workers_por_tribunal'] = int(nuevo_max_workers)
        except ValueError:
            print("⚠️ Valor inválido, manteniendo valor actual")
        
        # Pausa entre tribunales
        try:
            nueva_pausa = input(f"Pausa entre tribunales en segundos (actual: {config['pausa_entre_tribunales_segundos']}): ").strip()
            if nueva_pausa:
                config['pausa_entre_tribunales_segundos'] = int(nueva_pausa)
        except ValueError:
            print("⚠️ Valor inválido, manteniendo valor actual")
        
        # Timeout
        try:
            nuevo_timeout = input(f"Timeout de requests en segundos (actual: {config['timeout_requests_segundos']}): ").strip()
            if nuevo_timeout:
                config['timeout_requests_segundos'] = int(nuevo_timeout)
        except ValueError:
            print("⚠️ Valor inválido, manteniendo valor actual")
    
    def ejecutar_configuracion_interactiva(self):
        """Ejecuta la configuración interactiva"""
        print("🌍 CONFIGURADOR DE DESCARGA UNIVERSAL DE SENTENCIAS")
        print("=" * 70)
        
        # Cargar configuración actual
        config = self.cargar_configuracion()
        
        while True:
            print("\n" + "=" * 70)
            print("📋 MENÚ DE CONFIGURACIÓN")
            print("=" * 70)
            print("1. 📊 Ver configuración actual")
            print("2. 👥 Configurar workers por tribunal")
            print("3. 🏛️  Habilitar/deshabilitar tribunales")
            print("4. ⚙️  Configurar parámetros generales")
            print("5. 💾 Guardar configuración")
            print("6. 🚀 Iniciar descarga con configuración actual")
            print("7. ❌ Salir")
            
            opcion = input("\nSeleccione una opción (1-7): ").strip()
            
            if opcion == '1':
                self.mostrar_configuracion_actual(config)
            elif opcion == '2':
                self.configurar_workers_por_tribunal(config)
            elif opcion == '3':
                self.habilitar_deshabilitar_tribunales(config)
            elif opcion == '4':
                self.configurar_parametros_generales(config)
            elif opcion == '5':
                self.guardar_configuracion(config)
            elif opcion == '6':
                self.iniciar_descarga(config)
                break
            elif opcion == '7':
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida, intente nuevamente")
    
    def iniciar_descarga(self, config):
        """Inicia la descarga con la configuración actual"""
        print(f"\n🚀 INICIANDO DESCARGA UNIVERSAL")
        print("=" * 50)
        
        # Mostrar resumen de configuración
        tribunales_habilitados = [t for t, info in config['tribunales_habilitados'].items() if info['habilitado']]
        total_workers = sum(info['max_workers'] for t, info in config['tribunales_habilitados'].items() if info['habilitado'])
        total_pages = sum(info['total_pages_estimado'] for t, info in config['tribunales_habilitados'].items() if info['habilitado'])
        
        print(f"🏛️  Tribunales a procesar: {len(tribunales_habilitados)}")
        print(f"👥 Total workers: {total_workers:,}")
        print(f"📄 Total páginas estimadas: {total_pages:,}")
        
        # Confirmar inicio
        respuesta = input(f"\n¿Iniciar descarga con esta configuración? (s/n): ").lower().strip()
        if respuesta == 's':
            print("🚀 Iniciando descarga...")
            # Aquí se ejecutaría el script de descarga
            os.system("python3 descarga_universal_completa.py")
        else:
            print("❌ Descarga cancelada")

def main():
    """Función principal"""
    configurador = ConfiguradorDescargaUniversal()
    configurador.ejecutar_configuracion_interactiva()

if __name__ == "__main__":
    main()







