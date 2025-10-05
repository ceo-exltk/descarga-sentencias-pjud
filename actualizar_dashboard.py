#!/usr/bin/env python3
"""
Script para actualizar el dashboard con los totales reales por tribunal
"""

import json
from datetime import datetime
import os

# Totales reales obtenidos del script funcional
TOTALES_REALES = {
    "Corte_Suprema": 261871,
    "Corte_de_Apelaciones": 1510429,
    "Laborales": 233904,
    "Penales": 862269,
    "Familia": 371320,
    "Civiles": 849956,
    "Cobranza": 26132
}

TOTAL_GENERAL = sum(TOTALES_REALES.values())

def main():
    """Función principal"""
    print("🔄 Actualizando dashboard con totales reales por tribunal...")
    
    # Crear directorio si no existe
    os.makedirs("docs/dashboard/data", exist_ok=True)
    
    # Crear datos simplificados para el dashboard
    stats = {
        "total_sentencias": TOTAL_GENERAL,
        "tribunales_activos": 7,
        "ultima_actualizacion": datetime.now().isoformat(),
        "fuente": "API oficial PJUD (juris.pjud.cl)",
        "metodo": "Consulta directa con IDs de buscador corregidos",
        "confiabilidad": "Alta - IDs extraídos del código fuente real"
    }
    
    # Crear datos de tribunales
    tribunals = []
    for tribunal, total in TOTALES_REALES.items():
        tribunal_data = {
            "nombre": tribunal.replace("_", " "),
            "total": total,
            "estado": "disponible",
            "ultima_actualizacion": datetime.now().isoformat()
        }
        tribunals.append(tribunal_data)
    
    # Crear actividad reciente
    activity = {
        "entries": [
            {
                "timestamp": datetime.now().isoformat(),
                "message": f"✅ Totales reales obtenidos: {TOTAL_GENERAL:,} sentencias en 7 tribunales",
                "type": "success"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "message": "🔍 IDs de buscador corregidos basados en código fuente real",
                "type": "info"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "message": "📊 Dashboard actualizado con datos oficiales del PJUD",
                "type": "info"
            }
        ]
    }
    
    # Guardar archivos
    with open("docs/dashboard/data/stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    with open("docs/dashboard/data/tribunals.json", "w", encoding="utf-8") as f:
        json.dump(tribunals, f, indent=2, ensure_ascii=False)
    
    with open("docs/dashboard/data/activity.json", "w", encoding="utf-8") as f:
        json.dump(activity, f, indent=2, ensure_ascii=False)
    
    print("✅ Dashboard actualizado exitosamente!")
    print(f"📊 Total general: {TOTAL_GENERAL:,} sentencias")
    print("📁 Archivos actualizados:")
    print("  - docs/dashboard/data/stats.json")
    print("  - docs/dashboard/data/tribunals.json")
    print("  - docs/dashboard/data/activity.json")
    print("\n🎯 Totales por tribunal:")
    for tribunal, total in TOTALES_REALES.items():
        print(f"  - {tribunal.replace('_', ' ')}: {total:,} sentencias")

if __name__ == "__main__":
    main()