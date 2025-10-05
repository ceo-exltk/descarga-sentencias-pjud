#!/usr/bin/env python3
"""
Descargar sentencias por tipo de tribunal específico
Permite descargar solo el tribunal que necesites
"""

import sys
from descargar_sentencias_api import DescargadorSentencias

# Configuración de tribunales disponibles
TRIBUNALES_DISPONIBLES = {
    "1": ("Corte_Suprema", "528", "Buscador_Jurisprudencial_de_la_Corte_Suprema"),
    "2": ("Corte_de_Apelaciones", "168", "Buscador_Jurisprudencial_de_Cortes_de_Apelaciones"),
    "3": ("Laborales", "271", "Buscador_Jurisprudencial_de_Tribunales_Laborales"),
    "4": ("Penales", "268", "Buscador_Jurisprudencial_de_Tribunales_Penales"),
    "5": ("Familia", "270", "Buscador_Jurisprudencial_de_Tribunales_de_Familia"),
    "6": ("Civiles", "328", "Buscador_Jurisprudencial_de_Tribunales_Civiles"),
    "7": ("Cobranza", "269", "Buscador_Jurisprudencial_de_Tribunales_de_Cobranza"),
}

def mostrar_menu():
    """Muestra el menú de tribunales disponibles"""
    print("🏛️ DESCARGA POR TRIBUNAL - SISTEMA PJUD")
    print("=" * 50)
    print("Selecciona el tribunal a descargar:")
    print()
    
    for codigo, (nombre, id_buscador, cabecera) in TRIBUNALES_DISPONIBLES.items():
        print(f"{codigo}. {nombre.replace('_', ' ')}")
    
    print()
    print("0. Salir")
    print("-" * 50)

def descargar_tribunal_especifico(nombre_tribunal, id_buscador, cabecera, limite=None):
    """Descarga sentencias de un tribunal específico"""
    print(f"\n🏛️ DESCARGA DE {nombre_tribunal.replace('_', ' ').upper()}")
    print("=" * 60)
    
    # Crear descargador
    output_dir = f"output/descarga_{nombre_tribunal.lower()}"
    descargador = DescargadorSentencias(output_dir=output_dir)
    
    # Configurar sesión
    if not descargador.obtener_token():
        return False
    if not descargador.establecer_contexto():
        return False
    
    # Descargar sentencias
    try:
        sentencias_descargadas = descargador.descargar_sentencias_tribunal(
            nombre_tribunal, id_buscador, cabecera, limite
        )
        
        print(f"\n✅ Descarga completada: {sentencias_descargadas:,} sentencias")
        print(f"📁 Archivos guardados en: {output_dir}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en la descarga: {e}")
        return False

def main():
    """Función principal"""
    while True:
        mostrar_menu()
        
        try:
            opcion = input("Ingresa el número del tribunal (0 para salir): ").strip()
            
            if opcion == "0":
                print("👋 ¡Hasta luego!")
                break
            
            if opcion not in TRIBUNALES_DISPONIBLES:
                print("❌ Opción inválida. Intenta nuevamente.")
                continue
            
            # Obtener datos del tribunal
            nombre, id_buscador, cabecera = TRIBUNALES_DISPONIBLES[opcion]
            
            # Preguntar por límite
            print(f"\n📊 Descargando: {nombre.replace('_', ' ')}")
            print("💡 Tip: Deja vacío para descargar todas las sentencias")
            limite_input = input("Ingresa límite de sentencias (opcional): ").strip()
            
            limite = None
            if limite_input:
                try:
                    limite = int(limite_input)
                    if limite <= 0:
                        print("❌ El límite debe ser mayor a 0")
                        continue
                except ValueError:
                    print("❌ El límite debe ser un número válido")
                    continue
            
            # Confirmar descarga
            print(f"\n🎯 CONFIGURACIÓN:")
            print(f"   Tribunal: {nombre.replace('_', ' ')}")
            print(f"   Límite: {'Todas las sentencias' if limite is None else f'{limite:,} sentencias'}")
            print(f"   Directorio: output/descarga_{nombre.lower()}")
            
            confirmar = input("\n¿Continuar con la descarga? (s/n): ").strip().lower()
            if confirmar not in ['s', 'si', 'sí', 'y', 'yes']:
                print("⏹️ Descarga cancelada")
                continue
            
            # Ejecutar descarga
            print(f"\n🚀 Iniciando descarga...")
            exito = descargar_tribunal_especifico(nombre, id_buscador, cabecera, limite)
            
            if exito:
                print(f"\n✅ ¡Descarga completada exitosamente!")
            else:
                print(f"\n❌ La descarga falló")
            
            # Preguntar si continuar
            continuar = input("\n¿Descargar otro tribunal? (s/n): ").strip().lower()
            if continuar not in ['s', 'si', 'sí', 'y', 'yes']:
                print("👋 ¡Hasta luego!")
                break
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Operación cancelada por el usuario")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            break

if __name__ == "__main__":
    main()
