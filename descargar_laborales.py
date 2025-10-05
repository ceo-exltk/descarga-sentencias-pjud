#!/usr/bin/env python3
"""
Descargar sentencias de Tribunales Laborales
"""

from descargar_sentencias_api import DescargadorSentencias

def main():
    print("💼 DESCARGA TRIBUNALES LABORALES")
    print("=" * 40)
    
    # Configuración específica para Laborales
    nombre_tribunal = "Laborales"
    id_buscador = "271"
    cabecera = "Buscador_Jurisprudencial_de_Tribunales_Laborales"
    
    # Crear descargador
    descargador = DescargadorSentencias(output_dir=f"output/descarga_{nombre_tribunal.lower()}")
    
    # Configurar sesión
    if not descargador.obtener_token():
        return False
    if not descargador.establecer_contexto():
        return False
    
    # Descargar sentencias
    try:
        sentencias_descargadas = descargador.descargar_sentencias_tribunal(
            nombre_tribunal, id_buscador, cabecera
        )
        
        print(f"\n✅ Tribunales Laborales completados: {sentencias_descargadas:,} sentencias")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    main()
