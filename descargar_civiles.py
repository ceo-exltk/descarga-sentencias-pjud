#!/usr/bin/env python3
"""
Descargar sentencias de Tribunales Civiles
"""

from descargar_sentencias_api import DescargadorSentencias

def main():
    print("📋 DESCARGA TRIBUNALES CIVILES")
    print("=" * 40)
    
    # Configuración específica para Civiles
    nombre_tribunal = "Civiles"
    id_buscador = "328"
    cabecera = "Buscador_Jurisprudencial_de_Tribunales_Civiles"
    
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
        
        print(f"\n✅ Tribunales Civiles completados: {sentencias_descargadas:,} sentencias")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    main()
