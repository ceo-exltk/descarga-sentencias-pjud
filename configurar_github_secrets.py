#!/usr/bin/env python3
"""
Script para configurar automáticamente los GitHub Secrets
"""

import os
import sys
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def generate_github_token():
    """Genera un token de GitHub para configurar secrets"""
    print("🔑 CONFIGURACIÓN DE GITHUB SECRETS")
    print("=" * 50)
    print()
    print("Para configurar automáticamente los secrets, necesitas:")
    print("1. Un token de GitHub con permisos de repositorio")
    print("2. Las credenciales de Supabase")
    print()
    print("📋 PASOS MANUALES (Recomendado):")
    print("1. Ve a tu repositorio en GitHub")
    print("2. Settings → Secrets and variables → Actions")
    print("3. Click 'New repository secret'")
    print("4. Agrega estos secrets:")
    print()
    print("   SUPABASE_URL:")
    print("   - Valor: https://tu-proyecto.supabase.co")
    print("   - Ejemplo: https://abcdefghijklmnop.supabase.co")
    print()
    print("   SUPABASE_ANON_KEY:")
    print("   - Valor: Tu anon key de Supabase")
    print("   - Encuéntralo en: Supabase Dashboard → Settings → API")
    print()
    print("✅ Una vez configurados, el workflow cargará automáticamente a Supabase")

def show_supabase_setup():
    """Muestra las instrucciones para configurar Supabase"""
    print("🔧 CONFIGURACIÓN DE SUPABASE")
    print("=" * 50)
    print()
    print("1. Ve a https://supabase.com y crea un proyecto")
    print("2. En el Dashboard, ve a Settings → API")
    print("3. Copia la 'Project URL' y 'anon public' key")
    print("4. En SQL Editor, ejecuta este código:")
    print()
    print("""
    CREATE TABLE sentencias (
        id SERIAL PRIMARY KEY,
        tribunal_origen TEXT,
        fecha_sentencia DATE,
        numero_rol TEXT,
        materia TEXT,
        texto_sentencia TEXT,
        fecha_descarga TIMESTAMP DEFAULT NOW(),
        batch_id INTEGER,
        archivo_origen TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    );
    
    -- Crear índices
    CREATE INDEX idx_sentencias_tribunal ON sentencias(tribunal_origen);
    CREATE INDEX idx_sentencias_fecha ON sentencias(fecha_sentencia);
    CREATE INDEX idx_sentencias_rol ON sentencias(numero_rol);
    """)
    print()
    print("5. Configura los GitHub Secrets con las credenciales")

def show_workflow_usage():
    """Muestra cómo usar el workflow"""
    print("🚀 USO DEL WORKFLOW")
    print("=" * 50)
    print()
    print("1. Ve a Actions en tu repositorio")
    print("2. Selecciona 'Descargar y Cargar a Supabase'")
    print("3. Click 'Run workflow'")
    print("4. Configura:")
    print("   - Fecha: YYYY-MM-DD (ej: 2024-01-16)")
    print("   - Cargar a Supabase: ✅ Marcado")
    print("5. Click 'Run workflow'")
    print()
    print("📊 El workflow hará:")
    print("   - Descargar sentencias del día especificado")
    print("   - Procesarlas para Supabase")
    print("   - Cargarlas automáticamente a tu base de datos")
    print("   - Generar un resumen con estadísticas")

def main():
    print("🎯 CONFIGURACIÓN COMPLETA DE SUPABASE + GITHUB")
    print("=" * 60)
    print()
    
    # Mostrar instrucciones de Supabase
    show_supabase_setup()
    print()
    
    # Mostrar instrucciones de GitHub
    generate_github_token()
    print()
    
    # Mostrar uso del workflow
    show_workflow_usage()
    print()
    
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("   Sigue los pasos anteriores para activar la carga automática")

if __name__ == "__main__":
    main()
