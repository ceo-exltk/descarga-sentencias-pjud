#!/usr/bin/env python3
"""
Script completo para configurar Supabase y probar la carga
"""

import json
import os
import sys
import requests
from datetime import datetime

class SupabaseConfigurator:
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
    
    def create_table(self):
        """Crea la tabla sentencias en Supabase"""
        print("🔧 Creando tabla 'sentencias' en Supabase...")
        
        # SQL para crear la tabla
        sql = """
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
        
        -- Crear índices para mejor rendimiento
        CREATE INDEX IF NOT EXISTS idx_sentencias_tribunal ON sentencias(tribunal_origen);
        CREATE INDEX IF NOT EXISTS idx_sentencias_fecha ON sentencias(fecha_sentencia);
        CREATE INDEX IF NOT EXISTS idx_sentencias_rol ON sentencias(numero_rol);
        """
        
        try:
            # Usar el endpoint de SQL de Supabase
            url = f"{self.supabase_url}/rest/v1/rpc/exec_sql"
            data = {"sql": sql}
            
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                print("✅ Tabla 'sentencias' creada exitosamente")
                return True
            else:
                print(f"❌ Error creando tabla: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error ejecutando SQL: {e}")
            return False
    
    def test_insert(self):
        """Prueba insertar datos de ejemplo"""
        print("🧪 Probando inserción de datos...")
        
        # Datos de prueba
        test_data = {
            "tribunal_origen": "Corte_Suprema",
            "fecha_sentencia": "2024-01-16",
            "numero_rol": "TEST-001",
            "materia": "Prueba de integración",
            "texto_sentencia": "Esta es una sentencia de prueba para verificar la integración con Supabase.",
            "fecha_descarga": datetime.now().isoformat(),
            "batch_id": 999,
            "archivo_origen": "test_integration.json"
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
    
    def get_table_info(self):
        """Obtiene información de la tabla"""
        try:
            url = f"{self.supabase_url}/rest/v1/sentencias?select=count"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Tabla 'sentencias': {len(data)} registros")
                return True
            else:
                print(f"❌ Error obteniendo info: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error consultando tabla: {e}")
            return False
    
    def cleanup_test_data(self):
        """Limpia los datos de prueba"""
        print("🧹 Limpiando datos de prueba...")
        
        try:
            url = f"{self.supabase_url}/rest/v1/sentencias?numero_rol=eq.TEST-001"
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
    
    def configure_github_secrets(self):
        """Muestra instrucciones para configurar GitHub Secrets"""
        print("\n🔧 CONFIGURACIÓN DE GITHUB SECRETS")
        print("=" * 50)
        print("Para habilitar la carga automática, configura estos secrets:")
        print()
        print("1. Ve a tu repositorio en GitHub")
        print("2. Settings → Secrets and variables → Actions")
        print("3. Click 'New repository secret'")
        print()
        print("Secrets requeridos:")
        print(f"   SUPABASE_URL: {self.supabase_url}")
        print(f"   SUPABASE_ANON_KEY: {self.supabase_key[:20]}...")
        print()
        print("Una vez configurados, el workflow cargará automáticamente a Supabase")
    
    def run_full_setup(self):
        """Ejecuta la configuración completa"""
        print("🚀 CONFIGURACIÓN COMPLETA DE SUPABASE")
        print("=" * 50)
        
        # 1. Probar conexión
        if not self.test_connection():
            return False
        
        # 2. Crear tabla
        if not self.create_table():
            return False
        
        # 3. Probar inserción
        if not self.test_insert():
            return False
        
        # 4. Verificar datos
        if not self.get_table_info():
            return False
        
        # 5. Limpiar datos de prueba
        self.cleanup_test_data()
        
        # 6. Mostrar instrucciones de GitHub
        self.configure_github_secrets()
        
        print("\n✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
        print("   Supabase está listo para recibir datos")
        print("   Configura los GitHub Secrets para activar la carga automática")
        
        return True

def main():
    if len(sys.argv) >= 3:
        supabase_url = sys.argv[1]
        supabase_key = sys.argv[2]
        configurator = SupabaseConfigurator(supabase_url, supabase_key)
    else:
        configurator = SupabaseConfigurator()
    
    return configurator.run_full_setup()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
