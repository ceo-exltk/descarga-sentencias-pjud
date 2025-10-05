#!/usr/bin/env python3
"""
Script para cargar datos directamente a Supabase
"""

import json
import os
import sys
import requests
from datetime import datetime
from pathlib import Path

class SupabaseLoader:
    def __init__(self, supabase_url, supabase_key):
        self.supabase_url = supabase_url.rstrip('/')
        self.supabase_key = supabase_key
        self.headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
    
    def test_connection(self):
        """Prueba la conexión a Supabase"""
        try:
            url = f"{self.supabase_url}/rest/v1/"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                print("✅ Conexión a Supabase exitosa")
                return True
            else:
                print(f"❌ Error de conexión: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error conectando a Supabase: {e}")
            return False
    
    def insert_sentencias(self, sentencias_data):
        """Inserta sentencias en la tabla de Supabase"""
        try:
            url = f"{self.supabase_url}/rest/v1/sentencias"
            
            # Si es una lista de sentencias, insertar en lotes
            if isinstance(sentencias_data, list):
                return self._insert_batch(sentencias_data)
            else:
                # Insertar una sola sentencia
                response = requests.post(url, headers=self.headers, json=sentencias_data)
                return self._handle_response(response)
                
        except Exception as e:
            print(f"❌ Error insertando sentencias: {e}")
            return False
    
    def _insert_batch(self, sentencias, batch_size=100):
        """Inserta sentencias en lotes para mejor rendimiento"""
        total_inserted = 0
        
        for i in range(0, len(sentencias), batch_size):
            batch = sentencias[i:i + batch_size]
            
            try:
                url = f"{self.supabase_url}/rest/v1/sentencias"
                response = requests.post(url, headers=self.headers, json=batch)
                
                if response.status_code in [200, 201]:
                    total_inserted += len(batch)
                    print(f"✅ Lote {i//batch_size + 1}: {len(batch)} sentencias insertadas")
                else:
                    print(f"❌ Error en lote {i//batch_size + 1}: {response.status_code}")
                    print(f"   Respuesta: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error en lote {i//batch_size + 1}: {e}")
        
        print(f"📊 Total insertadas: {total_inserted}/{len(sentencias)}")
        return total_inserted > 0
    
    def _handle_response(self, response):
        """Maneja la respuesta de Supabase"""
        if response.status_code in [200, 201]:
            print("✅ Datos insertados exitosamente")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
    
    def get_table_info(self, table_name="sentencias"):
        """Obtiene información de la tabla"""
        try:
            url = f"{self.supabase_url}/rest/v1/{table_name}?select=count"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Tabla {table_name}: {len(data)} registros")
                return True
            else:
                print(f"❌ Error obteniendo info de tabla: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error consultando tabla: {e}")
            return False

def cargar_desde_archivo(archivo_json, supabase_url, supabase_key):
    """Carga datos desde un archivo JSON a Supabase"""
    
    print(f"🔄 Cargando datos desde: {archivo_json}")
    
    # Verificar que el archivo existe
    if not os.path.exists(archivo_json):
        print(f"❌ Archivo no encontrado: {archivo_json}")
        return False
    
    # Cargar datos
    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return False
    
    # Inicializar Supabase
    loader = SupabaseLoader(supabase_url, supabase_key)
    
    # Probar conexión
    if not loader.test_connection():
        return False
    
    # Determinar el tipo de datos
    if isinstance(data, list):
        # Lista directa de sentencias
        sentencias = data
    elif isinstance(data, dict) and 'sentencias' in data:
        # Archivo con metadatos
        sentencias = data['sentencias']
    else:
        print("❌ Formato de archivo no reconocido")
        return False
    
    print(f"📄 Encontradas {len(sentencias)} sentencias para insertar")
    
    # Insertar datos
    success = loader.insert_sentencias(sentencias)
    
    if success:
        print("✅ Carga completada exitosamente")
        # Mostrar estadísticas de la tabla
        loader.get_table_info()
    
    return success

def main():
    if len(sys.argv) < 4:
        print("Uso: python3 cargar_a_supabase.py <archivo_json> <supabase_url> <supabase_key>")
        print("Ejemplo: python3 cargar_a_supabase.py sentencias.json https://xxx.supabase.co supabase_key")
        return False
    
    archivo_json = sys.argv[1]
    supabase_url = sys.argv[2]
    supabase_key = sys.argv[3]
    
    print("🚀 CARGANDO DATOS A SUPABASE")
    print("=" * 50)
    
    return cargar_desde_archivo(archivo_json, supabase_url, supabase_key)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
