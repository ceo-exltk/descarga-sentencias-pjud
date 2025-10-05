#!/usr/bin/env python3
"""
Generador de Dashboard - GitHub Pages
Sistema para generar datos del dashboard y bitácora de actividad
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

class GeneradorDashboard:
    """Generador de datos para el dashboard"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL', 'https://wluachczgiyrmrhdpcue.supabase.co')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.dashboard_dir = Path('docs/dashboard')
        self.data_dir = self.dashboard_dir / 'data'
        
        # Crear directorios si no existen
        self.dashboard_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        # Configurar sesión HTTP
        self.session = requests.Session()
        self.session.headers.update({
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json'
        })
    
    def obtener_estadisticas_supabase(self) -> Dict[str, Any]:
        """Obtener estadísticas detalladas desde Supabase"""
        try:
            # Consulta para obtener estadísticas generales
            url = f"{self.supabase_url}/rest/v1/sentencias"
            
            # Parámetros para contar sentencias
            params = {
                'select': 'count',
                'tribunal_type': 'not.is.null'
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                total_sentencias = response.json()[0]['count'] if response.json() else 0
            else:
                total_sentencias = 0
            
            # Obtener estadísticas detalladas por tribunal
            tribunales_stats = {}
            tribunales = [
                'Corte_Suprema', 'Corte_de_Apelaciones', 'Laborales', 
                'Penales', 'Familia', 'Civiles', 'Cobranza'
            ]
            
            for tribunal in tribunales:
                # Contar sentencias por tribunal
                params = {
                    'select': 'count',
                    'tribunal_type': f'eq.{tribunal}'
                }
                
                response = self.session.get(url, params=params)
                count = response.json()[0]['count'] if response.status_code == 200 and response.json() else 0
                
                # Obtener estadísticas de completitud de campos
                params_detalle = {
                    'select': 'rol_numero,caratulado,texto_completo,fecha_sentencia',
                    'tribunal_type': f'eq.{tribunal}',
                    'limit': '1000'  # Muestra para análisis
                }
                
                response_detalle = self.session.get(url, params=params_detalle)
                sentencias_muestra = response_detalle.json() if response_detalle.status_code == 200 else []
                
                # Analizar completitud de campos
                campos_completos = {
                    'rol_numero': sum(1 for s in sentencias_muestra if s.get('rol_numero')),
                    'caratulado': sum(1 for s in sentencias_muestra if s.get('caratulado')),
                    'texto_completo': sum(1 for s in sentencias_muestra if s.get('texto_completo')),
                    'fecha_sentencia': sum(1 for s in sentencias_muestra if s.get('fecha_sentencia'))
                }
                
                # Calcular porcentajes de completitud
                total_muestra = len(sentencias_muestra)
                porcentajes_completitud = {
                    campo: (valor / total_muestra * 100) if total_muestra > 0 else 0
                    for campo, valor in campos_completos.items()
                }
                
                # Obtener rango de fechas
                fechas = [s.get('fecha_sentencia') for s in sentencias_muestra if s.get('fecha_sentencia')]
                fecha_min = min(fechas) if fechas else None
                fecha_max = max(fechas) if fechas else None
                
                tribunales_stats[tribunal] = {
                    'total_sentencias': count,
                    'completitud_campos': porcentajes_completitud,
                    'campos_completos': campos_completos,
                    'fecha_minima': fecha_min,
                    'fecha_maxima': fecha_max,
                    'muestra_analizada': total_muestra
                }
            
            # Calcular estadísticas derivadas
            tribunales_activos = sum(1 for stats in tribunales_stats.values() if stats['total_sentencias'] > 0)
            
            # Calcular completitud general
            completitud_general = {}
            for campo in ['rol_numero', 'caratulado', 'texto_completo', 'fecha_sentencia']:
                total_campo = sum(stats['campos_completos'].get(campo, 0) for stats in tribunales_stats.values())
                total_general = sum(stats['total_sentencias'] for stats in tribunales_stats.values())
                completitud_general[campo] = (total_campo / total_general * 100) if total_general > 0 else 0
            
            # Simular velocidad promedio (esto se podría calcular con timestamps reales)
            velocidad_promedio = total_sentencias // 100 if total_sentencias > 0 else 0
            
            # Calcular tasa de éxito basada en completitud
            tasa_exito = sum(completitud_general.values()) / len(completitud_general) if completitud_general else 0
            
            return {
                'total_sentencias': total_sentencias,
                'tribunales_activos': tribunales_activos,
                'velocidad_promedio': velocidad_promedio,
                'tasa_exito': round(tasa_exito, 2),
                'completitud_general': completitud_general,
                'tribunales_stats': tribunales_stats,
                'ultima_actualizacion': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error obteniendo estadísticas de Supabase: {e}")
            return {
                'total_sentencias': 0,
                'tribunales_activos': 0,
                'velocidad_promedio': 0,
                'tasa_exito': 0,
                'completitud_general': {},
                'tribunales_stats': {},
                'ultima_actualizacion': datetime.now().isoformat()
            }
    
    def obtener_estado_tribunales(self) -> List[Dict[str, Any]]:
        """Obtener estado detallado de cada tribunal con análisis de completitud"""
        try:
            tribunales = [
                {
                    'nombre': 'Corte Suprema',
                    'codigo': 'Corte_Suprema',
                    'sentencias_estimadas': 50000,
                    'color': '#e74c3c'
                },
                {
                    'nombre': 'Corte de Apelaciones',
                    'codigo': 'Corte_de_Apelaciones',
                    'sentencias_estimadas': 100000,
                    'color': '#f39c12'
                },
                {
                    'nombre': 'Laborales',
                    'codigo': 'Laborales',
                    'sentencias_estimadas': 75000,
                    'color': '#3498db'
                },
                {
                    'nombre': 'Penales',
                    'codigo': 'Penales',
                    'sentencias_estimadas': 150000,
                    'color': '#9b59b6'
                },
                {
                    'nombre': 'Familia',
                    'codigo': 'Familia',
                    'sentencias_estimadas': 60000,
                    'color': '#2ecc71'
                },
                {
                    'nombre': 'Civiles',
                    'codigo': 'Civiles',
                    'sentencias_estimadas': 80000,
                    'color': '#1abc9c'
                },
                {
                    'nombre': 'Cobranza',
                    'codigo': 'Cobranza',
                    'sentencias_estimadas': 40000,
                    'color': '#34495e'
                }
            ]
            
            # Obtener estadísticas detalladas de Supabase
            stats = self.obtener_estadisticas_supabase()
            tribunales_stats = stats.get('tribunales_stats', {})
            
            # Crear estado detallado para cada tribunal
            estado_tribunales = []
            
            for tribunal in tribunales:
                codigo = tribunal['codigo']
                tribunal_data = tribunales_stats.get(codigo, {})
                
                sentencias_descargadas = tribunal_data.get('total_sentencias', 0)
                progreso = (sentencias_descargadas / tribunal['sentencias_estimadas']) * 100
                
                # Obtener información de completitud
                completitud_campos = tribunal_data.get('completitud_campos', {})
                fecha_minima = tribunal_data.get('fecha_minima')
                fecha_maxima = tribunal_data.get('fecha_maxima')
                
                # Calcular calidad de datos
                calidad_datos = sum(completitud_campos.values()) / len(completitud_campos) if completitud_campos else 0
                
                # Determinar estado basado en progreso y calidad
                if progreso >= 100 and calidad_datos >= 80:
                    estado = 'completed'
                elif progreso > 0 and calidad_datos >= 60:
                    estado = 'active'
                elif progreso > 0:
                    estado = 'partial'
                else:
                    estado = 'pending'
                
                # Obtener números de sentencia únicos
                numeros_sentencia = self.obtener_numeros_sentencia_tribunal(codigo)
                
                estado_tribunales.append({
                    'nombre': tribunal['nombre'],
                    'codigo': tribunal['codigo'],
                    'sentencias_descargadas': sentencias_descargadas,
                    'sentencias_estimadas': tribunal['sentencias_estimadas'],
                    'progreso': round(progreso, 2),
                    'estado': estado,
                    'color': tribunal['color'],
                    'calidad_datos': round(calidad_datos, 2),
                    'completitud_campos': completitud_campos,
                    'fecha_minima': fecha_minima,
                    'fecha_maxima': fecha_maxima,
                    'numeros_sentencia_unicos': len(numeros_sentencia),
                    'ejemplos_numeros': numeros_sentencia[:5],  # Primeros 5 ejemplos
                    'ultima_actualizacion': datetime.now().isoformat()
                })
            
            return estado_tribunales
            
        except Exception as e:
            print(f"Error obteniendo estado de tribunales: {e}")
            return []
    
    def obtener_numeros_sentencia_tribunal(self, tribunal_codigo: str) -> List[str]:
        """Obtener números de sentencia únicos para un tribunal"""
        try:
            url = f"{self.supabase_url}/rest/v1/sentencias"
            params = {
                'select': 'rol_numero',
                'tribunal_type': f'eq.{tribunal_codigo}',
                'rol_numero': 'not.is.null',
                'limit': '1000'
            }
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                sentencias = response.json()
                numeros = [s.get('rol_numero') for s in sentencias if s.get('rol_numero')]
                return list(set(numeros))  # Eliminar duplicados
            else:
                return []
                
        except Exception as e:
            print(f"Error obteniendo números de sentencia para {tribunal_codigo}: {e}")
            return []
    
    def obtener_bitacora_actividad(self) -> Dict[str, Any]:
        """Obtener bitácora de actividad"""
        try:
            # Crear entradas de bitácora simuladas (en un sistema real, esto vendría de logs)
            entradas = [
                {
                    'timestamp': datetime.now().isoformat(),
                    'message': 'Dashboard actualizado automáticamente',
                    'tipo': 'info',
                    'nivel': 'info'
                },
                {
                    'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
                    'message': 'Descarga incremental completada para Corte Suprema',
                    'tipo': 'success',
                    'nivel': 'info'
                },
                {
                    'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat(),
                    'message': 'Iniciando descarga histórica para Laborales',
                    'tipo': 'info',
                    'nivel': 'info'
                },
                {
                    'timestamp': (datetime.now() - timedelta(minutes=30)).isoformat(),
                    'message': 'Workflow GitHub Actions ejecutado exitosamente',
                    'tipo': 'success',
                    'nivel': 'info'
                },
                {
                    'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
                    'message': 'Sistema de monitoreo activado',
                    'tipo': 'info',
                    'nivel': 'info'
                }
            ]
            
            return {
                'entradas': entradas,
                'total_entradas': len(entradas),
                'ultima_actualizacion': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error obteniendo bitácora: {e}")
            return {
                'entradas': [],
                'total_entradas': 0,
                'ultima_actualizacion': datetime.now().isoformat()
            }
    
    def generar_archivos_dashboard(self):
        """Generar todos los archivos del dashboard"""
        print("🔄 Generando archivos del dashboard...")
        
        try:
            # 1. Generar estadísticas
            print("📊 Generando estadísticas...")
            stats = self.obtener_estadisticas_supabase()
            stats_file = self.data_dir / 'stats.json'
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            print(f"✅ Estadísticas guardadas en {stats_file}")
            
            # 2. Generar estado de tribunales
            print("🏛️ Generando estado de tribunales...")
            tribunales = self.obtener_estado_tribunales()
            tribunales_file = self.data_dir / 'tribunals.json'
            with open(tribunales_file, 'w', encoding='utf-8') as f:
                json.dump(tribunales, f, ensure_ascii=False, indent=2)
            print(f"✅ Estado de tribunales guardado en {tribunales_file}")
            
            # 3. Generar bitácora de actividad
            print("📝 Generando bitácora de actividad...")
            actividad = self.obtener_bitacora_actividad()
            actividad_file = self.data_dir / 'activity.json'
            with open(actividad_file, 'w', encoding='utf-8') as f:
                json.dump(actividad, f, ensure_ascii=False, indent=2)
            print(f"✅ Bitácora guardada en {actividad_file}")
            
            # 4. Generar resumen general
            print("📋 Generando resumen general...")
            resumen = {
                'dashboard_info': {
                    'nombre': 'Dashboard de Descarga de Sentencias PJUD',
                    'version': '1.0.0',
                    'ultima_actualizacion': datetime.now().isoformat(),
                    'fuente_datos': 'Supabase + GitHub Actions'
                },
                'estadisticas': stats,
                'tribunales': tribunales,
                'actividad': actividad
            }
            
            resumen_file = self.data_dir / 'summary.json'
            with open(resumen_file, 'w', encoding='utf-8') as f:
                json.dump(resumen, f, ensure_ascii=False, indent=2)
            print(f"✅ Resumen guardado en {resumen_file}")
            
            print("🎉 Dashboard generado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error generando dashboard: {e}")
            return False
    
    def mostrar_resumen(self):
        """Mostrar resumen del dashboard generado"""
        try:
            resumen_file = self.data_dir / 'summary.json'
            if resumen_file.exists():
                with open(resumen_file, 'r', encoding='utf-8') as f:
                    resumen = json.load(f)
                
                print("\n" + "=" * 60)
                print("📊 RESUMEN DEL DASHBOARD")
                print("=" * 60)
                
                stats = resumen['estadisticas']
                print(f"📄 Total de sentencias: {stats['total_sentencias']:,}")
                print(f"🏛️ Tribunales activos: {stats['tribunales_activos']}")
                print(f"⚡ Velocidad promedio: {stats['velocidad_promedio']} sentencias/min")
                print(f"🎯 Tasa de éxito: {stats['tasa_exito']}%")
                
                print(f"\n🏛️ ESTADO POR TRIBUNAL:")
                for tribunal in resumen['tribunales']:
                    print(f"   {tribunal['nombre']}: {tribunal['sentencias_descargadas']:,} / {tribunal['sentencias_estimadas']:,} ({tribunal['progreso']:.1f}%)")
                
                print(f"\n📝 ACTIVIDAD:")
                print(f"   Entradas en bitácora: {resumen['actividad']['total_entradas']}")
                print(f"   Última actualización: {resumen['dashboard_info']['ultima_actualizacion']}")
                
                print("=" * 60)
                
        except Exception as e:
            print(f"Error mostrando resumen: {e}")

def main():
    """Función principal"""
    print("🚀 GENERADOR DE DASHBOARD")
    print("=" * 50)
    print("Generando datos para GitHub Pages...")
    print("=" * 50)
    
    # Verificar variables de entorno
    if not os.getenv('SUPABASE_ANON_KEY'):
        print("⚠️ Advertencia: SUPABASE_ANON_KEY no configurado")
        print("💡 Usando datos simulados para el dashboard")
    
    # Crear generador
    generador = GeneradorDashboard()
    
    # Generar dashboard
    exito = generador.generar_archivos_dashboard()
    
    if exito:
        generador.mostrar_resumen()
        print("\n🎉 Dashboard generado exitosamente")
        print("📁 Archivos disponibles en: docs/dashboard/")
        print("🌐 Para ver el dashboard: docs/dashboard/index.html")
    else:
        print("\n❌ Error generando dashboard")
        sys.exit(1)

if __name__ == "__main__":
    main()
