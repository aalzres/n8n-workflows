# Subtarea 03: Configuración de Telegram Bot

## Objetivo
Bot de Telegram operativo como canal centralizado de gestión: alertas de sistema, escalado a humano, resúmenes diarios y alertas de límites. Conexión verificada con n8n.

## Dependencias
Ninguna — puede ejecutarse en paralelo con las subtareas 01 y 02.

---

## Pasos

### 1. Crear el bot con @BotFather

1. Abrir Telegram y buscar **@BotFather**
2. Enviar `/newbot`
3. Elegir nombre del bot: `Chatbot Lockers Manager` (nombre visible)
4. Elegir username del bot: `lockers_manager_bot` (debe terminar en `bot`)
5. BotFather responde con el **Bot Token** — Guardarlo de forma segura

> **El Bot Token tiene este formato:** `7123456789:AAH1234abcd5678efgh9012ijkl3456mnop`

### 2. Obtener tu Chat ID personal

El Chat ID es necesario para que n8n sepa a quién enviar las notificaciones.

1. Buscar en Telegram el bot **@userinfobot** (o **@getmyid_bot**)
2. Enviarle cualquier mensaje
3. Responde con tu **Chat ID** — Es un número (ej: `123456789`)
4. Guardarlo

**Alternativa manual:**
1. Enviar cualquier mensaje a tu bot recién creado
2. Ir a: `https://api.telegram.org/bot[TU_BOT_TOKEN]/getUpdates`
3. En el JSON de respuesta, buscar `"chat":{"id": TU_CHAT_ID}`

### 3. Configurar el bot (opcional pero recomendado)

Volver a @BotFather y configurar:

1. `/setdescription` → "Bot de gestión interna del chatbot de lockers. Notificaciones de escalado, alertas y resúmenes."
2. `/setabouttext` → "Gestión interna - No para clientes"
3. `/setuserpic` → Subir un icono/logo

### 4. Definir formato de notificaciones

El bot enviará 4 tipos de notificaciones con formato diferenciado:

**🔴 Alerta de sistema (errores):**
```
🔴 ERROR DE SISTEMA

Tipo: [Tipo de error]
Módulo: [Módulo afectado]
Detalle: [Descripción del error]
Hora: [Timestamp]

⚠️ El bot puede no estar respondiendo a clientes.
```

**🟡 Escalado a humano:**
```
🟡 ESCALADO A HUMANO

Cliente: [Nombre] ([Teléfono])
Intent: [complaint/emergency/otro]
Confidence: [0.XX]
Motivo: [Por qué se escaló]

Últimos mensajes:
- Cliente: [mensaje 1]
- Bot: [respuesta 1]
- Cliente: [mensaje 2]

📱 El cliente ha sido informado de que un agente revisará su caso.
```

**🟢 Resumen diario:**
```
🟢 RESUMEN DIARIO — [Fecha]

📊 Estadísticas:
- Mensajes procesados: [N]
- Conversaciones únicas: [N]
- Resueltas por el bot: [N] ([%])
- Escaladas a humano: [N] ([%])
- Confidence medio: [0.XX]

❓ Top preguntas sin respuesta:
1. [Pregunta más frecuente sin respuesta]
2. [...]

⚠️ Uso de Groq: [N]/30K requests ([%])
```

**⚠️ Alerta de límites:**
```
⚠️ ALERTA DE LÍMITES

Servicio: Groq Free Tier
Uso actual: [N]/30K requests diarios ([%])
Estimación: Se alcanzará el límite en ~[N] horas

💡 Considerar: reducir historial de contexto o activar caché.
```

### 5. Configurar conexión en n8n

1. En n8n → **Credentials → New Credential → Telegram API**
2. Configurar:
   - **Access Token:** El Bot Token de @BotFather
3. Guardar

### 6. Test de envío desde n8n

Crear un workflow temporal de prueba:

1. Nodo **Manual Trigger**
2. Nodo **Telegram** → Acción: Send Message
   - **Chat ID:** Tu Chat ID personal
   - **Text:** `🟢 Test de conexión — Bot de gestión operativo`
3. Ejecutar y verificar que recibes el mensaje en Telegram

### 7. Test de cada tipo de notificación

Crear un workflow de prueba que envíe los 4 tipos de mensaje para verificar el formato:

1. Enviar mensaje tipo 🔴 → Verificar que llega con formato correcto
2. Enviar mensaje tipo 🟡 → Verificar que llega con formato correcto
3. Enviar mensaje tipo 🟢 → Verificar que llega con formato correcto
4. Enviar mensaje tipo ⚠️ → Verificar que llega con formato correcto

### 8. Credenciales a guardar en n8n

| Variable | Valor | Para qué |
|----------|-------|----------|
| `TELEGRAM_BOT_TOKEN` | Token de @BotFather | Autenticación del bot |
| `TELEGRAM_CHAT_ID` | Tu Chat ID personal | Destino de las notificaciones |

---

## Verificación

```
[ ] Bot creado en @BotFather
[ ] Bot Token guardado de forma segura
[ ] Chat ID personal obtenido
[ ] Descripción y foto del bot configuradas
[ ] Credenciales guardadas en n8n
[ ] Test: mensaje de prueba recibido en Telegram desde n8n
[ ] Test: formato 🔴 alerta de sistema verificado
[ ] Test: formato 🟡 escalado a humano verificado
[ ] Test: formato 🟢 resumen diario verificado
[ ] Test: formato ⚠️ alerta de límites verificado
```
