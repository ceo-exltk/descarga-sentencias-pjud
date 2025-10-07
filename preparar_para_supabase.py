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
        
        # Las sentencias ya vienen en el formato correcto desde la API
        # Solo necesitamos mapear algunos campos para Supabase
        for sentencia in sentencias:
            sentencia_supabase = {
                # Campos principales
                'id_sentencia': sentencia.get('id'),
                'rol_era_sup_s': sentencia.get('rol_era_sup_s'),
                'rol_sup_i': sentencia.get('rol_sup_i'),
                'era_sup_i': sentencia.get('era_sup_i'),
                
                # Fechas
                'fecha_sentencia': sentencia.get('fecha_sentencia_dt_s') or sentencia.get('fecha_sentencia'),
                'fecha_ingreso': sentencia.get('fecha_ingreso_dt_s'),
                
                # Tribunal y sala
                'gls_corte_s': sentencia.get('gls_corte_s'),
                'gls_sala_sup_s': sentencia.get('gls_sala_sup_s'),
                
                # Tipo y resultado
                'gls_tipo_recurso_s': sentencia.get('gls_tipo_recurso_s'),
                'resultado_recurso_sup_s': sentencia.get('resultado_recurso_sup_s'),
                
                # Ministros y votos
                'id_ministro_ss': sentencia.get('id_ministro_ss', []),
                'id_voto_ss': sentencia.get('id_voto_ss', []),
                'gls_voto_ministro_ss': sentencia.get('gls_voto_ministro_ss', []),
                
                # Condición y flags
                'gls_condicion_publicacion_s': sentencia.get('gls_condicion_publicacion_s'),
                'flg_confidencial_i': sentencia.get('flg_confidencial_i', 0),
                'flg_reserva_i': sentencia.get('flg_reserva_i', 0),
                
                # Documento
                'sent__crr_documento_i': sentencia.get('sent__crr_documento_i'),
                
                # Materias
                'gls_materia_ss': sentencia.get('gls_materia_ss', []),
                'gls_submateria_ss': sentencia.get('gls_submateria_ss', []),
                
                # Metadata
                'corte': sentencia.get('gls_corte_s'),
                'fecha_descarga': datetime.now().isoformat()
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

