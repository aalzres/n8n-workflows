# Subtarea 04: Configuración de Uptime Kuma

## Objetivo
Sistema de vigilancia externa que monitoriza n8n de forma independiente y alerta por Telegram si se cae.

## Dependencias
- **Subtarea 03** — Bot de Telegram debe estar creado (se necesita el Bot Token y Chat ID para las alertas).

---

## Pasos

### 1. Instalar Uptime Kuma con Docker

> **Importante:** Uptime Kuma debe correr como contenedor Docker SEPARADO de n8n. Si corre en el mismo contenedor y n8n se cae, Uptime Kuma también caería.

**En el mismo servidor que n8n (contenedor separado):**

```bash
docker run -d \
  --restart=always \
  --name uptime-kuma \
  -p 3001:3001 \
  -v uptime-kuma:/app/data \
  louislam/uptime-kuma:latest
```

**En un servidor diferente (más seguro, cubre caída total del servidor):**

Misma instalación pero en otro VPS. Opción recomendada si tienes un segundo servidor disponible.

### 2. Acceder al panel

1. Abrir navegador: `http://[IP-DEL-SERVIDOR]:3001`
2. Primera vez: crear cuenta de administrador
   - **Username:** admin (o el que prefieras)
   - **Password:** Contraseña segura
3. Guardar credenciales

### 3. Configurar monitor para n8n

1. Clic en **Add New Monitor**
2. Configurar:
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** `n8n - Chatbot Lockers`
   - **URL:** `https://[tu-dominio-n8n]/healthz` (o la URL base de n8n)
   - **Heartbeat Interval:** `60` (cada 60 segundos)
   - **Retries:** `3` (3 intentos antes de marcar como caído)
   - **Accepted Status Codes:** `200-299`
3. Guardar

**Si n8n no tiene endpoint /healthz:**

Usar la URL base de n8n o crear un webhook específico de health check:
- Crear un workflow en n8n con un **Webhook** en `/health` que responda `{"status": "ok"}`
- Usar esa URL como monitor: `https://[tu-dominio-n8n]/webhook/health`

### 4. Configurar monitor para el webhook de WhatsApp

Opcional pero recomendado — verifica que el endpoint específico del webhook está respondiendo:

1. **Add New Monitor**
2. Configurar:
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** `Webhook WhatsApp`
   - **URL:** `https://[tu-dominio-n8n]/webhook/whatsapp`
   - **Heartbeat Interval:** `120` (cada 2 minutos)
   - **Accepted Status Codes:** `200-299`

### 5. Configurar alertas por Telegram

1. Ir a **Settings → Notifications**
2. Clic en **Setup Notification**
3. Seleccionar tipo: **Telegram**
4. Configurar:
   - **Bot Token:** El mismo Bot Token de @BotFather (de la subtarea 03)
   - **Chat ID:** Tu Chat ID personal (de la subtarea 03)
5. Clic en **Test** para verificar que llega la notificación
6. Guardar

### 6. Asignar notificación a los monitores

1. Ir a cada monitor creado
2. En la sección **Notifications**, activar la notificación de Telegram
3. Configurar:
   - **Notify when down:** ✅ Sí
   - **Notify when up:** ✅ Sí (para saber cuándo se recupera)

### 7. Configurar Status Page (opcional)

Uptime Kuma permite crear una página pública de estado:

1. Ir a **Status Pages → New Status Page**
2. Añadir los monitores
3. Esto genera una URL pública donde puedes ver el estado en tiempo real

### 8. Seguridad

- Cambiar el puerto por defecto si es accesible desde internet
- Configurar proxy reverso (nginx/Caddy) con HTTPS si vas a acceder remotamente
- Si solo accedes desde la red local, limitar el acceso por IP

---

## Verificación

```
[ ] Uptime Kuma instalado como contenedor Docker separado
[ ] Panel accesible en el navegador
[ ] Cuenta de administrador creada
[ ] Monitor de n8n configurado y funcionando (status: UP)
[ ] Monitor de webhook de WhatsApp configurado (opcional)
[ ] Notificación de Telegram configurada y testeada
[ ] Alertas asignadas a los monitores (down + up)
[ ] Test: parar n8n temporalmente → verificar que llega alerta a Telegram
[ ] Test: reiniciar n8n → verificar que llega notificación de recuperación
```
