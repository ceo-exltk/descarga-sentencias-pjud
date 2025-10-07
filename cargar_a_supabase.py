#!/usr/bin/env python3
"""
Cargar sentencias a Supabase
Script para subir sentencias preparadas a la base de datos Supabase
"""

import sys
import json
import os
from pathlib import Path
from supabase import create_client, Client

def cargar_sentencias_a_supabase(archivo_sentencias, supabase_url, supabase_key):
    """Cargar sentencias a Supabase"""
    
    # Validar archivo
    archivo_path = Path(archivo_sentencias)
    if not archivo_path.exists():
        print(f"❌ Error: Archivo {archivo_sentencias} no existe")
        return False
    
    # Cargar sentencias
    print(f"📖 Cargando sentencias desde {archivo_sentencias}...")
    with open(archivo_path, 'r', encoding='utf-8') as f:
        sentencias = json.load(f)
    
    print(f"📊 Total de sentencias a cargar: {len(sentencias)}")
    
    if len(sentencias) == 0:
        print("⚠️ No hay sentencias para cargar")
        return True
    
    # Crear cliente Supabase
    print(f"🔌 Conectando a Supabase...")
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"❌ Error conectando a Supabase: {e}")
        return False
    
    # Cargar sentencias en lotes
    batch_size = 100
    total_cargadas = 0
    total_errores = 0
    
    print(f"📤 Cargando sentencias en lotes de {batch_size}...")
    
    for i in range(0, len(sentencias), batch_size):
        batch = sentencias[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        try:
            # Insertar o actualizar (upsert)
            response = supabase.table('sentencias').upsert(
                batch,
                on_conflict='id_sentencia'
            ).execute()
            
            total_cargadas += len(batch)
            print(f"   ✅ Lote {batch_num}: {len(batch)} sentencias cargadas ({total_cargadas}/{len(sentencias)})")
            
        except Exception as e:
            total_errores += len(batch)
            print(f"   ❌ Lote {batch_num}: Error - {e}")
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE CARGA")
    print(f"   Total procesadas: {len(sentencias)}")
    print(f"   ✅ Cargadas exitosamente: {total_cargadas}")
    print(f"   ❌ Con errores: {total_errores}")
    
    if total_errores > 0:
        print(f"\n⚠️ Se encontraron {total_errores} errores durante la carga")
        return False
    else:
        print("\n🎉 Carga completada exitosamente")
        return True

def main():
    """Función principal"""
    if len(sys.argv) < 4:
        print("Uso: python cargar_a_supabase.py ARCHIVO_SENTENCIAS SUPABASE_URL SUPABASE_KEY")
        print("Ejemplo: python cargar_a_supabase.py output/descarga_api/sentencias_para_supabase.json https://xxx.supabase.co xxxkey")
        sys.exit(1)
    
    archivo_sentencias = sys.argv[1]
    supabase_url = sys.argv[2]
    supabase_key = sys.argv[3]
    
    print("🚀 CARGA DE SENTENCIAS A SUPABASE")
    print("=" * 60)
    
    exito = cargar_sentencias_a_supabase(archivo_sentencias, supabase_url, supabase_key)
    
    if not exito:
        sys.exit(1)

if __name__ == "__main__":
    main()

