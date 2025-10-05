#!/usr/bin/env python3
"""
Descargar sentencias de Tribunales de Familia
"""

from descargar_sentencias_api import DescargadorSentencias

def main():
    print("👨‍👩‍👧‍👦 DESCARGA TRIBUNALES DE FAMILIA")
    print("=" * 40)
    
    # Configuración específica para Familia
    nombre_tribunal = "Familia"
    id_buscador = "270"
    cabecera = "Buscador_Jurisprudencial_de_Tribunales_de_Familia"
    
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
        
        print(f"\n✅ Tribunales de Familia completados: {sentencias_descargadas:,} sentencias")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    main()
