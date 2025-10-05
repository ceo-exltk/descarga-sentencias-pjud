#!/usr/bin/env python3
"""
Monitor en Tiempo Real para Descarga Universal de Sentencias
Monitorea el progreso de la descarga y muestra estadísticas en tiempo real
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime, timedelta
import threading
import sys

class MonitorDescargaUniversal:
    """Monitor en tiempo real para la descarga universal"""
    
    def __init__(self, output_dir: str = "output/descarga_universal_completa"):
        self.output_dir = Path(output_dir)
        self.tribunales = [
            'Corte_Suprema',
            'Corte_de_Apelaciones', 
            'Laborales',
            'Penales',
            'Familia',
            'Civiles',
            'Cobranza'
        ]
        self.monitoring = True
        self.stats_previas = {}
    
    def limpiar_pantalla(self):
        """Limpia la pantalla del terminal"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def obtener_estadisticas_tribunal(self, tribunal_type: str) -> dict:
        """Obtiene estadísticas de un tribunal específico"""
        tribunal_dir = self.output_dir / tribunal_type
        
        if not tribunal_dir.exists():
            return {
                'tribunal_type': tribunal_type,
                'workers_completados': 0,
                'total_sentencias': 0,
                'total_con_texto': 0,
                'total_con_roles': 0,
                'archivos_procesados': 0,
                'estado': 'NO_INICIADO'
            }
        
        # Contar archivos de workers
        worker_dirs = [d for d in tribunal_dir.iterdir() if d.is_dir() and d.name.startswith(f"{tribunal_type}_worker_")]
        archivos_batch = list(tribunal_dir.glob("**/batch_*.json"))
        
        # Leer resúmenes de workers
        total_sentencias = 0
        total_con_texto = 0
        total_con_roles = 0
        workers_completados = 0
        
        for worker_dir in worker_dirs:
            resumen_file = worker_dir / "resumen_worker.json"
            if resumen_file.exists():
                try:
                    with open(resumen_file, 'r', encoding='utf-8') as f:
                        resumen = json.load(f)
                        total_sentencias += resumen.get('total_sentencias', 0)
                        total_con_texto += resumen.get('total_con_texto', 0)
                        total_con_roles += resumen.get('total_con_roles', 0)
                        workers_completados += 1
                except:
                    continue
        
        # Determinar estado
        if workers_completados == 0:
            estado = 'NO_INICIADO'
        elif workers_completados < len(worker_dirs):
            estado = 'EN_PROGRESO'
        else:
            estado = 'COMPLETADO'
        
        return {
            'tribunal_type': tribunal_type,
            'workers_completados': workers_completados,
            'total_workers': len(worker_dirs),
            'total_sentencias': total_sentencias,
            'total_con_texto': total_con_texto,
            'total_con_roles': total_con_roles,
            'archivos_procesados': len(archivos_batch),
            'estado': estado
        }
    
    def calcular_velocidad_descarga(self, stats_actuales: dict) -> dict:
        """Calcula la velocidad de descarga"""
        velocidades = {}
        
        for tribunal, stats in stats_actuales.items():
            if tribunal in self.stats_previas:
                prev_stats = self.stats_previas[tribunal]
                
                # Calcular diferencia de sentencias
                sentencias_previas = prev_stats.get('total_sentencias', 0)
                sentencias_actuales = stats.get('total_sentencias', 0)
                diferencia_sentencias = sentencias_actuales - sentencias_previas
                
                # Calcular diferencia de tiempo (asumiendo 5 segundos entre actualizaciones)
                tiempo_diferencia = 5  # segundos
                
                if tiempo_diferencia > 0:
                    velocidad_sentencias_por_segundo = diferencia_sentencias / tiempo_diferencia
                    velocidad_sentencias_por_hora = velocidad_sentencias_por_segundo * 3600
                else:
                    velocidad_sentencias_por_hora = 0
                
                velocidades[tribunal] = {
                    'sentencias_por_hora': velocidad_sentencias_por_hora,
                    'diferencia_sentencias': diferencia_sentencias
                }
            else:
                velocidades[tribunal] = {
                    'sentencias_por_hora': 0,
                    'diferencia_sentencias': 0
                }
        
        return velocidades
    
    def mostrar_dashboard(self, stats: dict, velocidades: dict):
        """Muestra el dashboard de monitoreo"""
        self.limpiar_pantalla()
        
        print("🌍 MONITOR DE DESCARGA UNIVERSAL DE SENTENCIAS")
        print("=" * 80)
        print(f"⏰ Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Estadísticas generales
        total_sentencias = sum(s.get('total_sentencias', 0) for s in stats.values())
        total_con_texto = sum(s.get('total_con_texto', 0) for s in stats.values())
        total_con_roles = sum(s.get('total_con_roles', 0) for s in stats.values())
        total_workers_completados = sum(s.get('workers_completados', 0) for s in stats.values())
        total_archivos = sum(s.get('archivos_procesados', 0) for s in stats.values())
        
        print(f"\n📊 ESTADÍSTICAS GENERALES:")
        print(f"   📚 Total sentencias: {total_sentencias:,}")
        print(f"   📝 Con texto: {total_con_texto:,} ({total_con_texto/total_sentencias*100:.1f}%)" if total_sentencias > 0 else "   📝 Con texto: 0 (0.0%)")
        print(f"   🔢 Con roles: {total_con_roles:,} ({total_con_roles/total_sentencias*100:.1f}%)" if total_sentencias > 0 else "   🔢 Con roles: 0 (0.0%)")
        print(f"   👥 Workers completados: {total_workers_completados}")
        print(f"   📄 Archivos procesados: {total_archivos:,}")
        
        # Velocidad total
        velocidad_total = sum(v.get('sentencias_por_hora', 0) for v in velocidades.values())
        print(f"   🚀 Velocidad total: {velocidad_total:,.0f} sentencias/hora")
        
        print(f"\n🏛️  ESTADO POR TRIBUNAL:")
        print("-" * 80)
        print(f"{'Tribunal':<25} {'Estado':<12} {'Workers':<10} {'Sentencias':<12} {'Velocidad/h':<12}")
        print("-" * 80)
        
        for tribunal in self.tribunales:
            if tribunal in stats:
                s = stats[tribunal]
                v = velocidades.get(tribunal, {})
                
                estado_icon = {
                    'NO_INICIADO': '⏳',
                    'EN_PROGRESO': '🔄',
                    'COMPLETADO': '✅'
                }.get(s.get('estado', 'NO_INICIADO'), '❓')
                
                estado_texto = f"{estado_icon} {s.get('estado', 'NO_INICIADO')}"
                workers_texto = f"{s.get('workers_completados', 0)}/{s.get('total_workers', 0)}"
                sentencias_texto = f"{s.get('total_sentencias', 0):,}"
                velocidad_texto = f"{v.get('sentencias_por_hora', 0):,.0f}"
                
                print(f"{tribunal:<25} {estado_texto:<12} {workers_texto:<10} {sentencias_texto:<12} {velocidad_texto:<12}")
        
        print("-" * 80)
        
        # Tribunales completados
        tribunales_completados = [t for t, s in stats.items() if s.get('estado') == 'COMPLETADO']
        tribunales_en_progreso = [t for t, s in stats.items() if s.get('estado') == 'EN_PROGRESO']
        tribunales_no_iniciados = [t for t, s in stats.items() if s.get('estado') == 'NO_INICIADO']
        
        print(f"\n📈 PROGRESO GENERAL:")
        print(f"   ✅ Completados: {len(tribunales_completados)}/{len(self.tribunales)}")
        print(f"   🔄 En progreso: {len(tribunales_en_progreso)}")
        print(f"   ⏳ No iniciados: {len(tribunales_no_iniciados)}")
        
        if tribunales_completados:
            print(f"\n✅ TRIBUNALES COMPLETADOS:")
            for tribunal in tribunales_completados:
                s = stats[tribunal]
                print(f"   🏛️  {tribunal}: {s.get('total_sentencias', 0):,} sentencias")
        
        if tribunales_en_progreso:
            print(f"\n🔄 TRIBUNALES EN PROGRESO:")
            for tribunal in tribunales_en_progreso:
                s = stats[tribunal]
                v = velocidades.get(tribunal, {})
                print(f"   🏛️  {tribunal}: {s.get('total_sentencias', 0):,} sentencias ({v.get('sentencias_por_hora', 0):,.0f}/h)")
        
        print(f"\n💡 Presione Ctrl+C para salir del monitor")
        print("=" * 80)
    
    def monitorear(self, intervalo: int = 5):
        """Inicia el monitoreo en tiempo real"""
        print("🚀 Iniciando monitor de descarga universal...")
        print("⏰ Actualizando cada 5 segundos...")
        print("💡 Presione Ctrl+C para salir")
        
        try:
            while self.monitoring:
                # Obtener estadísticas actuales
                stats_actuales = {}
                for tribunal in self.tribunales:
                    stats_actuales[tribunal] = self.obtener_estadisticas_tribunal(tribunal)
                
                # Calcular velocidades
                velocidades = self.calcular_velocidad_descarga(stats_actuales)
                
                # Mostrar dashboard
                self.mostrar_dashboard(stats_actuales, velocidades)
                
                # Guardar estadísticas para próxima iteración
                self.stats_previas = stats_actuales.copy()
                
                # Esperar antes de próxima actualización
                time.sleep(intervalo)
                
        except KeyboardInterrupt:
            print("\n\n👋 Monitor detenido por el usuario")
            self.monitoring = False
        except Exception as e:
            print(f"\n❌ Error en monitor: {e}")
            self.monitoring = False

def main():
    """Función principal"""
    print("🌍 MONITOR DE DESCARGA UNIVERSAL DE SENTENCIAS")
    print("=" * 50)
    
    # Verificar que existe el directorio de salida
    output_dir = "output/descarga_universal_completa"
    if not Path(output_dir).exists():
        print(f"❌ Directorio de salida no encontrado: {output_dir}")
        print("💡 Asegúrese de que la descarga esté en progreso")
        return
    
    # Crear y ejecutar monitor
    monitor = MonitorDescargaUniversal(output_dir)
    monitor.monitorear()

if __name__ == "__main__":
    main()







