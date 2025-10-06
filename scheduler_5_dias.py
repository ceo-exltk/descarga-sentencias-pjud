#!/usr/bin/env python3
"""
Scheduler para ejecutar la descarga del universo completo durante 5 días
Con pausas inteligentes y recuperación automática
"""

import os
import sys
import time
import subprocess
import signal
import json
from datetime import datetime, timedelta
from pathlib import Path

class Scheduler5Dias:
    def __init__(self, output_dir="output/universo_completo"):
        self.output_dir = Path(output_dir)
        self.estado_file = self.output_dir / "scheduler_estado.json"
        self.log_file = self.output_dir / "scheduler.log"
        
        # Configuración de horarios (UTC-3)
        self.horario_inicio = 6  # 6:00 AM
        self.horario_fin = 22    # 10:00 PM
        self.pausa_nocturna = False  # Sin pausas nocturnas
        
        # Configuración de pausas
        self.pausa_entre_tribunales = 60   # 1 minuto entre tribunales
        self.pausa_por_error = 300         # 5 minutos por error
        self.pausa_ciclo = 300             # 5 minutos entre ciclos
        
        # Estado
        self.ejecutando = False
        self.fecha_inicio = datetime.now()
        self.fecha_fin = self.fecha_inicio + timedelta(days=5)
        
        # Configurar manejo de señales
        signal.signal(signal.SIGINT, self.manejar_interrupcion)
        signal.signal(signal.SIGTERM, self.manejar_interrupcion)
    
    def log(self, mensaje):
        """Escribir log con timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {mensaje}"
        
        print(log_line)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    
    def cargar_estado(self):
        """Cargar estado del scheduler"""
        if self.estado_file.exists():
            with open(self.estado_file, 'r') as f:
                return json.load(f)
        return {
            "inicio": self.fecha_inicio.isoformat(),
            "fin_estimado": self.fecha_fin.isoformat(),
            "tribunales_completados": [],
            "tribunales_en_progreso": [],
            "errores": 0,
            "pausas_nocturnas": 0,
            "estado": "iniciando"
        }
    
    def guardar_estado(self, estado):
        """Guardar estado del scheduler"""
        estado["ultima_actualizacion"] = datetime.now().isoformat()
        with open(self.estado_file, 'w') as f:
            json.dump(estado, f, indent=2)
    
    def es_horario_valido(self):
        """Verificar si es horario válido para ejecutar"""
        ahora = datetime.now()
        hora_actual = ahora.hour
        
        if self.pausa_nocturna:
            return self.horario_inicio <= hora_actual < self.horario_fin
        return True
    
    def calcular_tiempo_restante_pausa_nocturna(self):
        """Calcular tiempo restante de pausa nocturna"""
        ahora = datetime.now()
        mañana_6am = ahora.replace(hour=self.horario_inicio, minute=0, second=0, microsecond=0)
        
        if ahora.hour >= self.horario_fin:
            mañana_6am += timedelta(days=1)
        
        return mañana_6am - ahora
    
    def ejecutar_pausa_nocturna(self):
        """Ejecutar pausa nocturna"""
        self.log("🌙 Iniciando pausa nocturna...")
        
        tiempo_restante = self.calcular_tiempo_restante_pausa_nocturna()
        self.log(f"⏰ Pausa hasta: {datetime.now() + tiempo_restante}")
        
        # Pausar en bloques de 1 hora para poder interrumpir
        while tiempo_restante.total_seconds() > 0:
            if not self.ejecutando:
                break
            
            pausa_segundos = min(3600, tiempo_restante.total_seconds())  # 1 hora máximo
            time.sleep(pausa_segundos)
            tiempo_restante -= timedelta(seconds=pausa_segundos)
            
            if tiempo_restante.total_seconds() > 0:
                self.log(f"⏳ Pausa nocturna: {tiempo_restante} restantes")
        
        self.log("🌅 Pausa nocturna completada")
    
    def ejecutar_descarga_tribunal(self, tribunal_name):
        """Ejecutar descarga de un tribunal específico"""
        self.log(f"🏛️ Iniciando descarga de {tribunal_name}")
        
        try:
            # Ejecutar script de descarga con timeout
            cmd = [
                sys.executable, 
                "descarga_universo_completo.py",
                "--tribunal", tribunal_name
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=7200  # 2 horas máximo por tribunal
            )
            
            if result.returncode == 0:
                self.log(f"✅ {tribunal_name} completado exitosamente")
                return True
            else:
                self.log(f"❌ Error en {tribunal_name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"⏰ Timeout en {tribunal_name} - continuando con siguiente")
            return False
        except Exception as e:
            self.log(f"❌ Error ejecutando {tribunal_name}: {e}")
            return False
    
    def ejecutar_ciclo_descarga(self):
        """Ejecutar un ciclo completo de descarga"""
        self.log("🚀 Iniciando ciclo de descarga")
        
        # Orden de tribunales por prioridad
        tribunales = [
            "Corte_de_Apelaciones",  # Más grande
            "Civiles",
            "Penales", 
            "Familia",
            "Laborales",
            "Corte_Suprema",
            "Cobranza"  # Más pequeño
        ]
        
        estado = self.cargar_estado()
        tribunales_completados = set(estado.get("tribunales_completados", []))
        
        for tribunal in tribunales:
            if not self.ejecutando:
                break
            
            if tribunal in tribunales_completados:
                self.log(f"⏭️ {tribunal} ya completado - saltando")
                continue
            
            # Verificar horario antes de cada tribunal
            if not self.es_horario_valido():
                self.log("🌙 Fuera de horario - iniciando pausa nocturna")
                self.pausa_nocturna()
                continue
            
            # Ejecutar descarga
            estado["tribunales_en_progreso"] = [tribunal]
            self.guardar_estado(estado)
            
            exito = self.ejecutar_descarga_tribunal(tribunal)
            
            if exito:
                tribunales_completados.add(tribunal)
                estado["tribunales_completados"] = list(tribunales_completados)
                estado["tribunales_en_progreso"] = []
                self.guardar_estado(estado)
                
                self.log(f"✅ {tribunal} agregado a completados")
            else:
                estado["errores"] += 1
                self.guardar_estado(estado)
                
                self.log(f"❌ Error en {tribunal} - pausa de {self.pausa_por_error}s")
                time.sleep(self.pausa_por_error)
            
            # Pausa entre tribunales
            if tribunal != tribunales[-1]:  # No pausar después del último
                self.log(f"⏸️ Pausa entre tribunales: {self.pausa_entre_tribunales}s")
                time.sleep(self.pausa_entre_tribunales)
    
    def ejecutar_scheduler(self):
        """Ejecutar scheduler principal"""
        self.ejecutando = True
        self.log("🚀 INICIANDO SCHEDULER DE 5 DÍAS")
        self.log(f"📅 Fecha inicio: {self.fecha_inicio}")
        self.log(f"📅 Fecha fin: {self.fecha_fin}")
        self.log(f"⏰ Horario: {self.horario_inicio}:00 - {self.horario_fin}:00")
        
        estado = self.cargar_estado()
        estado["estado"] = "ejecutando"
        self.guardar_estado(estado)
        
        try:
            while self.ejecutando and datetime.now() < self.fecha_fin:
                # Ejecutar descarga continua (sin pausas nocturnas)
                self.log("🚀 Ejecutando descarga continua")
                self.ejecutar_ciclo_descarga()
                
                # Verificar si todos los tribunales están completos
                estado = self.cargar_estado()
                if len(estado.get("tribunales_completados", [])) >= 7:
                    self.log("🎉 ¡TODOS LOS TRIBUNALES COMPLETADOS!")
                    break
                
                # Pausa corta antes del siguiente ciclo
                if self.ejecutando:
                    self.log(f"⏸️ Pausa de {self.pausa_ciclo}s antes del siguiente ciclo")
                    time.sleep(self.pausa_ciclo)
            
            if datetime.now() >= self.fecha_fin:
                self.log("⏰ Tiempo de 5 días completado")
            
            estado["estado"] = "completado"
            self.guardar_estado(estado)
            
        except Exception as e:
            self.log(f"❌ Error en scheduler: {e}")
            estado["estado"] = "error"
            self.guardar_estado(estado)
        
        self.log("🏁 Scheduler finalizado")
    
    def manejar_interrupcion(self, signum, frame):
        """Manejar interrupciones (Ctrl+C)"""
        self.log("⏹️ Interrupción recibida - deteniendo scheduler...")
        self.ejecutando = False
        
        estado = self.cargar_estado()
        estado["estado"] = "interrumpido"
        self.guardar_estado(estado)
        
        self.log("💾 Estado guardado - puedes continuar más tarde")
        sys.exit(0)

def main():
    """Función principal"""
    print("📅 SCHEDULER DE DESCARGA - 5 DÍAS")
    print("=" * 50)
    print("⚠️  Este scheduler ejecutará la descarga durante 5 días CONTINUOS")
    print("⚠️  Sin pausas nocturnas - ejecución 24/7")
    print("⚠️  Presiona Ctrl+C para detener de forma segura")
    print("=" * 50)
    
    # Confirmar ejecución
    respuesta = input("\n¿Iniciar scheduler de 5 días? (s/N): ").lower()
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Scheduler cancelado")
        return
    
    # Crear y ejecutar scheduler
    scheduler = Scheduler5Dias()
    scheduler.ejecutar_scheduler()

if __name__ == "__main__":
    main()
