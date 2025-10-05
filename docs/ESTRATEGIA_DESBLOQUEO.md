# 🚨 Estrategia de Desbloqueo - Poder Judicial

## 📊 **Estado Actual: BLOQUEADO**

### ❌ **Confirmación del Bloqueo:**
- **Servidor base**: ✅ Responde (HTTP 302)
- **Peticiones de búsqueda**: ❌ Bloqueadas (HTTP 419)
- **Causa**: Exceso de peticiones simultáneas (50+ workers)

## 🕐 **Cronología del Bloqueo:**

1. **Fin de semana**: 50 workers funcionaron correctamente
2. **Lunes 30 Sep**: Bloqueo activado después de intentos masivos
3. **Estado actual**: IP bloqueada para peticiones POST de búsqueda

## 🛠️ **Estrategias de Desbloqueo:**

### **1. ESTRATEGIA DE ESPERA (Recomendada)**
```bash
# Tiempo de espera: 24-48 horas
# Configuración post-desbloqueo:
- Máximo 2 workers simultáneos
- Delay de 30+ segundos entre peticiones
- Solo 1-2 páginas por sesión
- Pausas de 1 hora entre tribunales
```

### **2. ESTRATEGIA DE HORARIOS**
```bash
# Horarios recomendados:
- Madrugada: 2:00 AM - 6:00 AM
- Fines de semana: Sábado-Domingo
- Días festivos: Menor tráfico del servidor
```

### **3. ESTRATEGIA DE IP DIFERENTE**
```bash
# Opciones de cambio de IP:
- VPN con ubicación diferente
- Proxy rotativo
- Cambio de red (móvil vs WiFi)
- Usar servidor en la nube
```

### **4. ESTRATEGIA DE CONTACTO OFICIAL**
```bash
# Contactar al Poder Judicial:
- Email: info@pjud.cl
- Explicar propósito académico/investigativo
- Solicitar límites específicos de rate limiting
- Proponer colaboración técnica
```

## 📋 **Plan de Acción Inmediato:**

### **Paso 1: Verificar Estado (Cada 6 horas)**
```bash
curl -X POST "https://juris.pjud.cl/busqueda?Corte_Suprema" \
  -d "pagina=1&cantidad_registros=10&corte_suprema=true" \
  -s -o /dev/null -w "HTTP Status: %{http_code}\n"
```

### **Paso 2: Configuración Ultra-Conservadora (Cuando se desbloquee)**
```python
# Parámetros seguros:
max_workers = 2
delay_between_requests = 30  # 30 segundos
max_pages_per_session = 1
pause_between_tribunals = 3600  # 1 hora
max_requests_per_hour = 10
```

### **Paso 3: Monitoreo Continuo**
```python
# Sistema de monitoreo:
- Verificar cada petición
- Detener inmediatamente si hay error 419
- Implementar backoff exponencial
- Logs detallados de cada intento
```

## ⚠️ **Consideraciones Importantes:**

### **Riesgos:**
- Bloqueo permanente si continuamos agresivamente
- Pérdida total de acceso al sistema
- Necesidad de cambiar infraestructura completa

### **Alternativas:**
1. **API Oficial**: Buscar si existe API pública
2. **Scraping Distribuido**: Múltiples IPs/proxies
3. **Descarga Manual**: Proceso más lento pero seguro
4. **Colaboración Oficial**: Contactar al Poder Judicial

## 🎯 **Recomendación Final:**

**ESPERAR 24-48 HORAS** y luego usar configuración ultra-conservadora con máximo 2 workers.

### **Configuración Segura para Reintento:**
```python
# Sistema ultra-conservador:
- 2 workers máximo
- 30 segundos entre peticiones
- 1 página por sesión
- 1 hora entre tribunales
- Monitoreo constante de errores 419
```

---

**⚠️ IMPORTANTE: No intentar descarga masiva hasta confirmar que el bloqueo se ha levantado completamente.**







