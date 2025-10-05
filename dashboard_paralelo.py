#!/usr/bin/env python3
"""
Dashboard de Completitud - Ejecución paralela de requests
Obtiene token CSRF y ejecuta POST requests en paralelo para todos los tribunales
"""

import requests
import json
import re
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuración de buscadores (id y cabecera) - IDs CORRECTOS
BUSCADORES = {
    "Corte_Suprema": ("528", "Buscador_Jurisprudencial_de_la_Corte_Suprema"),
    "Corte_de_Apelaciones": ("168", "Buscador_Jurisprudencial_de_Cortes_de_Apelaciones"),
    "Laborales": ("271", "Buscador_Jurisprudencial_de_Tribunales_Laborales"),
    "Penales": ("268", "Buscador_Jurisprudencial_de_Tribunales_Penales"),
    "Familia": ("270", "Buscador_Jurisprudencial_de_Tribunales_de_Familia"),
    "Civiles": ("328", "Buscador_Jurisprudencial_de_Tribunales_Civiles"),
    "Cobranza": ("269", "Buscador_Jurisprudencial_de_Tribunales_de_Cobranza"),
}

def obtener_token_y_contexto():
    """Obtener token CSRF y establecer contexto de sesión"""
    session = requests.Session()
    
    # 1. Obtener token CSRF
    print("🔑 Obteniendo token CSRF...")
    try:
        resp = session.get("https://juris.pjud.cl/", timeout=30)
        resp.raise_for_status()
        
        m = re.search(r'name="_token"\s+value="([^"]+)"', resp.text)
        if not m:
            raise Exception("No se encontró el token CSRF")
        
        token = m.group(1)
        print(f"✅ Token CSRF obtenido: {token[:20]}...")
        
    except Exception as e:
        print(f"❌ Error obteniendo token: {e}")
        return None, None
    
    # 2. Establecer contexto
    print("🌐 Estableciendo contexto...")
    try:
        resp = session.get("https://juris.pjud.cl/busqueda", timeout=30)
        resp.raise_for_status()
        print("✅ Contexto establecido")
        
    except Exception as e:
        print(f"❌ Error estableciendo contexto: {e}")
        return None, None
    
    return session, token

def consultar_tribunal(session, token, tribunal, id_buscador, cabecera):
    """Consultar un tribunal específico"""
    try:
        print(f"🔍 Consultando {tribunal}...")
        
        # Preparar datos del POST
        data = {
            "_token": token,
            "id_buscador": id_buscador,
            "filtros": '{"rol":"","era":"","fec_desde":"","fec_hasta":"","tipo_norma":"","num_norma":"","num_art":"","num_inciso":"","todas":"","algunas":"","excluir":"","literal":"","proximidad":"","distancia":"","analisis_s":"","submaterias":"","facetas_seleccionadas":[],"filtros_omnibox":[],"ids_comunas_seleccionadas_mapa":[]}',
            "numero_filas_paginacion": "1",
            "offset_paginacion": "0",
            "orden": "rel"
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
            "busqueda": cabecera,
            "Content-Type": "application/json",
            "Referer": f"https://juris.pjud.cl/busqueda?{tribunal}"
        }
        
        # Ejecutar POST request
        resp = session.post(
            "https://juris.pjud.cl/busqueda/buscar_sentencias",
            json=data,
            headers=headers,
            timeout=30
        )
        
        if resp.status_code == 200:
            data_resp = resp.json()
            if 'response' in data_resp and 'numFound' in data_resp['response']:
                total = data_resp['response']['numFound']
                print(f"✅ {tribunal}: {total:,} sentencias")
                return tribunal, total
            else:
                print(f"❌ {tribunal}: No se encontró 'numFound' en la respuesta")
                return tribunal, 0
        else:
            print(f"❌ {tribunal}: Error {resp.status_code}")
            return tribunal, 0
            
    except Exception as e:
        print(f"❌ {tribunal}: Error - {e}")
        return tribunal, 0

def consultar_supabase():
    """Consultar Supabase para obtener totales descargados por tribunal"""
    try:
        # TODO: Implementar consulta real a Supabase
        # Por ahora retornamos datos de ejemplo
        print("📊 Consultando Supabase...")
        print("⚠️  NOTA: Implementar consulta real a Supabase")
        
        descargados = {
            "Corte_Suprema": 0,
            "Corte_de_Apelaciones": 0,
            "Laborales": 0,
            "Penales": 0,
            "Familia": 0,
            "Civiles": 0,
            "Cobranza": 0
        }
        
        return descargados
        
    except Exception as e:
        print(f"❌ Error consultando Supabase: {e}")
        return {}

def ejecutar_requests_paralelos():
    """Ejecutar requests en paralelo para todos los tribunales"""
    print("🚀 DASHBOARD DE COMPLETITUD - EJECUCIÓN PARALELA")
    print("=" * 60)
    
    # 1. Obtener token y contexto
    session, token = obtener_token_y_contexto()
    if not session or not token:
        return None
    
    # 2. Ejecutar requests en paralelo
    print("\n📊 Ejecutando requests en paralelo...")
    print("-" * 40)
    
    totales_reales = {}
    
    with ThreadPoolExecutor(max_workers=7) as executor:
        # Enviar todos los requests
        futures = {}
        for tribunal, (id_buscador, cabecera) in BUSCADORES.items():
            future = executor.submit(
                consultar_tribunal, 
                session, token, tribunal, id_buscador, cabecera
            )
            futures[future] = tribunal
        
        # Recoger resultados
        for future in as_completed(futures):
            tribunal, total = future.result()
            totales_reales[tribunal] = total
    
    # 3. Consultar Supabase
    print("\n📊 Consultando Supabase...")
    descargados = consultar_supabase()
    
    # 4. Calcular completitud
    print("\n📊 Calculando completitud...")
    completitud = {}
    total_real = 0
    total_descargado = 0
    
    for tribunal in BUSCADORES.keys():
        real = totales_reales.get(tribunal, 0)
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
        
        total_real += real
        total_descargado += descargado
    
    # 5. Generar datos del dashboard
    completitud_general = (total_descargado / total_real * 100) if total_real > 0 else 0
    
    dashboard_data = {
        "timestamp": datetime.now().isoformat(),
        "resumen": {
            "total_real": total_real,
            "total_descargado": total_descargado,
            "total_pendiente": total_real - total_descargado,
            "completitud_general": round(completitud_general, 2)
        },
        "tribunales": completitud,
        "fuente": "API oficial PJUD + Supabase",
        "metodo": "Ejecución paralela de requests"
    }
    
    # 6. Mostrar resumen
    print("\n📈 RESUMEN DE COMPLETITUD")
    print("=" * 60)
    print(f"Total real: {total_real:,} sentencias")
    print(f"Total descargado: {total_descargado:,} sentencias")
    print(f"Total pendiente: {total_real - total_descargado:,} sentencias")
    print(f"Completitud general: {completitud_general:.2f}%")
    
    print("\n📊 COMPLETITUD POR TRIBUNAL")
    print("-" * 60)
    for tribunal, data in completitud.items():
        print(f"{tribunal.replace('_', ' ')}:")
        print(f"  Real: {data['total_real']:,} | Descargado: {data['descargado']:,} | Completitud: {data['porcentaje']}%")
    
    # 7. Guardar datos
    os.makedirs("docs", exist_ok=True)
    with open("docs/dashboard_data.json", "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Datos guardados en: docs/dashboard_data.json")
    print("✅ Dashboard de completitud generado exitosamente!")
    
    return dashboard_data

def main():
    """Función principal"""
    try:
        dashboard_data = ejecutar_requests_paralelos()
        if dashboard_data:
            print("\n🎯 Dashboard actualizado exitosamente!")
        else:
            print("\n❌ Error generando dashboard")
    except Exception as e:
        print(f"\n❌ Error en el proceso: {e}")

if __name__ == "__main__":
    main()
