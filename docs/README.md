# 📊 Dashboard de Descarga de Sentencias PJUD

Dashboard en tiempo real para el sistema de descarga masiva de sentencias del Poder Judicial de Chile.

## 🎯 Características

- **Totales reales**: 4,115,881 sentencias distribuidas en 7 tribunales
- **Datos oficiales**: Obtenidos directamente de la API del PJUD
- **Actualización automática**: Dashboard se actualiza cada 30 segundos
- **Análisis de completitud**: Métricas de calidad de datos por tribunal

## 📈 Estadísticas Actuales

| Tribunal | Total Sentencias |
|----------|------------------|
| Corte Suprema | 261,871 |
| Corte de Apelaciones | 1,510,429 |
| Laborales | 233,904 |
| Penales | 862,269 |
| Familia | 371,320 |
| Civiles | 849,956 |
| Cobranza | 26,132 |
| **TOTAL** | **4,115,881** |

## 🚀 Acceso al Dashboard

El dashboard está disponible en: [Ver Dashboard](https://alexispena.github.io/descarga_sentencias/)

## 🔧 Tecnologías

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Python, Supabase
- **Deployment**: GitHub Pages
- **Datos**: API oficial PJUD (juris.pjud.cl)

## 📊 Fuente de Datos

Los totales son obtenidos directamente de la API oficial del Poder Judicial de Chile usando:

- **Endpoint**: `https://juris.pjud.cl/busqueda/buscar_sentencias`
- **Método**: POST con IDs de buscador corregidos
- **Autenticación**: Token CSRF + cookies de sesión
- **Frecuencia**: Actualización en tiempo real

## 🛠️ Desarrollo

Para ejecutar localmente:

```bash
# Clonar repositorio
git clone https://github.com/alexispena/descarga_sentencias.git
cd descarga_sentencias

# Actualizar dashboard
python3 actualizar_dashboard.py

# Servir localmente
cd docs
python3 -m http.server 8000
```

## 📝 Licencia

Este proyecto está desarrollado para facilitar el acceso a la información judicial pública en Chile.

---

**Desarrollado con ❤️ para el acceso a la justicia**
