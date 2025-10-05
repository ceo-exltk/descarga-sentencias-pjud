#!/usr/bin/env python3
"""
Script para configurar las variables de Supabase en GitHub
"""

import os
import sys

def mostrar_instrucciones():
    """Muestra las instrucciones para configurar Supabase"""
    
    print("🔧 CONFIGURACIÓN DE SUPABASE PARA GITHUB ACTIONS")
    print("=" * 60)
    print()
    print("Para habilitar la carga automática a Supabase, necesitas configurar")
    print("los siguientes secrets en tu repositorio de GitHub:")
    print()
    print("📋 SECRETS REQUERIDOS:")
    print("   1. SUPABASE_URL")
    print("   2. SUPABASE_ANON_KEY")
    print()
    print("🔗 CÓMO CONFIGURAR:")
    print("   1. Ve a tu repositorio en GitHub")
    print("   2. Settings → Secrets and variables → Actions")
    print("   3. Click 'New repository secret'")
    print("   4. Agrega cada secret:")
    print()
    print("   SUPABASE_URL:")
    print("   - Valor: https://tu-proyecto.supabase.co")
    print("   - Ejemplo: https://abcdefghijklmnop.supabase.co")
    print()
    print("   SUPABASE_ANON_KEY:")
    print("   - Valor: Tu anon key de Supabase")
    print("   - Encuéntralo en: Supabase Dashboard → Settings → API")
    print()
    print("📊 ESTRUCTURA DE TABLA RECOMENDADA:")
    print("   Tabla: sentencias")
    print("   Campos:")
    print("   - id (serial, primary key)")
    print("   - tribunal_origen (text)")
    print("   - fecha_sentencia (date)")
    print("   - numero_rol (text)")
    print("   - materia (text)")
    print("   - texto_sentencia (text)")
    print("   - fecha_descarga (timestamp)")
    print("   - batch_id (integer)")
    print("   - archivo_origen (text)")
    print()
    print("🚀 USO DEL WORKFLOW:")
    print("   1. Configura los secrets")
    print("   2. Ve a Actions → 'Descargar y Cargar a Supabase'")
    print("   3. Click 'Run workflow'")
    print("   4. Ingresa la fecha deseada")
    print("   5. Marca 'Cargar a Supabase' si quieres carga automática")
    print()
    print("✅ Una vez configurado, el workflow:")
    print("   - Descargará las sentencias del día especificado")
    print("   - Las procesará para Supabase")
    print("   - Las cargará automáticamente a tu base de datos")
    print("   - Generará un resumen con estadísticas")

def verificar_configuracion():
    """Verifica si la configuración está completa"""
    
    print("🔍 VERIFICANDO CONFIGURACIÓN...")
    print()
    
    # Verificar si estamos en GitHub Actions
    if os.getenv('GITHUB_ACTIONS'):
        print("✅ Ejecutándose en GitHub Actions")
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if supabase_url and supabase_key:
            print("✅ Variables de Supabase configuradas")
            print(f"   URL: {supabase_url}")
            print(f"   Key: {supabase_key[:10]}...")
            return True
        else:
            print("❌ Variables de Supabase no configuradas")
            print("   Configura SUPABASE_URL y SUPABASE_ANON_KEY en GitHub Secrets")
            return False
    else:
        print("ℹ️  Ejecutándose localmente")
        print("   Para probar localmente, configura las variables de entorno:")
        print("   export SUPABASE_URL='https://tu-proyecto.supabase.co'")
        print("   export SUPABASE_ANON_KEY='tu-anon-key'")
        return False

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--verificar':
        return verificar_configuracion()
    else:
        mostrar_instrucciones()
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
