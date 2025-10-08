#!/usr/bin/env python3
"""
Preparar sentencias descargadas para carga en Supabase
Transforma el formato de la API PJUD al formato de Supabase
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def preparar_sentencias_para_supabase(input_dir):
    """Preparar sentencias para Supabase"""
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"❌ Error: Directorio {input_dir} no existe")
        return False
    
    # Buscar archivos JSON con sentencias
    archivos_json = list(input_path.glob("sentencias_*.json"))
    
    if not archivos_json:
        print(f"⚠️ No se encontraron archivos de sentencias en {input_dir}")
        return False
    
    print(f"📄 Encontrados {len(archivos_json)} archivos de sentencias")
    
    todas_sentencias = []
    
    for archivo in archivos_json:
        print(f"📖 Procesando {archivo.name}...")
        
        with open(archivo, 'r', encoding='utf-8') as f:
            sentencias = json.load(f)
        
        # Mapear campos de la API PJUD a la estructura de la tabla Supabase
        for sentencia in sentencias:
            sentencia_supabase = {
                # Campos que coinciden con la tabla Supabase
                'rol_numero': sentencia.get('rol_era_sup_s'),
                'rol_completo': sentencia.get('rol_era_sup_s'),
                'caratulado': sentencia.get('des_contenido_s', '')[:500] if sentencia.get('des_contenido_s') else '',  # Limitar longitud
                'fecha_sentencia': sentencia.get('fec_sentencia_d', '').split('T')[0] if sentencia.get('fec_sentencia_d') else None,
                'corte': sentencia.get('gls_corte_s'),
                'sala': sentencia.get('gls_sala_sup_s'),
                'resultado_recurso': sentencia.get('resultado_recurso_sup_s'),
                'texto_completo': sentencia.get('des_contenido_s'),
                
                # Campos adicionales disponibles
                'url_acceso': f"https://juris.pjud.cl/sentencia/{sentencia.get('id')}" if sentencia.get('id') else None,
                'condicion_publicacion': sentencia.get('gls_condicion_publicacion_s'),
                
                # Arrays si están disponibles
                'ministros': sentencia.get('id_ministro_ss', []) if isinstance(sentencia.get('id_ministro_ss'), list) else [],
                'materias': sentencia.get('gls_materia_ss', []) if isinstance(sentencia.get('gls_materia_ss'), list) else [],
                'normas': sentencia.get('gls_norma_ss', []) if isinstance(sentencia.get('gls_norma_ss'), list) else [],
                
                # Metadata
                'fecha_actualizacion': datetime.now().date().isoformat()
            }
            
            todas_sentencias.append(sentencia_supabase)
    
    # Guardar archivo para Supabase
    output_file = input_path / "sentencias_para_supabase.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(todas_sentencias, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Preparación completada")
    print(f"📊 Total de sentencias preparadas: {len(todas_sentencias)}")
    print(f"💾 Archivo generado: {output_file}")
    
    return True

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python preparar_para_supabase.py DIRECTORIO_INPUT")
        print("Ejemplo: python preparar_para_supabase.py output/descarga_api")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    
    print("🔄 PREPARANDO SENTENCIAS PARA SUPABASE")
    print("=" * 60)
    
    exito = preparar_sentencias_para_supabase(input_dir)
    
    if not exito:
        sys.exit(1)

if __name__ == "__main__":
    main()

