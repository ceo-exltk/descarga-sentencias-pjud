#!/usr/bin/env python3
"""
Script para probar la carga de datos reales a Supabase
"""

import json
import os
import sys
import requests
from datetime import datetime
from pathlib import Path

class SupabaseTester:
    def __init__(self, supabase_url=None, supabase_key=None):
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            print("❌ Variables de Supabase no configuradas")
            print("   Configura SUPABASE_URL y SUPABASE_ANON_KEY")
            sys.exit(1)
        
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
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
    
    def load_test_data(self, archivo_json):
        """Carga datos de prueba desde un archivo JSON"""
        print(f"📄 Cargando datos desde: {archivo_json}")
        
        if not os.path.exists(archivo_json):
            print(f"❌ Archivo no encontrado: {archivo_json}")
            return False
        
        try:
            with open(archivo_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Error leyendo archivo: {e}")
            return False
        
        # Determinar el tipo de datos
        if isinstance(data, list):
            sentencias = data
        elif isinstance(data, dict) and 'sentencias' in data:
            sentencias = data['sentencias']
        else:
            print("❌ Formato de archivo no reconocido")
            return False
        
        print(f"📊 Encontradas {len(sentencias)} sentencias para cargar")
        
        # Cargar en lotes
        return self._insert_batch(sentencias)
    
    def _insert_batch(self, sentencias, batch_size=10):
        """Inserta sentencias en lotes"""
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
    
    def get_table_stats(self):
        """Obtiene estadísticas de la tabla"""
        try:
            # Contar total de registros
            url = f"{self.supabase_url}/rest/v1/sentencias?select=count"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                total = len(response.json())
                print(f"📊 Total de registros en tabla: {total}")
            
            # Contar por tribunal
            url = f"{self.supabase_url}/rest/v1/sentencias?select=tribunal_origen"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                tribunales = {}
                for record in response.json():
                    tribunal = record.get('tribunal_origen', 'Desconocido')
                    tribunales[tribunal] = tribunales.get(tribunal, 0) + 1
                
                print("📊 Registros por tribunal:")
                for tribunal, count in tribunales.items():
                    print(f"   {tribunal}: {count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return False
    
    def test_workflow_integration(self):
        """Prueba la integración completa del workflow"""
        print("🔄 PROBANDO INTEGRACIÓN COMPLETA")
        print("=" * 50)
        
        # 1. Probar conexión
        if not self.test_connection():
            return False
        
        # 2. Buscar archivos de datos
        archivos_datos = [
            "output/descarga_api/sentencias_para_supabase.json",
            "output/descarga_api/sentencias_consolidadas.json"
        ]
        
        archivo_encontrado = None
        for archivo in archivos_datos:
            if os.path.exists(archivo):
                archivo_encontrado = archivo
                break
        
        if not archivo_encontrado:
            print("❌ No se encontraron archivos de datos")
            print("   Ejecuta primero el workflow de descarga")
            return False
        
        # 3. Cargar datos
        if not self.load_test_data(archivo_encontrado):
            return False
        
        # 4. Mostrar estadísticas
        self.get_table_stats()
        
        print("\n✅ INTEGRACIÓN COMPLETADA EXITOSAMENTE")
        print("   Los datos se cargaron correctamente a Supabase")
        print("   El workflow está listo para carga automática")
        
        return True

def main():
    if len(sys.argv) >= 3:
        supabase_url = sys.argv[1]
        supabase_key = sys.argv[2]
        tester = SupabaseTester(supabase_url, supabase_key)
    else:
        tester = SupabaseTester()
    
    return tester.test_workflow_integration()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
