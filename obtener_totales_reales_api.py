#!/usr/bin/env python3
"""
Script para obtener totales reales de sentencias por tribunal
Basado en el análisis del flujo exacto del sitio web juris.pjud.cl
"""

import requests
import json
import re
import time
from datetime import datetime
import sys

# Configuración de buscadores (id y cabecera)
BUSCADORES = {
    "Corte_Suprema": ("528", "Buscador_Jurisprudencial_de_la_Corte_Suprema"),
    "Corte_de_Apelaciones": ("529", "Buscador_Jurisprudencial_de_Cortes_de_Apelaciones"),
    "Laborales": ("530", "Buscador_Jurisprudencial_de_Tribunales_Laborales"),
    "Penales": ("531", "Buscador_Jurisprudencial_de_Tribunales_Penales"),
    "Familia": ("532", "Buscador_Jurisprudencial_de_Tribunales_de_Familia"),
    "Civiles": ("533", "Buscador_Jurisprudencial_de_Tribunales_Civiles"),
    "Cobranza": ("534", "Buscador_Jurisprudencial_de_Tribunales_de_Cobranza"),
}

def obtener_token(session):
    """Visita la página principal y extrae el token CSRF"""
    print("🔍 Obteniendo token CSRF...")
    try:
        resp = session.get("https://juris.pjud.cl/", timeout=30)
        resp.raise_for_status()
        
        # Buscar el token CSRF en el HTML
        m = re.search(r'name="_token"\s+value="([^"]+)"', resp.text)
        if m:
            token = m.group(1)
            print(f"✅ Token CSRF obtenido: {token[:20]}...")
            return token
        else:
            print("❌ No se encontró token CSRF en la respuesta")
            return None
    except Exception as e:
        print(f"❌ Error obteniendo token CSRF: {e}")
        return None

def establecer_contexto(session):
    """Establece el contexto de la sesión"""
    print("🔍 Estableciendo contexto de sesión...")
    try:
        resp = session.get("https://juris.pjud.cl/busqueda", timeout=30)
        resp.raise_for_status()
        print("✅ Contexto establecido correctamente")
        return True
    except Exception as e:
        print(f"❌ Error estableciendo contexto: {e}")
        return False

def obtener_total(session, token, id_buscador, cabecera, nombre_tribunal):
    """Obtiene el total de sentencias para un buscador específico"""
    print(f"🔍 Consultando {nombre_tribunal}...")
    
    # Filtros vacíos para contar todo el universo de fallos
    filtros_vacios = {
        "rol": "", "era": "", "fec_desde": "", "fec_hasta": "",
        "tipo_norma": "", "num_norma": "", "num_art": "", "num_inciso": "",
        "todas": "", "algunas": "", "excluir": "", "literal": "",
        "proximidad": "", "distancia": "", "analisis_s": "", "submaterias": "",
        "facetas_seleccionadas": [], "filtros_omnibox": [], "ids_comunas_seleccionadas_mapa": []
    }
    
    payload = {
        "_token": token,
        "id_buscador": id_buscador,
        "filtros": json.dumps(filtros_vacios, ensure_ascii=False),
        "numero_filas_paginacion": "1",
        "offset_paginacion": "0",
        "orden": "rel"
    }
    
    headers = {
        "busqueda": cabecera,
        "Content-Type": "application/json",
        "Referer": "https://juris.pjud.cl/busqueda",
        "X-Requested-With": "XMLHttpRequest",
    }
    
    try:
        resp = session.post(
            "https://juris.pjud.cl/busqueda/buscar_sentencias",
            json=payload, 
            headers=headers, 
            timeout=30
        )
        resp.raise_for_status()
        
        data = resp.json()
        total = data.get("response", {}).get("numFound", 0)
        print(f"✅ {nombre_tribunal}: {total:,} sentencias")
        return total
        
    except Exception as e:
        print(f"❌ Error consultando {nombre_tribunal}: {e}")
        return 0

def obtener_totales_todos():
    """Obtiene los totales de todos los tribunales"""
    print("🚀 Iniciando obtención de totales reales por tribunal...")
    print("=" * 60)
    
    resultados = {}
    total_general = 0
    
    with requests.Session() as s:
        # Cabeceras de navegador para evitar bloqueos
        s.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "es-ES,es;q=0.9",
            "X-Requested-With": "XMLHttpRequest",
        })
        
        # Paso 1: Obtener token CSRF
        token = obtener_token(s)
        if not token:
            raise RuntimeError("No se pudo obtener token CSRF")
        
        # Paso 2: Establecer contexto
        if not establecer_contexto(s):
            raise RuntimeError("No se pudo establecer contexto")
        
        # Paso 3: Consultar cada tribunal
        print("\n📊 Consultando tribunales...")
        print("-" * 40)
        
        for nombre, (id_bus, cabecera) in BUSCADORES.items():
            # Pequeña pausa entre solicitudes para no saturar el servidor
            time.sleep(2)
            
            total = obtener_total(s, token, id_bus, cabecera, nombre)
            resultados[nombre] = total
            total_general += total
        
        print("-" * 40)
        print(f"📈 Total general: {total_general:,} sentencias")
    
    return resultados, total_general

def guardar_resultados(resultados, total_general):
    """Guarda los resultados en un archivo JSON"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"totales_reales_api_{timestamp}.json"
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "totales_por_tribunal": resultados,
        "total_general": total_general,
        "fuente": "API oficial PJUD (juris.pjud.cl)",
        "metodo": "Consulta directa usando endpoints reales",
        "ip_origen": "Local",
        "confiabilidad": "Alta - Datos obtenidos directamente de la API",
        "endpoints_utilizados": [
            "https://juris.pjud.cl/ (token CSRF)",
            "https://juris.pjud.cl/busqueda (contexto)",
            "https://juris.pjud.cl/busqueda/buscar_sentencias (consulta)"
        ]
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Resultados guardados en: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error guardando resultados: {e}")
        return None

def main():
    """Función principal"""
    try:
        print("🏛️  SISTEMA DE OBTENCIÓN DE TOTALES REALES - PJUD")
        print("=" * 60)
        
        # Obtener totales
        resultados, total_general = obtener_totales_todos()
        
        # Mostrar resumen
        print("\n📋 RESUMEN DE RESULTADOS")
        print("=" * 60)
        for nombre, total in resultados.items():
            print(f"{nombre:20}: {total:>10,} sentencias")
        
        print("-" * 60)
        print(f"{'TOTAL GENERAL':20}: {total_general:>10,} sentencias")
        
        # Guardar resultados
        archivo = guardar_resultados(resultados, total_general)
        
        print("\n✅ Proceso completado exitosamente!")
        if archivo:
            print(f"📁 Archivo generado: {archivo}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en el proceso: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)