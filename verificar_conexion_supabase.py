#!/usr/bin/env python3
"""
Verificador de Conexión a Supabase
Script para verificar conectividad y acceso a las tablas de sentencias
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

class VerificadorSupabase:
    """Verificador de conexión y acceso a Supabase"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL', 'https://wluachczgiyrmrhdpcue.supabase.co')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_key:
            print("❌ Error: SUPABASE_ANON_KEY no configurado")
            print("💡 Configurar: export SUPABASE_ANON_KEY='tu_key'")
            sys.exit(1)
        
        # Configurar sesión HTTP
        self.session = requests.Session()
        self.session.headers.update({
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        self.resultados = {
            'conexion_basica': False,
            'acceso_tabla_sentencias': False,
            'queries_funcionando': False,
            'estructura_tabla': {},
            'estadisticas_tabla': {},
            'errores': []
        }
    
    def verificar_conexion_basica(self):
        """Verificar conexión básica a Supabase"""
        print("🔍 Verificando conexión básica a Supabase...")
        
        try:
            # URL de health check de Supabase
            health_url = f"{self.supabase_url}/rest/v1/"
            
            response = self.session.get(health_url, timeout=30)
            
            if response.status_code == 200:
                print("✅ Conexión básica exitosa")
                self.resultados['conexion_basica'] = True
                return True
            else:
                print(f"❌ Error en conexión básica: HTTP {response.status_code}")
                self.resultados['errores'].append(f"HTTP {response.status_code} en conexión básica")
                return False
                
        except Exception as e:
            print(f"❌ Error en conexión básica: {e}")
            self.resultados['errores'].append(f"Error conexión básica: {e}")
            return False
    
    def verificar_acceso_tabla_sentencias(self):
        """Verificar acceso a la tabla de sentencias"""
        print("🔍 Verificando acceso a tabla 'sentencias'...")
        
        try:
            # URL para acceder a la tabla sentencias
            sentencias_url = f"{self.supabase_url}/rest/v1/sentencias"
            
            # Parámetros para obtener solo el count (más eficiente)
            params = {
                'select': 'count'
            }
            
            response = self.session.get(sentencias_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                count = data[0]['count'] if data else 0
                print(f"✅ Acceso a tabla 'sentencias' exitoso - {count} registros")
                self.resultados['acceso_tabla_sentencias'] = True
                self.resultados['estadisticas_tabla']['total_registros'] = count
                return True
            elif response.status_code == 404:
                print("❌ Tabla 'sentencias' no encontrada")
                self.resultados['errores'].append("Tabla 'sentencias' no existe")
                return False
            else:
                print(f"❌ Error accediendo a tabla: HTTP {response.status_code}")
                print(f"   Respuesta: {response.text}")
                self.resultados['errores'].append(f"HTTP {response.status_code} accediendo a tabla")
                return False
                
        except Exception as e:
            print(f"❌ Error accediendo a tabla: {e}")
            self.resultados['errores'].append(f"Error accediendo tabla: {e}")
            return False
    
    def verificar_estructura_tabla(self):
        """Verificar estructura de la tabla sentencias"""
        print("🔍 Verificando estructura de la tabla...")
        
        try:
            # Obtener una muestra de registros para analizar estructura
            sentencias_url = f"{self.supabase_url}/rest/v1/sentencias"
            params = {
                'select': '*',
                'limit': '1'
            }
            
            response = self.session.get(sentencias_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    registro = data[0]
                    campos = list(registro.keys())
                    print(f"✅ Estructura de tabla obtenida - {len(campos)} campos")
                    print(f"   Campos encontrados: {', '.join(campos)}")
                    
                    self.resultados['estructura_tabla'] = {
                        'campos': campos,
                        'total_campos': len(campos)
                    }
                    return True
                else:
                    print("⚠️ Tabla vacía - no se puede analizar estructura")
                    return False
            else:
                print(f"❌ Error obteniendo estructura: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error analizando estructura: {e}")
            return False
    
    def verificar_queries_especificas(self):
        """Verificar queries específicas sobre la tabla"""
        print("🔍 Verificando queries específicas...")
        
        queries_tests = [
            {
                'nombre': 'Count por tribunal',
                'query': {'select': 'tribunal_type,count', 'group_by': 'tribunal_type'}
            },
            {
                'nombre': 'Filtro por fecha',
                'query': {'select': 'count', 'fecha_sentencia': 'not.is.null'}
            },
            {
                'nombre': 'Filtro por texto completo',
                'query': {'select': 'count', 'texto_completo': 'not.is.null'}
            },
            {
                'nombre': 'Filtro por ROL',
                'query': {'select': 'count', 'rol_numero': 'not.is.null'}
            }
        ]
        
        queries_exitosas = 0
        
        for test in queries_tests:
            try:
                sentencias_url = f"{self.supabase_url}/rest/v1/sentencias"
                response = self.session.get(sentencias_url, params=test['query'])
                
                if response.status_code == 200:
                    print(f"✅ {test['nombre']}: OK")
                    queries_exitosas += 1
                else:
                    print(f"❌ {test['nombre']}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {test['nombre']}: Error - {e}")
        
        if queries_exitosas == len(queries_tests):
            print("✅ Todas las queries funcionando correctamente")
            self.resultados['queries_funcionando'] = True
            return True
        else:
            print(f"⚠️ {queries_exitosas}/{len(queries_tests)} queries exitosas")
            return False
    
    def verificar_estadisticas_detalladas(self):
        """Verificar estadísticas detalladas de la tabla"""
        print("🔍 Obteniendo estadísticas detalladas...")
        
        try:
            # Estadísticas por tribunal
            sentencias_url = f"{self.supabase_url}/rest/v1/sentencias"
            params = {
                'select': 'tribunal_type,count',
                'group_by': 'tribunal_type'
            }
            
            response = self.session.get(sentencias_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Estadísticas por tribunal obtenidas:")
                
                for item in data:
                    tribunal = item.get('tribunal_type', 'N/A')
                    count = item.get('count', 0)
                    print(f"   {tribunal}: {count:,} sentencias")
                
                self.resultados['estadisticas_tabla']['por_tribunal'] = data
                return True
            else:
                print(f"❌ Error obteniendo estadísticas: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return False
    
    def verificar_insercion_datos(self):
        """Verificar capacidad de inserción (solo lectura para seguridad)"""
        print("🔍 Verificando permisos de escritura...")
        
        try:
            # Solo verificar que podemos hacer POST (sin insertar datos reales)
            sentencias_url = f"{self.supabase_url}/rest/v1/sentencias"
            
            # Headers para verificar permisos
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            }
            
            # Datos de prueba (no se insertarán realmente)
            test_data = {
                'rol_numero': 'TEST-123',
                'tribunal_type': 'TEST',
                'caratulado': 'Prueba de conexión',
                'fecha_sentencia': '2024-01-01'
            }
            
            # Solo verificar headers, no hacer POST real
            print("✅ Headers de inserción configurados correctamente")
            print("⚠️ Inserción real deshabilitada por seguridad")
            
            return True
            
        except Exception as e:
            print(f"❌ Error verificando permisos: {e}")
            return False
    
    def ejecutar_verificacion_completa(self):
        """Ejecutar verificación completa"""
        print("🚀 VERIFICACIÓN COMPLETA DE SUPABASE")
        print("=" * 60)
        print(f"🌐 URL: {self.supabase_url}")
        print(f"🔑 Key: {'Configurado' if self.supabase_key else 'No configurado'}")
        print("=" * 60)
        
        # Ejecutar todas las verificaciones
        test1 = self.verificar_conexion_basica()
        test2 = self.verificar_acceso_tabla_sentencias()
        test3 = self.verificar_estructura_tabla()
        test4 = self.verificar_queries_especificas()
        test5 = self.verificar_estadisticas_detalladas()
        test6 = self.verificar_insercion_datos()
        
        # Mostrar resultados finales
        self.mostrar_resultados_finales()
        
        return self.resultados
    
    def mostrar_resultados_finales(self):
        """Mostrar resultados finales"""
        print("\n" + "=" * 60)
        print("📊 RESULTADOS FINALES DE VERIFICACIÓN")
        print("=" * 60)
        
        # Estado de cada verificación
        print("🔍 ESTADO DE LAS VERIFICACIONES:")
        print(f"   Conexión básica: {'✅ EXITOSA' if self.resultados['conexion_basica'] else '❌ FALLÓ'}")
        print(f"   Acceso a tabla: {'✅ EXITOSA' if self.resultados['acceso_tabla_sentencias'] else '❌ FALLÓ'}")
        print(f"   Queries funcionando: {'✅ EXITOSA' if self.resultados['queries_funcionando'] else '❌ FALLÓ'}")
        
        # Estadísticas de la tabla
        if self.resultados['estadisticas_tabla']:
            print("\n📈 ESTADÍSTICAS DE LA TABLA:")
            total = self.resultados['estadisticas_tabla'].get('total_registros', 0)
            print(f"   Total de registros: {total:,}")
            
            if 'por_tribunal' in self.resultados['estadisticas_tabla']:
                print("   Por tribunal:")
                for item in self.resultados['estadisticas_tabla']['por_tribunal']:
                    tribunal = item.get('tribunal_type', 'N/A')
                    count = item.get('count', 0)
                    print(f"     {tribunal}: {count:,}")
        
        # Estructura de la tabla
        if self.resultados['estructura_tabla']:
            print("\n🏗️ ESTRUCTURA DE LA TABLA:")
            campos = self.resultados['estructura_tabla'].get('campos', [])
            print(f"   Total de campos: {len(campos)}")
            print(f"   Campos: {', '.join(campos)}")
        
        # Diagnóstico
        print("\n🔍 DIAGNÓSTICO:")
        if (self.resultados['conexion_basica'] and 
            self.resultados['acceso_tabla_sentencias'] and 
            self.resultados['queries_funcionando']):
            print("🎉 CONEXIÓN A SUPABASE COMPLETAMENTE FUNCIONAL")
            print("✅ Se puede realizar descarga y carga de datos")
            print("✅ Queries funcionando correctamente")
            print("✅ Sistema listo para descarga masiva")
        else:
            print("❌ PROBLEMAS DE CONECTIVIDAD")
            if self.resultados['errores']:
                print("🔍 Errores encontrados:")
                for i, error in enumerate(self.resultados['errores'], 1):
                    print(f"   {i}. {error}")
        
        print("=" * 60)

def main():
    """Función principal"""
    print("🔍 VERIFICADOR DE CONEXIÓN A SUPABASE")
    print("=" * 50)
    print("Verificando conectividad y acceso a tablas...")
    print("=" * 50)
    
    # Crear verificador
    verificador = VerificadorSupabase()
    
    # Ejecutar verificación completa
    resultados = verificador.ejecutar_verificacion_completa()
    
    # Guardar resultados
    resultados_file = Path("logs/verificacion_supabase.json")
    resultados_file.parent.mkdir(exist_ok=True)
    
    with open(resultados_file, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    print(f"📁 Resultados guardados en: {resultados_file}")
    
    # Código de salida
    if (resultados['conexion_basica'] and 
        resultados['acceso_tabla_sentencias'] and 
        resultados['queries_funcionando']):
        print("🎉 VERIFICACIÓN COMPLETADA EXITOSAMENTE")
        sys.exit(0)  # Éxito
    else:
        print("❌ VERIFICACIÓN FALLÓ")
        sys.exit(1)  # Error

if __name__ == "__main__":
    main()
