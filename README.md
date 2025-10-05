# 📊 Dashboard de Completitud - Sentencias PJUD

Sistema de monitoreo en tiempo real del progreso de descarga de sentencias del Poder Judicial de Chile.

## 🌐 Dashboard en Vivo

**URL del Dashboard:** https://ceo-exltk.github.io/descarga-sentencias-pjud/

## 📊 Datos en Tiempo Real

- **Total Real:** 4,115,881 sentencias (obtenido de API oficial PJUD)
- **Actualización:** Cada 6 horas automáticamente
- **Fuente:** API oficial del Poder Judicial de Chile

### 🏛️ Totales por Tribunal

| Tribunal | Total Real | Descargado | Completitud |
|----------|------------|------------|-------------|
| Corte Suprema | 261,871 | 0 | 0% |
| Corte de Apelaciones | 1,510,429 | 0 | 0% |
| Laborales | 233,904 | 0 | 0% |
| Penales | 862,269 | 0 | 0% |
| Familia | 371,320 | 0 | 0% |
| Civiles | 849,956 | 0 | 0% |
| Cobranza | 26,132 | 0 | 0% |

## 🚀 Características

- ✅ **Datos en Tiempo Real:** Obtenidos directamente de la API oficial PJUD
- ⚡ **Ejecución Paralela:** 7x más rápido que ejecución secuencial
- 🤖 **Actualización Automática:** GitHub Actions cada 6 horas
- 📈 **Dashboard Interactivo:** Diseño moderno y responsive
- 🔄 **Auto-refresh:** Actualización cada 30 segundos

## 🔧 Tecnologías

- **Frontend:** HTML5, CSS3, JavaScript
- **Backend:** Python, Requests
- **Deploy:** GitHub Pages + GitHub Actions
- **API:** Poder Judicial de Chile (juris.pjud.cl)

## 📁 Archivos Clave

- `dashboard_paralelo.py` - Script principal de obtención de datos
- `docs/index.html` - Dashboard web interactivo
- `docs/dashboard_data.json` - Datos en tiempo real
- `.github/workflows/` - Configuración de GitHub Actions

## 🎯 Objetivo

Monitorear el progreso de descarga de sentencias para garantizar la completitud del sistema de descarga masiva del Poder Judicial de Chile.

---

**Desarrollado con ❤️ para el acceso a la justicia**