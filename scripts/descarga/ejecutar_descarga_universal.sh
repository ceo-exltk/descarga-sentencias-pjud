#!/bin/bash

# Script de Ejecución Rápida para Descarga Universal de Sentencias
# Sistema optimizado con workers máximos para descarga completa

echo "🌍 SISTEMA DE DESCARGA UNIVERSAL DE SENTENCIAS"
echo "=============================================="
echo "Descarga completa de todos los tribunales del Poder Judicial"
echo "Con workers máximos y procesamiento optimizado de fechas"
echo "=============================================="

# Verificar que Python 3 esté disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Instalando..."
    if command -v brew &> /dev/null; then
        brew install python3
    else
        echo "❌ Por favor instale Python 3 manualmente"
        exit 1
    fi
fi

# Verificar que pip esté disponible
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 no está disponible. Instalando..."
    python3 -m ensurepip --upgrade
fi

# Instalar dependencias si es necesario
echo "📦 Verificando dependencias..."
python3 -c "import requests" 2>/dev/null || pip3 install requests

# Crear directorio de salida
mkdir -p output/descarga_universal_completa

# Hacer ejecutables los scripts
chmod +x *.py

echo ""
echo "🚀 OPCIONES DE EJECUCIÓN:"
echo "1. ⚙️  Configurar descarga (recomendado para primera vez)"
echo "2. 🚀 Ejecutar descarga con configuración por defecto"
echo "3. 📊 Solo monitorear descarga en progreso"
echo "4. ❌ Salir"
echo ""

read -p "Seleccione una opción (1-4): " opcion

case $opcion in
    1)
        echo "⚙️  Iniciando configurador..."
        python3 configurar_descarga_universal.py
        ;;
    2)
        echo "🚀 Iniciando descarga universal..."
        echo "⚠️  ADVERTENCIA: Esta operación puede tomar varias horas"
        echo "💡 Se recomienda ejecutar en una terminal separada y usar el monitor"
        echo ""
        read -p "¿Continuar? (s/n): " confirmar
        if [[ $confirmar == "s" || $confirmar == "S" ]]; then
            # Ejecutar en background
            nohup python3 descarga_universal_completa.py > descarga_universal.log 2>&1 &
            echo "✅ Descarga iniciada en background"
            echo "📊 Use 'python3 monitor_descarga_universal.py' para monitorear"
            echo "📄 Logs disponibles en 'descarga_universal.log'"
        else
            echo "❌ Descarga cancelada"
        fi
        ;;
    3)
        echo "📊 Iniciando monitor..."
        python3 monitor_descarga_universal.py
        ;;
    4)
        echo "👋 ¡Hasta luego!"
        exit 0
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo ""
echo "🎉 Proceso completado"
echo "📁 Archivos guardados en: output/descarga_universal_completa/"
echo "📄 Logs disponibles en: descarga_universal.log"







