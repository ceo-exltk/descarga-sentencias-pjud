#!/usr/bin/env python3
"""
Monitor en tiempo real para la descarga del universo completo
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys

class MonitorDescargaUniverso:
    def __init__(self, output_dir="output/universo_completo"):
        self.output_dir = Path(output_dir)
        self.estado_file = self.output_dir / "estado_descarga.json"
        self.log_dir = self.output_dir / "logs"
        
    def cargar_estado(self):
        """Cargar estado actual de la descarga"""
        if self.estado_file.exists():
            with open(self.estado_file, 'r') as f:
                return json.load(f)
        return None
    
    def calcular_progreso(self, estado):
        """Calcular progreso general"""
        if not estado:
            return 0, 0, 0
        
        total_estimado = estado.get("total_estimado", 4115881)
        total_descargado = estado.get("total_descargado", 0)
        
        # Calcular progreso por tribunal
        tribunales_completados = 0
        tribunales_total = 7
        
        for tribunal_name, tribunal_data in estado.get("tribunales", {}).items():
            if tribunal_data.get("estado") == "completado":
                tribunales_completados += 1
        
        progreso_general = (total_descargado / total_estimado) * 100 if total_estimado > 0 else 0
        progreso_tribunales = (tribunales_completados / tribunales_total) * 100
        
        return progreso_general, progreso_tribunales, total_descargado
    
    def mostrar_estado_tribunal(self, tribunal_name, tribunal_data):
        """Mostrar estado de un tribunal específico"""
        estado = tribunal_data.get("estado", "no_iniciado")
        total = tribunal_data.get("total", 0)
        descargado = tribunal_data.get("descargado", 0)
        batch_actual = tribunal_data.get("batch_actual", 0)
        
        # Calcular progreso
        progreso = (descargado / total) * 100 if total > 0 else 0
        
        # Emojis según estado
        emoji_estado = {
            "no_iniciado": "⏳",
            "iniciando": "🔄",
            "descargando": "📥",
            "completado": "✅",
            "error": "❌"
        }
        
        emoji = emoji_estado.get(estado, "❓")
        
        print(f"  {emoji} {tribunal_name:<20} | {descargado:>8,} / {total:>8,} | {progreso:>6.1f}% | Batch {batch_actual:>6}")
    
    def mostrar_dashboard(self):
        """Mostrar dashboard completo"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        estado = self.cargar_estado()
        if not estado:
            print("❌ No se encontró estado de descarga")
            return
        
        # Calcular métricas
        progreso_general, progreso_tribunales, total_descargado = self.calcular_progreso(estado)
        
        # Header
        print("🌍 MONITOR DE DESCARGA UNIVERSO COMPLETO")
        print("=" * 80)
        print(f"⏰ Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🚀 Estado general: {estado.get('estado', 'desconocido').upper()}")
        print()
        
        # Progreso general
        print("📊 PROGRESO GENERAL")
        print("-" * 40)
        print(f"📈 Progreso general: {progreso_general:.1f}%")
        print(f"🏛️ Tribunales completados: {progreso_tribunales:.1f}%")
        print(f"📥 Total descargado: {total_descargado:,} sentencias")
        print(f"🎯 Total estimado: {estado.get('total_estimado', 0):,} sentencias")
        print()
        
        # Estado por tribunal
        print("🏛️ ESTADO POR TRIBUNAL")
        print("-" * 80)
        print(f"{'Tribunal':<20} | {'Descargado':>10} | {'Total':>10} | {'Progreso':>8} | {'Batch':>8}")
        print("-" * 80)
        
        # Ordenar tribunales por prioridad
        tribunales_orden = [
            "Corte_de_Apelaciones", "Civiles", "Penales", 
            "Familia", "Laborales", "Corte_Suprema", "Cobranza"
        ]
        
        for tribunal_name in tribunales_orden:
            tribunal_data = estado.get("tribunales", {}).get(tribunal_name, {})
            self.mostrar_estado_tribunal(tribunal_name, tribunal_data)
        
        print("-" * 80)
        
        # Tiempo estimado
        if estado.get("inicio"):
            inicio = datetime.fromisoformat(estado["inicio"])
            tiempo_transcurrido = datetime.now() - inicio
            
            if total_descargado > 0:
                # Calcular tiempo estimado restante
                tasa_descarga = total_descargado / tiempo_transcurrido.total_seconds()
                total_restante = estado.get("total_estimado", 0) - total_descargado
                tiempo_restante = timedelta(seconds=total_restante / tasa_descarga) if tasa_descarga > 0 else timedelta(0)
                
                print(f"⏱️ Tiempo transcurrido: {tiempo_transcurrido}")
                print(f"⏳ Tiempo estimado restante: {tiempo_restante}")
                print(f"📊 Tasa de descarga: {tasa_descarga:.1f} sentencias/segundo")
        
        print()
        print("💡 Presiona Ctrl+C para salir del monitor")
    
    def ejecutar_monitor(self, intervalo=30):
        """Ejecutar monitor en tiempo real"""
        try:
            while True:
                self.mostrar_dashboard()
                time.sleep(intervalo)
        except KeyboardInterrupt:
            print("\n👋 Monitor detenido")

def main():
    """Función principal"""
    monitor = MonitorDescargaUniverso()
    
    if len(sys.argv) > 1:
        intervalo = int(sys.argv[1])
    else:
        intervalo = 30
    
    print(f"🔄 Iniciando monitor (actualización cada {intervalo}s)")
    monitor.ejecutar_monitor(intervalo)

if __name__ == "__main__":
    main()
