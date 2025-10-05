#!/usr/bin/env python3
"""
Descargar sentencias de Tribunales Penales
"""

from descargar_sentencias_api import DescargadorSentencias

def main():
    print("⚖️ DESCARGA TRIBUNALES PENALES")
    print("=" * 40)
    
    # Configuración específica para Penales
    nombre_tribunal = "Penales"
    id_buscador = "268"
    cabecera = "Buscador_Jurisprudencial_de_Tribunales_Penales"
    
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
        
        print(f"\n✅ Tribunales Penales completados: {sentencias_descargadas:,} sentencias")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    main()
