# 🔐 Configuración de GitHub Secrets

## 📋 **Pasos para Configurar Secretos**

### **1. Acceder a la Configuración**

1. Ve a tu repositorio: `https://github.com/ceo-exltk/descarga-sentencias-pjud`
2. Click en **Settings** (pestaña superior)
3. En el menú lateral, click en **Secrets and variables** → **Actions**

### **2. Agregar Secretos**

Click en **"New repository secret"** y agrega:

#### **SUPABASE_URL**
```
Name: SUPABASE_URL
Value: https://wluachczgiyrmrhdpcue.supabase.co
```

#### **SUPABASE_ANON_KEY**
```
Name: SUPABASE_ANON_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndsdWFjaGN6Z2l5cm1yaGRwY3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5MjA1NDcsImV4cCI6MjA3MjQ5NjU0N30.gXSqEYy_LFp951EnBhFxU_7RSf5VbJXRc2GlLn7OB7I
```

### **3. Verificar Configuración**

Los secretos deben aparecer en la lista como:
- ✅ SUPABASE_URL
- ✅ SUPABASE_ANON_KEY

### **4. Probar Configuración**

```bash
# Ejecutar verificación
python3 verificar_configuracion.py
```

## ⚠️ **Importante**

- Los secretos son **sensibles** - no los compartas
- Los secretos se usan **automáticamente** en los workflows
- Si cambias las credenciales, actualiza los secretos aquí

## 🔧 **Troubleshooting**

### **❌ Error: "Secret not found"**
- Verificar que el nombre sea exacto: `SUPABASE_URL` y `SUPABASE_ANON_KEY`
- Verificar que estén en la sección correcta: **Actions** (no Codespaces)

### **❌ Error: "Invalid credentials"**
- Verificar que los valores sean correctos
- Verificar que no haya espacios extra
- Verificar que la URL empiece con `https://`
