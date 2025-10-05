#!/usr/bin/env python3
"""
Script para configurar automáticamente Supabase usando endpoints
"""

import json
import os
import sys
import requests
from datetime import datetime

class SupabaseAutoSetup:
    def __init__(self, supabase_url, supabase_key):
        self.supabase_url = supabase_url.rstrip('/')
        self.supabase_key = supabase_key
        
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
    
    def create_table_via_sql(self):
        """Crea la tabla usando el endpoint SQL de Supabase"""
        print("🔧 Creando tabla 'sentencias'...")
        
        sql_commands = [
            """
            CREATE TABLE IF NOT EXISTS sentencias (
                id SERIAL PRIMARY KEY,
                tribunal_origen TEXT,
                fecha_sentencia DATE,
                numero_rol TEXT,
                materia TEXT,
                texto_sentencia TEXT,
                fecha_descarga TIMESTAMP DEFAULT NOW(),
                batch_id INTEGER,
                archivo_origen TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_sentencias_tribunal 
            ON sentencias(tribunal_origen);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_sentencias_fecha 
            ON sentencias(fecha_sentencia);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_sentencias_rol 
            ON sentencias(numero_rol);
            """
        ]
        
        for i, sql in enumerate(sql_commands, 1):
            try:
                # Usar el endpoint de SQL de Supabase
                url = f"{self.supabase_url}/rest/v1/rpc/exec_sql"
                data = {"sql": sql.strip()}
                
                response = requests.post(url, headers=self.headers, json=data)
                
                if response.status_code in [200, 201]:
                    print(f"✅ Comando SQL {i} ejecutado exitosamente")
                else:
                    print(f"⚠️  Comando SQL {i}: {response.status_code}")
                    print(f"   Respuesta: {response.text}")
                    
            except Exception as e:
                print(f"⚠️  Error en comando SQL {i}: {e}")
        
        return True
    
    def test_table_creation(self):
        """Prueba que la tabla se creó correctamente"""
        try:
            url = f"{self.supabase_url}/rest/v1/sentencias?select=count"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                print("✅ Tabla 'sentencias' creada y accesible")
                return True
            else:
                print(f"❌ Error accediendo a tabla: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error verificando tabla: {e}")
            return False
    
    def insert_test_data(self):
        """Inserta datos de prueba"""
        print("🧪 Insertando datos de prueba...")
        
        test_data = {
            "tribunal_origen": "Corte_Suprema",
            "fecha_sentencia": "2024-01-16",
            "numero_rol": "TEST-SETUP-001",
            "materia": "Configuración automática",
            "texto_sentencia": "Datos de prueba para verificar la configuración automática de Supabase.",
            "fecha_descarga": datetime.now().isoformat(),
            "batch_id": 999,
            "archivo_origen": "setup_automatico.json"
        }
        
        try:
            url = f"{self.supabase_url}/rest/v1/sentencias"
            response = requests.post(url, headers=self.headers, json=test_data)
            
            if response.status_code in [200, 201]:
                print("✅ Datos de prueba insertados exitosamente")
                return True
            else:
                print(f"❌ Error insertando datos: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error en inserción: {e}")
            return False
    
    def verify_data(self):
        """Verifica que los datos se insertaron correctamente"""
        try:
            url = f"{self.supabase_url}/rest/v1/sentencias?numero_rol=eq.TEST-SETUP-001"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    print(f"✅ Datos verificados: {len(data)} registro(s) encontrado(s)")
                    return True
                else:
                    print("❌ No se encontraron los datos de prueba")
                    return False
            else:
                print(f"❌ Error verificando datos: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error en verificación: {e}")
            return False
    
    def cleanup_test_data(self):
        """Limpia los datos de prueba"""
        print("🧹 Limpiando datos de prueba...")
        
        try:
            url = f"{self.supabase_url}/rest/v1/sentencias?numero_rol=eq.TEST-SETUP-001"
            response = requests.delete(url, headers=self.headers)
            
            if response.status_code in [200, 204]:
                print("✅ Datos de prueba eliminados")
                return True
            else:
                print(f"⚠️  No se pudieron eliminar datos de prueba: {response.status_code}")
                return False
        except Exception as e:
            print(f"⚠️  Error limpiando datos: {e}")
            return False
    
    def show_github_config(self):
        """Muestra la configuración para GitHub"""
        print("\n🔧 CONFIGURACIÓN PARA GITHUB SECRETS")
        print("=" * 50)
        print("Configura estos secrets en tu repositorio:")
        print()
        print("1. Ve a tu repositorio en GitHub")
        print("2. Settings → Secrets and variables → Actions")
        print("3. Click 'New repository secret'")
        print()
        print("Secrets requeridos:")
        print(f"   SUPABASE_URL: {self.supabase_url}")
        print(f"   SUPABASE_ANON_KEY: {self.supabase_key[:20]}...")
        print()
        print("✅ Una vez configurados, el workflow cargará automáticamente")
    
    def run_complete_setup(self):
        """Ejecuta la configuración completa"""
        print("🚀 CONFIGURACIÓN AUTOMÁTICA DE SUPABASE")
        print("=" * 50)
        
        # 1. Probar conexión
        if not self.test_connection():
            return False
        
        # 2. Crear tabla
        self.create_table_via_sql()
        
        # 3. Verificar tabla
        if not self.test_table_creation():
            return False
        
        # 4. Insertar datos de prueba
        if not self.insert_test_data():
            return False
        
        # 5. Verificar datos
        if not self.verify_data():
            return False
        
        # 6. Limpiar datos de prueba
        self.cleanup_test_data()
        
        # 7. Mostrar configuración de GitHub
        self.show_github_config()
        
        print("\n✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
        print("   Supabase está listo para recibir datos")
        print("   Configura los GitHub Secrets para activar la carga automática")
        
        return True

def main():
    if len(sys.argv) < 3:
        print("Uso: python3 setup_supabase_automatico.py <supabase_url> <supabase_key>")
        print("Ejemplo: python3 setup_supabase_automatico.py https://xxx.supabase.co eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        return False
    
    supabase_url = sys.argv[1]
    supabase_key = sys.argv[2]
    
    setup = SupabaseAutoSetup(supabase_url, supabase_key)
    return setup.run_complete_setup()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
