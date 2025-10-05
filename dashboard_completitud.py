#!/usr/bin/env python3
"""
Dashboard de Completitud - Compara totales reales vs descargados
Ejecuta el script funcional y consulta Supabase para calcular completitud
"""

import json
import subprocess
import sys
from datetime import datetime
import os

# Importar el script funcional
sys.path.append('.')
from obtener_totales_reales_api import obtener_totales_todos

def consultar_supabase():
    """Consultar Supabase para obtener totales descargados por tribunal"""
    try:
        # Aquí iría la consulta a Supabase
        # Por ahora retornamos datos de ejemplo
        # TODO: Implementar consulta real a Supabase
        
        # Datos de ejemplo - reemplazar con consulta real
        descargados = {
            "Corte_Suprema": 0,
            "Corte_de_Apelaciones": 0,
            "Laborales": 0,
            "Penales": 0,
            "Familia": 0,
            "Civiles": 0,
            "Cobranza": 0
        }
        
        print("📊 Consultando Supabase...")
        print("⚠️  NOTA: Implementar consulta real a Supabase")
        return descargados
        
    except Exception as e:
        print(f"❌ Error consultando Supabase: {e}")
        return {}

def calcular_completitud(totales_reales, descargados):
    """Calcular nivel de completitud por tribunal"""
    completitud = {}
    
    for tribunal in totales_reales:
        real = totales_reales[tribunal]
        descargado = descargados.get(tribunal, 0)
        
        if real > 0:
            porcentaje = (descargado / real) * 100
        else:
            porcentaje = 0
            
        completitud[tribunal] = {
            "total_real": real,
            "descargado": descargado,
            "porcentaje": round(porcentaje, 2),
            "pendiente": real - descargado
        }
    
    return completitud

def generar_dashboard_data(completitud):
    """Generar datos para el dashboard"""
    total_real = sum(data["total_real"] for data in completitud.values())
    total_descargado = sum(data["descargado"] for data in completitud.values())
    total_pendiente = total_real - total_descargado
    completitud_general = (total_descargado / total_real * 100) if total_real > 0 else 0
    
    dashboard_data = {
        "timestamp": datetime.now().isoformat(),
        "resumen": {
            "total_real": total_real,
            "total_descargado": total_descargado,
            "total_pendiente": total_pendiente,
            "completitud_general": round(completitud_general, 2)
        },
        "tribunales": completitud,
        "fuente": "API oficial PJUD + Supabase",
        "metodo": "Comparación totales reales vs descargados"
    }
    
    return dashboard_data

def main():
    """Función principal"""
    print("🚀 DASHBOARD DE COMPLETITUD")
    print("=" * 50)
    
    # 1. Obtener totales reales usando el script funcional
    print("📊 Obteniendo totales reales de la API del PJUD...")
    try:
        resultados, total_general = obtener_totales_todos()
        totales_reales = resultados
        print("✅ Totales reales obtenidos exitosamente")
    except Exception as e:
        print(f"❌ Error obteniendo totales reales: {e}")
        return
    
    # 2. Consultar Supabase para totales descargados
    print("\n📊 Consultando Supabase para totales descargados...")
    descargados = consultar_supabase()
    
    # 3. Calcular completitud
    print("\n📊 Calculando nivel de completitud...")
    completitud = calcular_completitud(totales_reales, descargados)
    
    # 4. Generar datos del dashboard
    dashboard_data = generar_dashboard_data(completitud)
    
    # 5. Mostrar resumen
    print("\n📈 RESUMEN DE COMPLETITUD")
    print("=" * 50)
    print(f"Total real: {dashboard_data['resumen']['total_real']:,} sentencias")
    print(f"Total descargado: {dashboard_data['resumen']['total_descargado']:,} sentencias")
    print(f"Total pendiente: {dashboard_data['resumen']['total_pendiente']:,} sentencias")
    print(f"Completitud general: {dashboard_data['resumen']['completitud_general']}%")
    
    print("\n📊 COMPLETITUD POR TRIBUNAL")
    print("-" * 50)
    for tribunal, data in completitud.items():
        print(f"{tribunal.replace('_', ' ')}:")
        print(f"  Real: {data['total_real']:,} | Descargado: {data['descargado']:,} | Completitud: {data['porcentaje']}%")
    
    # 6. Guardar datos
    os.makedirs("docs", exist_ok=True)
    with open("docs/dashboard_data.json", "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Datos guardados en: docs/dashboard_data.json")
    print("✅ Dashboard de completitud generado exitosamente!")

if __name__ == "__main__":
    main()
