#!/usr/bin/env python3
"""
Verificador Optimizado de Supabase
Script optimizado para consultas eficientes en tablas grandes
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

class VerificadorSupabaseOptimizado:
    """Verificador optimizado para Supabase con tablas grandes"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL', 'https://wluachczgiyrmrhdpcue.supabase.co')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_key:
            print("❌ Error: SUPABASE_ANON_KEY no configurado")
            sys.exit(1)
        
        # Configurar sesión HTTP con timeouts optimizados
        self.session = requests.Session()
        self.session.headers.update({
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Timeout más largo para tablas grandes
        self.session.timeout = 60
        
        self.resultados = {
            'conexion_basica': False,
            'acceso_tabla_sentencias': False,
            'queries_optimizadas': False,
            'estructura_tabla': {},
            'estadisticas_optimizadas': {},
            'errores': []
        }
    
    def verificar_conexion_basica(self):
        """Verificar conexión básica a Supabase"""
        print("🔍 Verificando conexión básica...")
        
        try:
            health_url = f"{self.supabase_url}/rest/v1/"
            response = self.session.get(health_url, timeout=30)
            
            if response.status_code == 200:
                print("✅ Conexión básica exitosa")
                self.resultados['conexion_basica'] = True
                return True
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def verificar_estructura_tabla_optimizada(self):
        """Verificar estructura de tabla con consulta optimizada"""
        print("🔍 Verificando estructura de tabla (optimizada)...")
        
        try:
            # Consulta muy simple para obtener estructura
            sentencias_url = f"{self.supabase_url}/rest/v1/sentencias"
            params = {
                'select': 'id,rol_numero,caratulado,fecha_sentencia,texto_completo',
                'limit': '1'
            }
            
            response = self.session.get(sentencias_url, params=params, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    registro = data[0]
                    campos = list(registro.keys())
                    print(f"✅ Estructura obtenida - {len(campos)} campos principales")
                    print(f"   Campos clave: {', '.join(campos)}")
                    
                    self.resultados['estructura_tabla'] = {
                        'campos_principales': campos,
                        'total_campos': len(campos)
                    }
                    return True
                else:
                    print("⚠️ Tabla vacía")
                    return False
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def verificar_count_optimizado(self):
        """Verificar count con consulta optimizada"""
        print("🔍 Verificando count de registros (optimizado)...")
        
        try:
            # Usar count optimizado
            sentencias_url = f"{self.supabase_url}/rest/v1/sentencias"
            params = {
                'select': 'count',
                'limit': '1'
            }
            
            response = self.session.get(sentencias_url, params=params, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                count = data[0]['count'] if data else 0
                print(f"✅ Count obtenido: {count:,} registros")
                self.resultados['estadisticas_optimizadas']['total_registros'] = count
                return True
            else:
                print(f"❌ Error en count: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error en count: {e}")
            return False
    
    def verificar_queries_simples(self):
        """Verificar queries simples y eficientes"""
        print("🔍 Verificando queries simples...")
        
        queries_simples = [
            {
                'nombre': 'Últimos registros',
                'query': {'select': 'id,rol_numero,created_at', 'order': 'created_at.desc', 'limit': '5'}
            },
            {
                'nombre': 'Filtro por ROL no nulo',
                'query': {'select': 'id,rol_numero', 'rol_numero': 'not.is.null', 'limit': '5'}
            },
            {
                'nombre': 'Filtro por fecha reciente',
                'query': {'select': 'id,fecha_sentencia', 'fecha_sentencia': 'gte.2024-01-01', 'limit': '5'}
            }
        ]
        
        queries_exitosas = 0
        
        for test in queries_simples:
            try:
                sentencias_url = f"{self.supabase_url}/rest/v1/sentencias"
                response = self.session.get(sentencias_url, params=test['query'], timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {test['nombre']}: {len(data)} registros")
                    queries_exitosas += 1
                else:
                    print(f"❌ {test['nombre']}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {test['nombre']}: {e}")
        
        if queries_exitosas > 0:
            print(f"✅ {queries_exitosas}/{len(queries_simples)} queries exitosas")
            self.resultados['queries_optimizadas'] = True
            return True
        else:
            print("❌ Ninguna query exitosa")
            return False
    
    def verificar_insercion_test(self):
        """Verificar capacidad de inserción con datos de prueba"""
        print("🔍 Verificando capacidad de inserción...")
        
        try:
            # Datos de prueba para inserción
            test_data = {
                'rol_numero': f'TEST-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'caratulado': 'Prueba de conexión',
                'fecha_sentencia': '2024-01-01',
                'texto_completo': 'Texto de prueba para verificar inserción'
            }
            
            sentencias_url = f"{self.supabase_url}/rest/v1/sentencias"
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            }
            
            # Hacer inserción de prueba
            response = self.session.post(sentencias_url, json=[test_data], headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                print("✅ Inserción de prueba exitosa")
                return True
            else:
                print(f"❌ Error en inserción: HTTP {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error en inserción: {e}")
            return False
    
    def verificar_estadisticas_por_tribunal(self):
        """Verificar estadísticas por tribunal con consulta optimizada"""
        print("🔍 Obteniendo estadísticas por tribunal...")
        
        try:
            # Consulta optimizada para estadísticas
            sentencias_url = f"{self.supabase_url}/rest/v1/sentencias"
            params = {
                'select': 'corte,count',
                'group_by': 'corte',
                'limit': '10'
            }
            
            response = self.session.get(sentencias_url, params=params, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Estadísticas por tribunal obtenidas:")
                
                for item in data:
                    tribunal = item.get('corte', 'N/A')
                    count = item.get('count', 0)
                    print(f"   {tribunal}: {count:,} sentencias")
                
                self.resultados['estadisticas_optimizadas']['por_tribunal'] = data
                return True
            else:
                print(f"❌ Error en estadísticas: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error en estadísticas: {e}")
            return False
    
    def ejecutar_verificacion_optimizada(self):
        """Ejecutar verificación optimizada completa"""
        print("🚀 VERIFICACIÓN OPTIMIZADA DE SUPABASE")
        print("=" * 60)
        print(f"🌐 URL: {self.supabase_url}")
        print(f"🔑 Key: {'Configurado' if self.supabase_key else 'No configurado'}")
        print("=" * 60)
        
        # Ejecutar verificaciones optimizadas
        test1 = self.verificar_conexion_basica()
        test2 = self.verificar_estructura_tabla_optimizada()
        test3 = self.verificar_count_optimizado()
        test4 = self.verificar_queries_simples()
        test5 = self.verificar_insercion_test()
        test6 = self.verificar_estadisticas_por_tribunal()
        
        # Mostrar resultados finales
        self.mostrar_resultados_finales()
        
        return self.resultados
    
    def mostrar_resultados_finales(self):
        """Mostrar resultados finales"""
        print("\n" + "=" * 60)
        print("📊 RESULTADOS FINALES - VERIFICACIÓN OPTIMIZADA")
        print("=" * 60)
        
        # Estado de verificaciones
        print("🔍 ESTADO DE LAS VERIFICACIONES:")
        print(f"   Conexión básica: {'✅ EXITOSA' if self.resultados['conexion_basica'] else '❌ FALLÓ'}")
        print(f"   Estructura tabla: {'✅ EXITOSA' if self.resultados['estructura_tabla'] else '❌ FALLÓ'}")
        print(f"   Queries optimizadas: {'✅ EXITOSA' if self.resultados['queries_optimizadas'] else '❌ FALLÓ'}")
        
        # Estadísticas
        if self.resultados['estadisticas_optimizadas']:
            print("\n📈 ESTADÍSTICAS OBTENIDAS:")
            total = self.resultados['estadisticas_optimizadas'].get('total_registros', 0)
            print(f"   Total de registros: {total:,}")
            
            if 'por_tribunal' in self.resultados['estadisticas_optimizadas']:
                print("   Por tribunal:")
                for item in self.resultados['estadisticas_optimizadas']['por_tribunal']:
                    tribunal = item.get('corte', 'N/A')
                    count = item.get('count', 0)
                    print(f"     {tribunal}: {count:,}")
        
        # Estructura
        if self.resultados['estructura_tabla']:
            print("\n🏗️ ESTRUCTURA DE LA TABLA:")
            campos = self.resultados['estructura_tabla'].get('campos_principales', [])
            print(f"   Campos principales: {', '.join(campos)}")
        
        # Diagnóstico final
        print("\n🔍 DIAGNÓSTICO FINAL:")
        if (self.resultados['conexion_basica'] and 
            self.resultados['estructura_tabla'] and 
            self.resultados['queries_optimizadas']):
            print("🎉 CONEXIÓN A SUPABASE FUNCIONAL")
            print("✅ Queries optimizadas funcionando")
            print("✅ Sistema listo para descarga masiva")
            print("💡 Recomendación: Usar consultas optimizadas para mejor rendimiento")
        else:
            print("❌ PROBLEMAS PERSISTENTES")
            if self.resultados['errores']:
                print("🔍 Errores encontrados:")
                for i, error in enumerate(self.resultados['errores'], 1):
                    print(f"   {i}. {error}")
        
        print("=" * 60)

def main():
    """Función principal"""
    print("🔍 VERIFICADOR OPTIMIZADO DE SUPABASE")
    print("=" * 50)
    print("Verificación optimizada para tablas grandes...")
    print("=" * 50)
    
    # Crear verificador optimizado
    verificador = VerificadorSupabaseOptimizado()
    
    # Ejecutar verificación optimizada
    resultados = verificador.ejecutar_verificacion_optimizada()
    
    # Guardar resultados
    resultados_file = Path("logs/verificacion_supabase_optimizada.json")
    resultados_file.parent.mkdir(exist_ok=True)
    
    with open(resultados_file, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    print(f"📁 Resultados guardados en: {resultados_file}")
    
    # Código de salida
    if (resultados['conexion_basica'] and 
        resultados['estructura_tabla'] and 
        resultados['queries_optimizadas']):
        print("🎉 VERIFICACIÓN OPTIMIZADA EXITOSA")
        sys.exit(0)  # Éxito
    else:
        print("❌ VERIFICACIÓN OPTIMIZADA FALLÓ")
        sys.exit(1)  # Error

if __name__ == "__main__":
    main()
