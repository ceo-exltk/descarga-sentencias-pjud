#!/usr/bin/env python3
"""
Script para actualizar el dashboard con las estimaciones realistas
basadas en los análisis previos del código existente
"""

import requests
import json
import os
from datetime import datetime

class DashboardUpdater:
    def __init__(self):
        # Configuración de Supabase
        self.supabase_url = "https://wluachczgiyrmrhdpcue.supabase.co"
        self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndsdWFjaGN6Z2l5cm1yaGRwY3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5MjA1NDcsImV4cCI6MjA3MjQ5NjU0N30.gXSqEYy_LFp951EnBhFxU_7RSf5VbJXRc2GlLn7OB7I"
        
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Estimaciones realistas basadas en el código existente
        self.estimaciones_tribunales = {
            'Corte Suprema': {
                'total_estimado': 26150,  # 2,615 páginas * 10 sentencias
                'icono': '🏛️',
                'descripcion': 'Corte Suprema de Chile'
            },
            'Corte de Apelaciones': {
                'total_estimado': 1509890,  # 150,989 páginas * 10 sentencias
                'icono': '⚖️',
                'descripcion': 'Cortes de Apelaciones'
            },
            'Laborales': {
                'total_estimado': 173960,  # 17,396 páginas * 10 sentencias
                'icono': '💼',
                'descripcion': 'Tribunales Laborales'
            },
            'Penales': {
                'total_estimado': 228010,  # 22,801 páginas * 10 sentencias
                'icono': '⚖️',
                'descripcion': 'Tribunales Penales'
            },
            'Familia': {
                'total_estimado': 113350,  # 11,335 páginas * 10 sentencias
                'icono': '👨‍👩‍👧‍👦',
                'descripcion': 'Tribunales de Familia'
            },
            'Civiles': {
                'total_estimado': 333130,  # 33,313 páginas * 10 sentencias
                'icono': '📋',
                'descripcion': 'Tribunales Civiles'
            },
            'Cobranza': {
                'total_estimado': 26130,  # 2,613 páginas * 10 sentencias
                'icono': '💰',
                'descripcion': 'Tribunales de Cobranza'
            }
        }
    
    def consultar_supabase(self, endpoint, params=None):
        """Consulta Supabase con parámetros"""
        try:
            url = f"{self.supabase_url}/rest/v1/{endpoint}"
            if params:
                url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error consultando Supabase: {e}")
            return []
    
    def obtener_total_descargadas(self):
        """Obtiene el total de sentencias descargadas desde Supabase"""
        try:
            # Obtener conteo total
            response = requests.head(
                f"{self.supabase_url}/rest/v1/sentencias?select=id",
                headers={**self.headers, "Prefer": "count=exact"}
            )
            
            if 'Content-Range' in response.headers:
                total = int(response.headers['Content-Range'].split('/')[-1])
                return total
            else:
                # Fallback: contar registros
                data = self.consultar_supabase("sentencias", {"select": "id"})
                return len(data)
                
        except Exception as e:
            print(f"❌ Error obteniendo total descargadas: {e}")
            return 0
    
    def obtener_distribucion_por_tribunal(self):
        """Obtiene la distribución de sentencias por tribunal desde Supabase"""
        try:
            # Obtener todas las sentencias con su tribunal
            data = self.consultar_supabase("sentencias", {
                "select": "corte",
                "limit": "10000"  # Límite para evitar timeout
            })
            
            # Contar por tribunal
            distribucion = {}
            for sentencia in data:
                corte = sentencia.get('corte', 'Sin especificar')
                distribucion[corte] = distribucion.get(corte, 0) + 1
            
            return distribucion
            
        except Exception as e:
            print(f"❌ Error obteniendo distribución: {e}")
            return {}
    
    def mapear_tribunal_a_categoria(self, corte):
        """Mapea tribunales de Supabase a categorías oficiales"""
        corte_lower = corte.lower()
        
        if 'suprema' in corte_lower:
            return 'Corte Suprema'
        elif 'apelaciones' in corte_lower:
            return 'Corte de Apelaciones'
        elif 'laboral' in corte_lower:
            return 'Laborales'
        elif 'familia' in corte_lower:
            return 'Familia'
        elif 'civil' in corte_lower:
            return 'Civiles'
        elif 'penal' in corte_lower:
            return 'Penales'
        elif 'cobranza' in corte_lower:
            return 'Cobranza'
        else:
            return 'Otros'
    
    def generar_dashboard_data(self):
        """Genera los datos para el dashboard"""
        print("📊 GENERANDO DATOS DEL DASHBOARD")
        print("=" * 40)
        
        # Obtener datos de Supabase
        print("🔍 Consultando Supabase...")
        total_descargadas = self.obtener_total_descargadas()
        distribucion_supabase = self.obtener_distribucion_por_tribunal()
        
        print(f"✅ Total descargadas: {total_descargadas:,}")
        
        # Calcular distribución por tipo de tribunal
        distribucion_por_tipo = {}
        for tipo in self.estimaciones_tribunales.keys():
            distribucion_por_tipo[tipo] = 0
        
        # Mapear datos de Supabase a tipos de tribunal
        for corte, count in distribucion_supabase.items():
            tipo = self.mapear_tribunal_a_categoria(corte)
            if tipo in distribucion_por_tipo:
                distribucion_por_tipo[tipo] += count
        
        # Calcular total estimado
        total_estimado = sum(config['total_estimado'] for config in self.estimaciones_tribunales.values())
        completitud_general = round((total_descargadas / total_estimado * 100), 1)
        
        # Calcular estadísticas por tribunal
        estadisticas_tribunales = {}
        
        for tipo, config in self.estimaciones_tribunales.items():
            descargadas = distribucion_por_tipo.get(tipo, 0)
            total_estimado_tipo = config['total_estimado']
            completitud = round((descargadas / total_estimado_tipo * 100), 1) if total_estimado_tipo > 0 else 0
            
            estadisticas_tribunales[tipo] = {
                'descargadas': descargadas,
                'total_estimado': total_estimado_tipo,
                'completitud': completitud,
                'icono': config['icono'],
                'descripcion': config['descripcion']
            }
        
        # Generar datos finales
        dashboard_data = {
            'timestamp': datetime.now().isoformat(),
            'total_descargadas': total_descargadas,
            'total_estimado': total_estimado,
            'completitud_general': completitud_general,
            'tribunales': estadisticas_tribunales,
            'ultima_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'fuente': 'Supabase + Estimaciones basadas en análisis previo'
        }
        
        return dashboard_data
    
    def actualizar_dashboard_html(self, dashboard_data):
        """Actualiza el archivo HTML del dashboard con los datos reales"""
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Dashboard por Tipo de Tribunal - Sentencias PJUD</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        
        .stat-number {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #718096;
            font-size: 0.9rem;
        }}
        
        .tribunales-section {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
        }}
        
        .tribunales-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .tribunal-card {{
            background: #f7fafc;
            border-radius: 15px;
            padding: 20px;
            border-left: 4px solid #4299e1;
            transition: transform 0.2s ease;
        }}
        
        .tribunal-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .tribunal-header {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .tribunal-icon {{
            font-size: 2rem;
            margin-right: 15px;
        }}
        
        .tribunal-name {{
            font-size: 1.2rem;
            font-weight: bold;
            color: #2d3748;
        }}
        
        .tribunal-stats {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #4299e1;
        }}
        
        .stat-label-small {{
            font-size: 0.8rem;
            color: #718096;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 10px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #4299e1, #63b3ed);
            transition: width 0.3s ease;
        }}
        
        .completitud {{
            font-size: 0.9rem;
            color: #4a5568;
            text-align: center;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            opacity: 0.8;
        }}
        
        .info-box {{
            background: #e6fffa;
            border: 1px solid #38b2ac;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            color: #234e52;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Dashboard por Tipo de Tribunal</h1>
            <p>Progreso de descarga basado en datos reales de Supabase</p>
        </div>
        
        <div class="info-box">
            <strong>📈 Datos Actualizados:</strong> {dashboard_data['ultima_actualizacion']}<br>
            <strong>🔗 Fuente:</strong> {dashboard_data['fuente']}<br>
            <strong>📊 Total Estimado:</strong> {dashboard_data['total_estimado']:,} sentencias
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{dashboard_data['total_descargadas']:,}</div>
                <div class="stat-label">Total Descargadas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{dashboard_data['total_estimado']:,}</div>
                <div class="stat-label">Total Estimado</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{dashboard_data['completitud_general']}%</div>
                <div class="stat-label">% Completitud General</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{dashboard_data['ultima_actualizacion'].split(' ')[1]}</div>
                <div class="stat-label">Última Actualización</div>
            </div>
        </div>
        
        <div class="tribunales-section">
            <h2>🏛️ Progreso por Tipo de Tribunal</h2>
            <div class="tribunales-grid">
"""
        
        # Agregar cards de tribunales
        for tribunal, stats in dashboard_data['tribunales'].items():
            html_content += f"""
                <div class="tribunal-card">
                    <div class="tribunal-header">
                        <div class="tribunal-icon">{stats['icono']}</div>
                        <div class="tribunal-name">{tribunal}</div>
                    </div>
                    
                    <div class="tribunal-stats">
                        <div class="stat-item">
                            <div class="stat-value">{stats['descargadas']:,}</div>
                            <div class="stat-label-small">Descargadas</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{stats['total_estimado']:,}</div>
                            <div class="stat-label-small">Total Estimado</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{stats['completitud']}%</div>
                            <div class="stat-label-small">Completitud</div>
                        </div>
                    </div>
                    
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {min(stats['completitud'], 100)}%"></div>
                    </div>
                    
                    <div class="completitud">
                        Progreso: {stats['descargadas']:,} / {stats['total_estimado']:,} sentencias
                    </div>
                </div>
"""
        
        html_content += """
            </div>
        </div>
        
        <div class="footer">
            <p>🚀 Sistema de Descarga Cloud - GitHub Actions + Supabase</p>
            <p>✅ Monitoreo en tiempo real con estimaciones basadas en análisis previo</p>
        </div>
    </div>
</body>
</html>"""
        
        return html_content

def main():
    """Función principal"""
    print("🔄 ACTUALIZANDO DASHBOARD CON ESTIMACIONES REALISTAS")
    print("=" * 60)
    
    try:
        updater = DashboardUpdater()
        
        # Generar datos del dashboard
        dashboard_data = updater.generar_dashboard_data()
        
        # Generar HTML actualizado
        html_content = updater.actualizar_dashboard_html(dashboard_data)
        
        # Guardar dashboard actualizado
        with open('dashboard_tribunales_final.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Dashboard actualizado: dashboard_tribunales_final.html")
        print(f"📊 Total descargadas: {dashboard_data['total_descargadas']:,}")
        print(f"📊 Total estimado: {dashboard_data['total_estimado']:,}")
        print(f"📊 Completitud general: {dashboard_data['completitud_general']}%")
        
        # Guardar también los datos en JSON para referencia
        with open('dashboard_data_final.json', 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
        
        print("✅ Datos guardados en: dashboard_data_final.json")
        
        # Mostrar resumen por tribunal
        print("\n📊 RESUMEN POR TRIBUNAL:")
        print("-" * 60)
        for tribunal, stats in dashboard_data['tribunales'].items():
            print(f"{tribunal:20} | {stats['descargadas']:>8,} / {stats['total_estimado']:>8,} ({stats['completitud']:>5.1f}%)")
        
    except Exception as e:
        print(f"❌ Error actualizando dashboard: {e}")

if __name__ == "__main__":
    main()
