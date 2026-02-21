# Subtarea 06: Workflow Core en n8n (Módulos 1-4)

## Objetivo
Workflow principal operativo en n8n: recibe mensaje de WhatsApp → procesa → genera respuesta con IA → envía respuesta → guarda en BD.

## Dependencias
- **Subtarea 01** — Supabase operativa con tablas creadas
- **Subtarea 02** — Meta WhatsApp API configurada y webhook activo
- **Subtarea 05** — System prompt redactado y probado

---

## Estructura del Workflow

```
[Webhook] → [Módulo 1: Preprocesamiento] → [Módulo 2: Estado y Contexto] 
→ [Módulo 3: Generación de Respuesta] → [Módulo 4: Post-procesamiento y Envío]
```

---

## Pasos

### Módulo 1: Recepción y Preprocesamiento

**Nodos a crear:**

| # | Tipo de nodo | Nombre | Función |
|---|-------------|--------|---------|
| 1 | Webhook | `WhatsApp Webhook` | Recibe POST de Meta Cloud API |
| 2 | Code | `Extraer Datos` | Parsea el payload y extrae campos |
| 3 | IF | `¿Es texto o audio?` | Bifurca según tipo de mensaje |
| 4 | HTTP Request | `Descargar Audio` | Descarga el archivo de audio de Meta (rama audio) |
| 5 | HTTP Request | `Groq Whisper` | Transcribe audio a texto (rama audio) |
| 6 | HTTP Request | `Responder No Soportado` | Responde al cliente que solo procesa texto y audio (rama otros) |

**Configuración del Webhook:**

- **Path:** `/whatsapp`
- **HTTP Method:** POST
- **Response Code:** 200
- **Response Mode:** Immediately (Meta requiere respuesta rápida, si no reintenta)

**Datos a extraer del payload de Meta (nodo Code):**

| Campo | Path en el payload |
|-------|-------------------|
| `clientPhone` | `body.entry[0].changes[0].value.messages[0].from` |
| `messageText` | `body.entry[0].changes[0].value.messages[0].text.body` |
| `messageType` | `body.entry[0].changes[0].value.messages[0].type` |
| `timestamp` | `body.entry[0].changes[0].value.messages[0].timestamp` |
| `clientName` | `body.entry[0].changes[0].value.contacts[0].profile.name` |
| `mediaId` | `body.entry[0].changes[0].value.messages[0].audio.id` (solo si es audio) |

**Lógica del IF:**

- Si `messageType === 'text'` → continúa al Módulo 2 con `messageText`
- Si `messageType === 'audio'` → descarga audio → Whisper → continúa al Módulo 2 con texto transcrito
- Si otro tipo → responde al cliente que solo procesa texto y audio

**Configuración de Groq Whisper (HTTP Request):**

- **URL:** `https://api.groq.com/openai/v1/audio/transcriptions`
- **Método:** POST
- **Headers:** `Authorization: Bearer [GROQ_API_KEY]`
- **Body type:** Form-Data/Multipart
  - `file`: el archivo de audio descargado
  - `model`: `whisper-large-v3-turbo`
  - `language`: `es` (o vacío para detección automática)

---

### Módulo 2: Estado y Contexto

**Nodos a crear:**

| # | Tipo de nodo | Nombre | Función |
|---|-------------|--------|---------|
| 1 | Postgres | `Consultar Estado` | SELECT de conversation_state por clientPhone |
| 2 | IF | `¿Human Takeover?` | Verifica si status = 'human' |
| 3 | Postgres | `Obtener Historial` | SELECT últimos 20 mensajes de conversations |
| 4 | Code | `Construir Mensajes` | Arma el array {role, content} para la API de IA |

**Lógica de Human Takeover:**

- Si `status = 'human'` → NO responder (un humano gestiona esta conversación) → FIN
- Si `status = 'bot'` o no existe registro → continúa normalmente
- Si no existe registro en conversation_state → crear uno nuevo con status='bot'

**Gestión de expiración de conversación:**

- Si `last_interaction` tiene más de 6 horas de antigüedad → tratar como conversación nueva
- Resetear `current_intent` a null
- Esto evita arrastrar contexto viejo irrelevante

**Construcción del array de mensajes:**

El array debe tener este formato (es lo que esperan las APIs de Groq y Anthropic):

```
[
    {"role": "user", "content": "mensaje antiguo del cliente"},
    {"role": "assistant", "content": "respuesta antigua del bot"},
    {"role": "user", "content": "mensaje actual del cliente"}
]
```

Ordenado cronológicamente (del más antiguo al más reciente). Últimos 20 mensajes máximo.

---

### Módulo 3: Generación de Respuesta con IA

**Nodos a crear:**

| # | Tipo de nodo | Nombre | Función |
|---|-------------|--------|---------|
| 1 | Code | `Preparar Body Groq` | Construye el JSON para la API de Groq |
| 2 | HTTP Request | `Llamada a Groq` | POST a Groq API |
| 3 | Code | `Parsear Respuesta` | Extrae JSON de la respuesta |
| 4 | IF | `¿Necesita Fallback?` | Evalúa confidence e intent |
| 5 | Code | `Preparar Body Claude` | Construye el JSON para Anthropic (rama fallback) |
| 6 | HTTP Request | `Llamada a Claude` | POST a Anthropic API (rama fallback) |
| 7 | Code | `Parsear Respuesta Claude` | Extrae JSON de la respuesta de Claude (rama fallback) |

**Configuración de la llamada a Groq (HTTP Request):**

- **URL:** `https://api.groq.com/openai/v1/chat/completions`
- **Método:** POST
- **Headers:**
  - `Authorization`: `Bearer [GROQ_API_KEY]`
  - `Content-Type`: `application/json`
- **Body:**
  - `model`: `meta-llama/llama-4-scout-17b-16e-instruct`
  - `messages`: [{"role": "system", "content": "[SYSTEM_PROMPT]"}, ...historial]
  - `max_tokens`: 500
  - `temperature`: 0.3 (baja para respuestas más consistentes)

**Configuración de la llamada a Claude Sonnet (HTTP Request — rama fallback):**

- **URL:** `https://api.anthropic.com/v1/messages`
- **Método:** POST
- **Headers:**
  - `x-api-key`: `[ANTHROPIC_API_KEY]`
  - `anthropic-version`: `2023-06-01`
  - `Content-Type`: `application/json`
- **Body:**
  - `model`: `claude-sonnet-4-20250514`
  - `system`: `[SYSTEM_PROMPT]`
  - `messages`: [...historial]
  - `max_tokens`: 500

**Lógica del IF para fallback:**

- Si `confidence < 0.7` → fallback a Claude
- Si `intent === 'complaint'` → fallback a Claude
- Si `intent === 'emergency'` → fallback a Claude
- Si el JSON de Groq no es válido → fallback a Claude
- En cualquier otro caso → usar respuesta de Groq

**Error handling:**

- Si Groq no responde (timeout 10s) → intentar Claude directamente
- Si Claude tampoco responde (timeout 15s) → enviar mensaje genérico al cliente: "Estamos teniendo problemas técnicos, un agente te atenderá pronto" + escalar + alerta 🔴 a Telegram
- Configurar **Retry on Fail** en ambos HTTP Request: 1 reintento con 2s de espera

---

### Módulo 4: Post-procesamiento y Envío

**Nodos a crear:**

| # | Tipo de nodo | Nombre | Función |
|---|-------------|--------|---------|
| 1 | Code | `Procesar Respuesta` | Extrae responseText, intent, escalate, confidence del JSON |
| 2 | IF | `¿Escalar?` | Evalúa si necesita escalado a humano |
| 3 | Telegram | `Notificar Escalado` | Envía 🟡 a Telegram (rama escalado) |
| 4 | Postgres | `Marcar Human Takeover` | UPDATE status='human' en conversation_state (rama escalado) |
| 5 | HTTP Request | `Enviar WhatsApp` | POST a Meta API para enviar respuesta al cliente |
| 6 | Postgres | `Guardar Mensaje Cliente` | INSERT en conversations (role='user') |
| 7 | Postgres | `Guardar Respuesta Bot` | INSERT en conversations (role='assistant') |
| 8 | Postgres | `Actualizar Estado` | UPDATE conversation_state (intent, last_interaction) |

**Configuración del envío por WhatsApp (HTTP Request):**

- **URL:** `https://graph.facebook.com/v21.0/[PHONE_NUMBER_ID]/messages`
- **Método:** POST
- **Headers:**
  - `Authorization`: `Bearer [META_ACCESS_TOKEN]`
  - `Content-Type`: `application/json`
- **Body:**
  - `messaging_product`: `whatsapp`
  - `to`: `[clientPhone]`
  - `type`: `text`
  - `text.body`: `[responseText del JSON del modelo]`

**Orden de guardado en BD:**

1. Primero guardar el mensaje del cliente (role='user')
2. Luego guardar la respuesta del bot (role='assistant')
3. Actualizar conversation_state con el intent actual y timestamp

**Notificación de escalado a Telegram (formato 🟡):**

Incluir en el mensaje:
- Nombre y teléfono del cliente
- Intent detectado
- Confidence
- Últimos 3-5 mensajes de la conversación
- Motivo del escalado

---

## Error Handling General

Añadir un **Error Workflow** en n8n que capture cualquier error no manejado:

1. En n8n → **Settings → Error Workflow**
2. Crear un workflow de error que:
   - Reciba el error
   - Envíe alerta 🔴 a Telegram con el detalle del error
   - Si es posible, envíe mensaje genérico al cliente por WhatsApp

---

## Verificación

```
[ ] Módulo 1: Webhook recibe mensajes de Meta correctamente
[ ] Módulo 1: Extracción de datos funciona (todos los campos)
[ ] Módulo 1: IF texto/audio/otro bifurca correctamente
[ ] Módulo 1: Transcripción con Whisper funciona
[ ] Módulo 1: Mensaje "solo texto y audio" se envía para otros tipos
[ ] Módulo 2: Consulta de conversation_state funciona
[ ] Módulo 2: Human takeover bloquea respuesta del bot
[ ] Módulo 2: Historial se obtiene correctamente (últimos 20 mensajes)
[ ] Módulo 2: Array de mensajes se construye en formato correcto
[ ] Módulo 2: Conversaciones expiradas (>6h) se tratan como nuevas
[ ] Módulo 3: Llamada a Groq funciona y devuelve JSON válido
[ ] Módulo 3: Fallback a Claude se activa cuando confidence < 0.7
[ ] Módulo 3: Fallback a Claude se activa cuando intent = complaint/emergency
[ ] Módulo 3: Error handling funciona si Groq no responde
[ ] Módulo 3: Error handling funciona si Claude no responde
[ ] Módulo 4: Respuesta se envía al cliente por WhatsApp
[ ] Módulo 4: Mensaje del cliente se guarda en conversations
[ ] Módulo 4: Respuesta del bot se guarda en conversations
[ ] Módulo 4: conversation_state se actualiza correctamente
[ ] Módulo 4: Escalado notifica a Telegram con formato 🟡
[ ] Módulo 4: Human takeover se activa al escalar
[ ] Error Workflow configurado y enviando alertas 🔴 a Telegram
```
