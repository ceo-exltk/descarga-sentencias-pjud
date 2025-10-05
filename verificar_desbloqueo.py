#!/usr/bin/env python3
"""
Verificador de Desbloqueo del Servidor
Script para verificar periódicamente si se ha levantado el bloqueo
"""

import requests
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/verificacion_desbloqueo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VerificadorDesbloqueo:
    """Verificador automático de desbloqueo del servidor"""
    
    def __init__(self):
        self.base_url = "https://juris.pjud.cl"
        self.session = requests.Session()
        
        # Headers ultra-conservadores
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        })
    
    def verificar_estado_servidor(self):
        """Verifica el estado actual del servidor"""
        logger.info("🔍 Verificando estado del servidor...")
        
        try:
            # Test 1: Conexión básica
            response = self.session.get(self.base_url, timeout=30)
            if response.status_code != 200:
                return False, f"Error conexión básica: HTTP {response.status_code}"
            
            # Test 2: Petición POST ultra-conservadora
            search_url = f"{self.base_url}/busqueda/buscar_sentencias"
            post_data = {
                'pagina': '1',
                'cantidad_registros': '1',  # Solo 1 resultado
                'corte_suprema': 'true'
            }
            
            # Headers específicos para POST
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/busqueda?Corte_Suprema',
                'Origin': self.base_url
            }
            
            response = self.session.post(search_url, data=post_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                logger.info("✅ SERVIDOR DESBLOQUEADO - Se pueden realizar peticiones POST")
                return True, "Servidor funcionando normalmente"
            elif response.status_code == 419:
                logger.warning("🚨 BLOQUEO ACTIVO - HTTP 419")
                return False, "Bloqueo activo (HTTP 419)"
            else:
                logger.warning(f"⚠️ RESPUESTA INESPERADA - HTTP {response.status_code}")
                return False, f"Respuesta inesperada: HTTP {response.status_code}"
                
        except Exception as e:
            logger.error(f"❌ Error verificando servidor: {e}")
            return False, f"Error de conexión: {e}"
    
    def verificar_periodicamente(self, intervalo_horas=6):
        """Verifica el estado del servidor periódicamente"""
        logger.info(f"🔄 Iniciando verificación periódica cada {intervalo_horas} horas")
        logger.info("💡 Presione Ctrl+C para detener")
        
        intervalo_segundos = intervalo_horas * 3600
        intento = 1
        
        try:
            while True:
                logger.info(f"\n{'='*50}")
                logger.info(f"🔍 VERIFICACIÓN #{intento} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*50}")
                
                # Verificar estado
                desbloqueado, mensaje = self.verificar_estado_servidor()
                
                if desbloqueado:
                    logger.info("🎉 ¡SERVIDOR DESBLOQUEADO!")
                    logger.info("✅ Se puede proceder con descarga masiva")
                    logger.info("🚀 Ejecutar: python3 scripts/descarga/descarga_universal_completa.py")
                    break
                else:
                    logger.warning(f"⏸️ {mensaje}")
                    logger.info(f"⏰ Próxima verificación en {intervalo_horas} horas...")
                
                # Guardar resultado
                self.guardar_resultado_verificacion(intento, desbloqueado, mensaje)
                
                intento += 1
                
                # Esperar antes de próxima verificación
                if not desbloqueado:
                    logger.info(f"😴 Esperando {intervalo_horas} horas...")
                    time.sleep(intervalo_segundos)
                
        except KeyboardInterrupt:
            logger.info("\n👋 Verificación detenida por el usuario")
    
    def guardar_resultado_verificacion(self, intento, desbloqueado, mensaje):
        """Guarda el resultado de la verificación"""
        resultado = {
            'intento': intento,
            'fecha': datetime.now().isoformat(),
            'desbloqueado': desbloqueado,
            'mensaje': mensaje
        }
        
        # Crear directorio de logs si no existe
        Path("logs").mkdir(exist_ok=True)
        
        # Guardar en archivo
        log_file = Path("logs/verificacion_desbloqueo.json")
        
        # Cargar resultados existentes
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                resultados = json.load(f)
        else:
            resultados = []
        
        # Agregar nuevo resultado
        resultados.append(resultado)
        
        # Guardar actualizado
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    def mostrar_historial(self):
        """Muestra el historial de verificaciones"""
        log_file = Path("logs/verificacion_desbloqueo.json")
        
        if not log_file.exists():
            logger.info("📁 No hay historial de verificaciones")
            return
        
        with open(log_file, 'r', encoding='utf-8') as f:
            resultados = json.load(f)
        
        logger.info("📊 HISTORIAL DE VERIFICACIONES")
        logger.info("=" * 50)
        
        for resultado in resultados[-10:]:  # Últimos 10
            fecha = resultado['fecha'][:19]  # Solo fecha y hora
            estado = "✅ DESBLOQUEADO" if resultado['desbloqueado'] else "🚨 BLOQUEADO"
            logger.info(f"   {fecha} - {estado} - {resultado['mensaje']}")

def main():
    """Función principal"""
    print("🔍 VERIFICADOR DE DESBLOQUEO DEL SERVIDOR")
    print("=" * 50)
    print("1. Verificar estado actual")
    print("2. Verificación periódica (cada 6 horas)")
    print("3. Verificación periódica (cada 12 horas)")
    print("4. Mostrar historial")
    print("5. Salir")
    print("=" * 50)
    
    verificador = VerificadorDesbloqueo()
    
    while True:
        try:
            opcion = input("Seleccione una opción (1-5): ").strip()
            
            if opcion == "1":
                logger.info("🔍 Verificando estado actual...")
                desbloqueado, mensaje = verificador.verificar_estado_servidor()
                if desbloqueado:
                    print("🎉 ¡SERVIDOR DESBLOQUEADO!")
                else:
                    print(f"⏸️ {mensaje}")
            
            elif opcion == "2":
                verificador.verificar_periodicamente(6)
                break
            
            elif opcion == "3":
                verificador.verificar_periodicamente(12)
                break
            
            elif opcion == "4":
                verificador.mostrar_historial()
            
            elif opcion == "5":
                print("👋 ¡Hasta luego!")
                break
            
            else:
                print("❌ Opción inválida")
            
            if opcion in ["1", "4"]:
                input("\n⏸️ Presione Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n👋 Verificación detenida")
            break

if __name__ == "__main__":
    main()
