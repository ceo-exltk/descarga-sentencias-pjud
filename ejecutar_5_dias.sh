#!/bin/bash

# Script de inicio para descarga del universo completo durante 5 días
# Uso: ./ejecutar_5_dias.sh

echo "🌍 DESCARGA UNIVERSO COMPLETO - 5 DÍAS"
echo "======================================"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "iniciar_descarga_5_dias.py" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio del proyecto"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 no está instalado"
    exit 1
fi

# Crear directorio de output si no existe
mkdir -p output/universo_completo/logs

# Hacer archivos ejecutables
chmod +x iniciar_descarga_5_dias.py
chmod +x descarga_universo_completo.py
chmod +x monitor_descarga_universo.py
chmod +x scheduler_5_dias.py
chmod +x recuperar_descarga.py

echo "✅ Verificaciones completadas"
echo ""

# Ejecutar script principal
python3 iniciar_descarga_5_dias.py
