#!/usr/bin/env python3
"""
Actualizar Dashboard con Datos Reales de Supabase
Script para generar datos reales del dashboard basados en la base de datos
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

class ActualizadorDashboard:
    """Actualizador del dashboard con datos reales de Supabase"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL', 'https://wluachczgiyrmrhdpcue.supabase.co')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_key:
            print("❌ Error: SUPABASE_ANON_KEY no configurado")
            return
        
        # Configurar sesión HTTP
        self.session = requests.Session()
        self.session.headers.update({
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        self.datos_reales = {}
    
    def obtener_estadisticas_generales(self):
        """Obtener estadísticas generales de la base de datos"""
        print("🔍 Obteniendo estadísticas generales...")
        
        try:
            # Query para estadísticas generales
            query = """
            SELECT 
                COUNT(*) as total_sentencias,
                COUNT(CASE WHEN texto_completo IS NOT NULL AND LENGTH(texto_completo) > 100 THEN 1 END) as con_texto_completo,
                COUNT(CASE WHEN rol_numero IS NOT NULL AND rol_numero != '' THEN 1 END) as con_rol_numero,
                COUNT(CASE WHEN caratulado IS NOT NULL AND caratulado != '' THEN 1 END) as con_caratulado,
                COUNT(CASE WHEN fecha_sentencia IS NOT NULL THEN 1 END) as con_fecha_sentencia,
                ROUND(AVG(LENGTH(texto_completo)), 0) as promedio_longitud_texto,
                MAX(created_at) as ultima_actualizacion
            FROM sentencias
            """
            
            response = self.session.post(
                f"{self.supabase_url}/rest/v1/rpc/execute_sql",
                json={"query": query}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    stats = data[0]
                    self.datos_reales['estadisticas_generales'] = {
                        'total_sentencias': stats['total_sentencias'],
                        'con_texto_completo': stats['con_texto_completo'],
                        'con_rol_numero': stats['con_rol_numero'],
                        'con_caratulado': stats['con_caratulado'],
                        'con_fecha_sentencia': stats['con_fecha_sentencia'],
                        'promedio_longitud_texto': int(stats['promedio_longitud_texto']) if stats['promedio_longitud_texto'] else 0,
                        'ultima_actualizacion': stats['ultima_actualizacion'],
                        'fecha_actualizacion': datetime.now().isoformat()
                    }
                    print(f"✅ Estadísticas generales obtenidas: {stats['total_sentencias']} sentencias")
                    return True
            else:
                print(f"❌ Error obteniendo estadísticas: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return False
    
    def obtener_estadisticas_por_tribunal(self):
        """Obtener estadísticas detalladas por tribunal"""
        print("🔍 Obteniendo estadísticas por tribunal...")
        
        try:
            # Query para estadísticas por tribunal
            query = """
            SELECT 
                corte,
                COUNT(*) as total_sentencias,
                COUNT(CASE WHEN texto_completo IS NOT NULL AND LENGTH(texto_completo) > 100 THEN 1 END) as con_texto_completo,
                COUNT(CASE WHEN rol_numero IS NOT NULL AND rol_numero != '' THEN 1 END) as con_rol_numero,
                COUNT(CASE WHEN caratulado IS NOT NULL AND caratulado != '' THEN 1 END) as con_caratulado,
                COUNT(CASE WHEN fecha_sentencia IS NOT NULL THEN 1 END) as con_fecha_sentencia,
                ROUND(AVG(LENGTH(texto_completo)), 0) as promedio_longitud_texto,
                MAX(created_at) as ultima_actualizacion
            FROM sentencias 
            GROUP BY corte 
            ORDER BY total_sentencias DESC
            """
            
            response = self.session.post(
                f"{self.supabase_url}/rest/v1/rpc/execute_sql",
                json={"query": query}
            )
            
            if response.status_code == 200:
                data = response.json()
                tribunales = []
                
                for item in data:
                    tribunal = {
                        'nombre': item['corte'] or 'Sin especificar',
                        'total_sentencias': item['total_sentencias'],
                        'con_texto_completo': item['con_texto_completo'],
                        'con_rol_numero': item['con_rol_numero'],
                        'con_caratulado': item['con_caratulado'],
                        'con_fecha_sentencia': item['con_fecha_sentencia'],
                        'promedio_longitud_texto': int(item['promedio_longitud_texto']) if item['promedio_longitud_texto'] else 0,
                        'ultima_actualizacion': item['ultima_actualizacion'],
                        'porcentaje_texto_completo': round((item['con_texto_completo'] / item['total_sentencias']) * 100, 1) if item['total_sentencias'] > 0 else 0,
                        'porcentaje_rol_numero': round((item['con_rol_numero'] / item['total_sentencias']) * 100, 1) if item['total_sentencias'] > 0 else 0,
                        'porcentaje_caratulado': round((item['con_caratulado'] / item['total_sentencias']) * 100, 1) if item['total_sentencias'] > 0 else 0,
                        'porcentaje_fecha_sentencia': round((item['con_fecha_sentencia'] / item['total_sentencias']) * 100, 1) if item['total_sentencias'] > 0 else 0,
                        'calidad_datos': round(((item['con_texto_completo'] + item['con_rol_numero'] + item['con_caratulado']) / (item['total_sentencias'] * 3)) * 100, 1) if item['total_sentencias'] > 0 else 0,
                        'estado': 'completed',
                        'fecha_actualizacion': datetime.now().strftime('%d-%m-%Y, %I:%M:%S %p')
                    }
                    tribunales.append(tribunal)
                
                self.datos_reales['tribunales'] = tribunales
                print(f"✅ Estadísticas de {len(tribunales)} tribunales obtenidas")
                return True
            else:
                print(f"❌ Error obteniendo estadísticas por tribunal: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas por tribunal: {e}")
            return False
    
    def generar_archivos_dashboard(self):
        """Generar archivos JSON para el dashboard"""
        print("📝 Generando archivos del dashboard...")
        
        try:
            # Crear directorio data si no existe
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            # Generar stats.json
            stats_data = {
                "total_sentencias": self.datos_reales['estadisticas_generales']['total_sentencias'],
                "fecha_actualizacion": self.datos_reales['estadisticas_generales']['fecha_actualizacion'],
                "estado": "Conectado a Supabase",
                "tribunales_activos": 0,
                "velocidad_promedio": 0,
                "tasa_exito": 100.0
            }
            
            with open(data_dir / "stats.json", 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, ensure_ascii=False, indent=2)
            
            # Generar tribunals.json
            tribunals_data = []
            for tribunal in self.datos_reales['tribunales']:
                tribunal_data = {
                    "nombre": tribunal['nombre'],
                    "total_sentencias": tribunal['total_sentencias'],
                    "con_texto_completo": tribunal['con_texto_completo'],
                    "con_rol_numero": tribunal['con_rol_numero'],
                    "con_caratulado": tribunal['con_caratulado'],
                    "con_fecha_sentencia": tribunal['con_fecha_sentencia'],
                    "promedio_longitud_texto": tribunal['promedio_longitud_texto'],
                    "porcentaje_texto_completo": tribunal['porcentaje_texto_completo'],
                    "porcentaje_rol_numero": tribunal['porcentaje_rol_numero'],
                    "porcentaje_caratulado": tribunal['porcentaje_caratulado'],
                    "porcentaje_fecha_sentencia": tribunal['porcentaje_fecha_sentencia'],
                    "calidad_datos": tribunal['calidad_datos'],
                    "estado": tribunal['estado'],
                    "fecha_actualizacion": tribunal['fecha_actualizacion']
                }
                tribunals_data.append(tribunal_data)
            
            with open(data_dir / "tribunals.json", 'w', encoding='utf-8') as f:
                json.dump(tribunals_data, f, ensure_ascii=False, indent=2)
            
            # Generar activity.json
            activity_data = [
                {
                    "timestamp": datetime.now().strftime('%d-%m-%Y, %I:%M:%S %p'),
                    "evento": "✅ Dashboard actualizado con datos reales de Supabase",
                    "tipo": "info"
                },
                {
                    "timestamp": datetime.now().strftime('%d-%m-%Y, %I:%M:%S %p'),
                    "evento": f"📊 {self.datos_reales['estadisticas_generales']['total_sentencias']} sentencias cargadas en la base de datos",
                    "tipo": "success"
                }
            ]
            
            with open(data_dir / "activity.json", 'w', encoding='utf-8') as f:
                json.dump(activity_data, f, ensure_ascii=False, indent=2)
            
            # Generar summary.json
            summary_data = {
                "resumen": {
                    "total_sentencias": self.datos_reales['estadisticas_generales']['total_sentencias'],
                    "tribunales_procesados": len(self.datos_reales['tribunales']),
                    "calidad_promedio": round(sum(t['calidad_datos'] for t in self.datos_reales['tribunales']) / len(self.datos_reales['tribunales']), 1) if self.datos_reales['tribunales'] else 0,
                    "fecha_actualizacion": datetime.now().strftime('%d-%m-%Y, %I:%M:%S %p')
                },
                "top_tribunales": [
                    {
                        "nombre": t['nombre'],
                        "total": t['total_sentencias'],
                        "calidad": t['calidad_datos']
                    } for t in sorted(self.datos_reales['tribunales'], key=lambda x: x['total_sentencias'], reverse=True)[:5]
                ]
            }
            
            with open(data_dir / "summary.json", 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)
            
            print("✅ Archivos del dashboard generados correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error generando archivos: {e}")
            return False
    
    def actualizar_dashboard_completo(self):
        """Actualizar dashboard completo con datos reales"""
        print("🚀 ACTUALIZANDO DASHBOARD CON DATOS REALES")
        print("=" * 60)
        
        # Obtener datos
        if not self.obtener_estadisticas_generales():
            return False
        
        if not self.obtener_estadisticas_por_tribunal():
            return False
        
        if not self.generar_archivos_dashboard():
            return False
        
        # Mostrar resumen
        print("\n📊 RESUMEN DE ACTUALIZACIÓN:")
        print(f"   Total de sentencias: {self.datos_reales['estadisticas_generales']['total_sentencias']:,}")
        print(f"   Tribunales procesados: {len(self.datos_reales['tribunales'])}")
        print(f"   Calidad promedio: {round(sum(t['calidad_datos'] for t in self.datos_reales['tribunales']) / len(self.datos_reales['tribunales']), 1)}%")
        
        print("\n🏛️ TOP 5 TRIBUNALES:")
        for i, tribunal in enumerate(sorted(self.datos_reales['tribunales'], key=lambda x: x['total_sentencias'], reverse=True)[:5], 1):
            print(f"   {i}. {tribunal['nombre']}: {tribunal['total_sentencias']:,} sentencias ({tribunal['calidad_datos']}% calidad)")
        
        print("\n✅ Dashboard actualizado con datos reales de Supabase")
        return True

def main():
    """Función principal"""
    print("🔄 ACTUALIZADOR DE DASHBOARD CON DATOS REALES")
    print("=" * 50)
    
    actualizador = ActualizadorDashboard()
    
    if actualizador.actualizar_dashboard_completo():
        print("🎉 Dashboard actualizado exitosamente")
        print("📁 Archivos generados en: data/")
        print("🌐 Dashboard disponible en: https://ceo-exltk.github.io/descarga-sentencias-pjud")
    else:
        print("❌ Error actualizando dashboard")

if __name__ == "__main__":
    main()
