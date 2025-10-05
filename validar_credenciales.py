#!/usr/bin/env python3
"""
Validar Credenciales de Supabase
Script para verificar que las credenciales y endpoints funcionan correctamente
"""

import requests
import json
from datetime import datetime

def validar_credenciales():
    """Validar credenciales de Supabase"""
    
    # Configuración
    SUPABASE_URL = "https://wluachczgiyrmrhdpcue.supabase.co"
    SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndsdWFjaGN6Z2l5cm1yaGRwY3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5MjA1NDcsImV4cCI6MjA3MjQ5NjU0N30.gXSqEYy_LFp951EnBhFxU_7RSf5VbJXRc2GlLn7OB7I"
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 VALIDANDO CREDENCIALES DE SUPABASE")
    print("=" * 50)
    
    # Test 1: Obtener una sentencia específica
    print("1. Probando endpoint básico...")
    try:
        url = f"{SUPABASE_URL}/rest/v1/sentencias?select=id,caratulado,corte&limit=1"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito: {len(data)} sentencia obtenida")
            if data:
                print(f"   ID: {data[0].get('id')}")
                print(f"   Caratulado: {data[0].get('caratulado')}")
                print(f"   Corte: {data[0].get('corte')}")
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # Test 2: Contar total de sentencias
    print("\n2. Contando total de sentencias...")
    try:
        url = f"{SUPABASE_URL}/rest/v1/sentencias?select=count"
        response = requests.head(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content_range = response.headers.get('content-range')
            if content_range:
                total = content_range.split('/')[1]
                print(f"✅ Total de sentencias: {total}")
            else:
                print("⚠️ No se pudo obtener el conteo total")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error contando: {e}")
    
    # Test 3: Obtener datos por tribunal
    print("\n3. Probando filtros por tribunal...")
    try:
        url = f"{SUPABASE_URL}/rest/v1/sentencias?corte=eq.C.A.%20de%20Santiago&select=corte&limit=5"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sentencias de C.A. de Santiago: {len(data)}")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error filtrando: {e}")
    
    # Test 4: Búsqueda de texto completo
    print("\n4. Probando búsqueda de texto...")
    try:
        url = f"{SUPABASE_URL}/rest/v1/sentencias?select=id,caratulado&fts_vector=wfts.contrato&limit=3"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Búsqueda 'contrato': {len(data)} resultados")
            for item in data:
                print(f"   - {item.get('caratulado')}")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
    
    print("\n🎉 VALIDACIÓN COMPLETADA")
    print("=" * 50)
    return True

if __name__ == "__main__":
    validar_credenciales()
