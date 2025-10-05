#!/bin/bash
# Configuración de variables de entorno para GitHub Actions

export GITHUB_REPO="ceo-exltk/descarga-sentencias-pjud"
export SUPABASE_URL="https://wluachczgiyrmrhdpcue.supabase.co"
export SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndsdWFjaGN6Z2l5cm1yaGRwY3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5MjA1NDcsImV4cCI6MjA3MjQ5NjU0N30.gXSqEYy_LFp951EnBhFxU_7RSf5VbJXRc2GlLn7OB7I"

echo "✅ Variables de entorno configuradas"
echo "📝 Repositorio: $GITHUB_REPO"
echo "🗄️ Supabase URL: $SUPABASE_URL"
