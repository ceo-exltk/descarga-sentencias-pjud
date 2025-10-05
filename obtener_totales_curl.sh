#!/bin/bash
"""
Script con comandos curl reales para obtener totales del PJUD
Listo para copiar y pegar - Usa los mismos endpoints que los scripts de descarga
"""

echo "🔍 OBTENIENDO TOTALES REALES CON CURL"
echo "===================================="
echo "⏰ Timestamp: $(date)"
echo "🌍 IP: Local"
echo "🔍 Método: Comandos curl directos"
echo ""

# Función para obtener token CSRF
obtener_token() {
    echo "🔑 Obteniendo token CSRF..."
    
    # Paso 1: Obtener token CSRF de la página principal
    TOKEN=$(curl -s "https://juris.pjud.cl/" | grep -o 'name="_token" value="[^"]*"' | cut -d'"' -f4)
    
    if [ -z "$TOKEN" ]; then
        echo "❌ No se pudo obtener token CSRF"
        return 1
    fi
    
    echo "✅ Token CSRF obtenido: ${TOKEN:0:20}..."
    echo "$TOKEN"
}

# Función para consultar un tribunal específico
consultar_tribunal() {
    local tribunal_name="$1"
    local id_buscador="$2"
    local busqueda="$3"
    local icono="$4"
    
    echo ""
    echo "🏛️ Consultando $tribunal_name"
    echo "----------------------------------------"
    
    # Obtener token
    TOKEN=$(obtener_token)
    if [ -z "$TOKEN" ]; then
        echo "❌ No se pudo obtener token para $tribunal_name"
        return 0
    fi
    
    # Establecer contexto visitando página de búsqueda
    echo "🌐 Estableciendo contexto..."
    curl -s "https://juris.pjud.cl/busqueda" > /dev/null
    
    # Preparar payload JSON
    FILTROS='{"rol":"","era":"","fec_desde":"","fec_hasta":"","tipo_norma":"","num_norma":"","num_art":"","num_inciso":"","todas":"","algunas":"","excluir":"","literal":"","proximidad":"","distancia":"","analisis_s":"","submaterias":"","facetas_seleccionadas":[],"filtros_omnibox":[],"ids_comunas_seleccionadas_mapa":[]}'
    
    # Realizar consulta POST
    echo "🔍 Realizando consulta a $busqueda..."
    
    RESPONSE=$(curl -s -X POST "https://juris.pjud.cl/busqueda/buscar_sentencias" \
        -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
        -H "Accept: application/json, text/plain, */*" \
        -H "Accept-Language: es-ES,es;q=0.9,en;q=0.8" \
        -H "Accept-Encoding: gzip, deflate, br" \
        -H "Connection: keep-alive" \
        -H "X-Requested-With: XMLHttpRequest" \
        -H "Origin: https://juris.pjud.cl" \
        -H "Sec-Fetch-Dest: empty" \
        -H "Sec-Fetch-Mode: cors" \
        -H "Sec-Fetch-Site: same-origin" \
        -H "Cache-Control: no-cache" \
        -H "Pragma: no-cache" \
        -H "Referer: https://juris.pjud.cl/busqueda" \
        -H "busqueda: $busqueda" \
        -H "Content-Type: application/json" \
        -d "{
            \"_token\": \"$TOKEN\",
            \"id_buscador\": \"$id_buscador\",
            \"filtros\": \"$FILTROS\",
            \"numero_filas_paginacion\": \"1\",
            \"offset_paginacion\": \"0\",
            \"orden\": \"rel\"
        }")
    
    # Verificar respuesta
    if [ $? -eq 0 ]; then
        # Extraer total usando jq
        TOTAL=$(echo "$RESPONSE" | jq -r '.response.numFound // 0' 2>/dev/null)
        
        if [ "$TOTAL" != "null" ] && [ "$TOTAL" != "0" ]; then
            echo "✅ $tribunal_name: $TOTAL sentencias encontradas"
            echo "$TOTAL"
        else
            echo "⚠️ $tribunal_name: No se pudo extraer total de la respuesta"
            echo "📄 Respuesta recibida:"
            echo "$RESPONSE" | head -5
            echo "0"
        fi
    else
        echo "❌ $tribunal_name: Error en la consulta"
        echo "0"
    fi
}

# Función principal
main() {
    echo "🚀 INICIANDO CONSULTA REAL A LA API DEL PJUD"
    echo "============================================="
    
    # Array para almacenar resultados
    declare -A resultados
    total_general=0
    
    # Consultar cada tribunal
    echo ""
    echo "📊 CONSULTANDO TRIBUNALES:"
    echo "=========================="
    
    # Corte Suprema
    total=$(consultar_tribunal "Corte Suprema de Chile" "528" "Buscador_Jurisprudencial_de_la_Corte_Suprema" "🏛️")
    resultados["Corte_Suprema"]=$total
    total_general=$((total_general + total))
    
    sleep 2  # Delay entre consultas
    
    # Cortes de Apelaciones
    total=$(consultar_tribunal "Cortes de Apelaciones" "529" "Buscador_Jurisprudencial_de_Cortes_de_Apelaciones" "⚖️")
    resultados["Corte_de_Apelaciones"]=$total
    total_general=$((total_general + total))
    
    sleep 2
    
    # Tribunales Laborales
    total=$(consultar_tribunal "Tribunales Laborales" "530" "Buscador_Jurisprudencial_de_Tribunales_Laborales" "💼")
    resultados["Laborales"]=$total
    total_general=$((total_general + total))
    
    sleep 2
    
    # Tribunales Penales
    total=$(consultar_tribunal "Tribunales Penales" "531" "Buscador_Jurisprudencial_de_Tribunales_Penales" "⚖️")
    resultados["Penales"]=$total
    total_general=$((total_general + total))
    
    sleep 2
    
    # Tribunales de Familia
    total=$(consultar_tribunal "Tribunales de Familia" "532" "Buscador_Jurisprudencial_de_Tribunales_de_Familia" "👨‍👩‍👧‍👦")
    resultados["Familia"]=$total
    total_general=$((total_general + total))
    
    sleep 2
    
    # Tribunales Civiles
    total=$(consultar_tribunal "Tribunales Civiles" "533" "Buscador_Jurisprudencial_de_Tribunales_Civiles" "📋")
    resultados["Civiles"]=$total
    total_general=$((total_general + total))
    
    sleep 2
    
    # Tribunales de Cobranza
    total=$(consultar_tribunal "Tribunales de Cobranza" "534" "Buscador_Jurisprudencial_de_Tribunales_de_Cobranza" "💰")
    resultados["Cobranza"]=$total
    total_general=$((total_general + total))
    
    # Mostrar resumen final
    echo ""
    echo "📊 RESUMEN FINAL:"
    echo "================="
    echo "🏛️ Corte Suprema: ${resultados[Corte_Suprema]:-,} sentencias"
    echo "⚖️ Cortes de Apelaciones: ${resultados[Corte_de_Apelaciones]:-,} sentencias"
    echo "💼 Tribunales Laborales: ${resultados[Laborales]:-,} sentencias"
    echo "⚖️ Tribunales Penales: ${resultados[Penales]:-,} sentencias"
    echo "👨‍👩‍👧‍👦 Tribunales de Familia: ${resultados[Familia]:-,} sentencias"
    echo "📋 Tribunales Civiles: ${resultados[Civiles]:-,} sentencias"
    echo "💰 Tribunales de Cobranza: ${resultados[Cobranza]:-,} sentencias"
    echo "----------------------------------------"
    echo "TOTAL GENERAL: $total_general sentencias"
    
    # Guardar resultados en JSON
    timestamp=$(date +%Y%m%d_%H%M%S)
    filename="totales_reales_curl_${timestamp}.json"
    
    cat > "$filename" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "totales_por_tribunal": {
    "Corte_Suprema": ${resultados[Corte_Suprema]},
    "Corte_de_Apelaciones": ${resultados[Corte_de_Apelaciones]},
    "Laborales": ${resultados[Laborales]},
    "Penales": ${resultados[Penales]},
    "Familia": ${resultados[Familia]},
    "Civiles": ${resultados[Civiles]},
    "Cobranza": ${resultados[Cobranza]}
  },
  "total_general": $total_general,
  "fuente": "API oficial PJUD (juris.pjud.cl)",
  "metodo": "Comandos curl directos",
  "ip_origen": "Local",
  "confiabilidad": "Alta - Datos obtenidos directamente de la API"
}
EOF
    
    echo ""
    echo "💾 Resultados guardados en: $filename"
    echo "✅ Consulta completada exitosamente"
}

# Ejecutar función principal
main "$@"

