# Plan de Acción Técnico: Chatbot IA con n8n

## Servicio de Alquiler de Lockers

---

## Índice

1. [Stack Tecnológico](#1-stack-tecnológico)
2. [Esquema de Base de Datos](#2-esquema-de-base-de-datos-supabase---postgres)
3. [Arquitectura del Workflow en n8n](#3-arquitectura-del-workflow-en-n8n)
4. [System Prompt — Estructura Técnica](#4-system-prompt--estructura-técnica)
5. [Casos de Uso y Comportamiento Esperado](#5-casos-de-uso-y-comportamiento-esperado)
6. [Checklist de Desarrollo](#6-checklist-de-desarrollo)

---

## 1. Stack Tecnológico

| Componente | Herramienta | Función |
|-----------|-------------|---------|
| Orquestador | **n8n** (self-hosted) | Motor del workflow completo |
| Canal de comunicación | **WhatsApp Business API** (Meta Cloud API directa) | Recibir y enviar mensajes |
| IA principal | **Groq** (llama-4-scout-17b-16e-instruct) | Generar respuestas rápidas para consultas estándar (80% del tráfico) |
| IA fallback | **Claude API (Sonnet)** | Generar respuestas de alta calidad para casos complejos (20% del tráfico) |
| Transcripción de audio | **Groq Whisper** (whisper-large-v3-turbo) | Convertir notas de voz a texto |
| Base de datos | **Supabase (Postgres)** | Historial de conversaciones, estado, analítica |
| Canal de gestión y monitorización | **Telegram Bot** (canal personal) | Alertas de sistema, escalado a humano, resúmenes diarios, alertas de límites |
| Vigilancia externa | **Uptime Kuma** (self-hosted, Docker) | Monitoriza que n8n esté activo de forma independiente, avisa por Telegram si se cae |

### Estrategia Híbrida de IA: Groq + Claude Sonnet

```
[Mensaje del cliente]
    → [Groq: llama-4-scout genera respuesta]
    → [Code: evaluar confidence]
    → [IF: confidence < 0.7 OR intent = complaint/emergency]
        → SÍ → [Claude Sonnet: regenerar respuesta con mayor calidad]
        → NO → [Enviar respuesta de Groq]
```

- **Groq (principal):** Modelo `meta-llama/llama-4-scout-17b-16e-instruct` — Free tier: 30K req/día, 500K tokens/día
- **Claude Sonnet (fallback):** Modelo `claude-sonnet-4-20250514` — ~3$/1M input, ~15$/1M output

### Transcripción de Audio con Groq Whisper

```
[Mensaje de audio entrante en WhatsApp]
    → [HTTP Request: descargar audio de Meta API]
    → [Groq Whisper: transcribir audio a texto]
    → [Continúa el flujo normal con el texto transcrito]
```

- **Modelo:** `whisper-large-v3-turbo` — Free tier: 7.2K seg audio/hora, 28.8K seg/día

### Mapa de Arquitectura del Stack

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CLIENTE (WhatsApp)                             │
│                    📱 Envía mensaje (texto o audio)                     │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     META CLOUD API (WhatsApp)                           │
│              Recibe mensaje → Webhook POST → n8n                        │
│              Recibe respuesta de n8n → Envía al cliente                  │
│              💰 Gratis (conversaciones iniciadas por cliente)            │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          n8n (Orquestador)                              │
│                                                                         │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────────────────┐  │
│  │  Webhook     │───▶│ Preprocesar  │───▶│  ¿Texto o Audio?           │  │
│  │  (Trigger)   │    │  mensaje     │    │                            │  │
│  └─────────────┘    └──────────────┘    └─────┬──────────┬───────────┘  │
│                                               │          │              │
│                                          TEXTO│     AUDIO│              │
│                                               │          │              │
│                                               │          ▼              │
│                                               │  ┌──────────────────┐   │
│                                               │  │  GROQ WHISPER    │   │
│                                               │  │  Transcribir     │   │
│                                               │  │  audio → texto   │   │
│                                               │  │  🆓 Free tier    │   │
│                                               │  └───────┬──────────┘   │
│                                               │          │              │
│                                               ◀──────────┘              │
│                                               │                         │
│                                               ▼                         │
│                                  ┌─────────────────────────┐            │
│                                  │  SUPABASE (Postgres)    │            │
│                                  │  • Obtener historial    │            │
│                                  │  • Consultar estado     │            │
│                                  │  🆓 Free tier           │            │
│                                  └────────────┬────────────┘            │
│                                               │                         │
│                                               ▼                         │
│                                  ┌─────────────────────────┐            │
│                                  │  GROQ (IA Principal)    │            │
│                                  │  llama-4-scout-17b      │            │
│                                  │  Genera respuesta JSON  │            │
│                                  │  🆓 Free tier           │            │
│                                  └────────────┬────────────┘            │
│                                               │                         │
│                                               ▼                         │
│                                  ┌─────────────────────────┐            │
│                                  │  ¿Confidence < 0.7?     │            │
│                                  │  ¿Intent complejo?      │            │
│                                  └─────┬───────────┬───────┘            │
│                                        │           │                    │
│                                   SÍ   │      NO   │                    │
│                                        ▼           │                    │
│                           ┌────────────────────┐   │                    │
│                           │  CLAUDE SONNET     │   │                    │
│                           │  (IA Fallback)     │   │                    │
│                           │  Regenera con      │   │                    │
│                           │  mayor calidad     │   │                    │
│                           │  💰 Pago por uso   │   │                    │
│                           └─────────┬──────────┘   │                    │
│                                     │              │                    │
│                                     ▼              ▼                    │
│                                  ┌─────────────────────────┐            │
│                                  │  ¿Escalar a humano?     │            │
│                                  └─────┬───────────┬───────┘            │
│                                        │           │                    │
│                                   SÍ   │      NO   │                    │
│                                        ▼           │                    │
│                           ┌────────────────────┐   │                    │
│                           │  TELEGRAM BOT      │   │                    │
│                           │  Notifica al       │   │                    │
│                           │  propietario       │   │                    │
│                           │  🆓 Gratis         │   │                    │
│                           └────────────────────┘   │                    │
│                                     │              │                    │
│                                     ▼              ▼                    │
│                                  ┌─────────────────────────┐            │
│                                  │  SUPABASE (Postgres)    │            │
│                                  │  • Guardar mensaje      │            │
│                                  │  • Guardar respuesta    │            │
│                                  │  • Actualizar estado    │            │
│                                  └────────────┬────────────┘            │
│                                               │                         │
└───────────────────────────────────────────────┼─────────────────────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     META CLOUD API (WhatsApp)                           │
│                    Envía respuesta al cliente 📱                        │
└─────────────────────────────────────────────────────────────────────────┘


          ┌──────────────────────────────────────────────────────────┐
          │        TELEGRAM BOT — Canal de Gestión (en paralelo)     │
          │                                                          │
          │  🔴 Alertas de sistema → n8n caído, webhook sin          │
          │     respuesta, errores en el workflow                     │
          │  🟡 Escalado a humano → Cliente requiere atención,       │
          │     con contexto de la conversación                       │
          │  🟢 Resumen diario → Mensajes procesados, tasa de        │
          │     resolución, preguntas sin respuesta                   │
          │  ⚠️  Alertas de límites → Aviso al acercarse a los       │
          │     límites del free tier de Groq                         │
          │                                                          │
          │  Fuentes: n8n Error Workflow + Logs en Supabase           │
          └──────────────────────────────────────────────────────────┘

          ┌──────────────────────────────────────────────────────────┐
          │     UPTIME KUMA — Vigilancia Externa (independiente)     │
          │                                                          │
          │  Funciona FUERA de n8n (contenedor Docker separado)      │
          │  Hace ping a n8n cada X minutos                          │
          │  Si n8n no responde → Avisa por Telegram directamente    │
          │  Cubre el escenario: "n8n caído y nadie se entera"       │
          └──────────────────────────────────────────────────────────┘
```

---

## 2. Esquema de Base de Datos (Supabase - Postgres)

### Modelos de datos

**conversations** — Almacena todos los mensajes intercambiados entre clientes y bot.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Serial (PK) | Identificador único del mensaje |
| client_phone | Varchar(20) | Número de teléfono del cliente (FK → conversation_state) |
| role | Varchar(10) | Quién envió el mensaje: `user` o `assistant` |
| message | Text | Contenido del mensaje |
| timestamp | Timestamptz | Fecha y hora del mensaje |

**conversation_state** — Estado actual de cada conversación activa por cliente.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| client_phone | Varchar(20) (PK) | Número de teléfono del cliente |
| status | Varchar(20) | Quién gestiona la conversación: `bot` / `human` / `closed` |
| current_intent | Varchar(50) | Intención detectada: `info` / `booking` / `support` / `complaint` / `emergency` |
| last_interaction | Timestamptz | Última actividad del cliente |
| metadata | JSONB | Datos variables: idioma, nombre, nº de interacciones, etc. |

**pending_messages** — Buffer temporal para agrupar mensajes rápidos del mismo cliente (antiflood).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Serial (PK) | Identificador único |
| client_phone | Varchar(20) | Número de teléfono del cliente (FK → conversation_state) |
| message | Text | Mensaje pendiente de procesar |
| created_at | Timestamptz | Fecha y hora de recepción |
| processed | Boolean | Si ya fue procesado o no |

### Relaciones entre modelos

```
conversation_state (1) ←──── (N) conversations
       │
       └──────────────────── (N) pending_messages

- conversation_state es el modelo central, identificado por client_phone
- conversations guarda el historial completo de mensajes de cada cliente
- pending_messages es temporal: acumula mensajes rápidos antes de procesarlos como uno solo
```

---

## 3. Arquitectura del Workflow en n8n

### Diagrama general

```
[Mensaje del cliente]
    → [Webhook/Trigger]
    → [Preprocesamiento]
    → [Antiflood: agrupar mensajes]
    → [Consultar estado de conversación]
    → [IF: ¿Humano ha tomado control?]
        → SÍ → [No hacer nada]
        → NO → [Obtener historial]
              → [Construir mensajes para IA]
              → [Llamada a API de IA]
              → [Post-procesar respuesta]
              → [IF: ¿Escalar a humano?]
                  → SÍ → [Notificar Telegram + marcar status='human']
                  → NO → (continúa)
              → [Enviar respuesta por WhatsApp]
              → [Guardar mensaje + respuesta en BD]
              → [Actualizar conversation_state]
```

---

### Módulo 1: Recepción y Preprocesamiento

```
[Webhook: mensaje entrante de WhatsApp (Meta Cloud API)]
    → [Extraer datos: clientPhone, messageText, messageType, timestamp, clientName]
    → [Validar tipo de mensaje]
    → [IF: ¿Es texto?]
        → SÍ → [Continúa al Módulo 2]
        → NO → [IF: ¿Es audio?]
            → SÍ → [Groq Whisper: transcribir a texto] → [Continúa al Módulo 2]
            → NO → [Responder: "Solo puedo procesar texto y audio"]
```

**Datos a extraer del webhook de Meta Cloud API:**

| Campo | Origen | Descripción |
|-------|--------|-------------|
| clientPhone | `messages[0].from` | Número del cliente |
| messageText | `messages[0].text.body` | Contenido del mensaje |
| messageType | `messages[0].type` | Tipo: text, image, audio, document |
| timestamp | `messages[0].timestamp` | Hora del mensaje |
| clientName | `contacts[0].profile.name` | Nombre del cliente en WhatsApp |

---

### Módulo 2: Estado y Contexto

```
[Supabase: consultar conversation_state por clientPhone]
    → [IF: ¿status = 'human'?]
        → SÍ → [No hacer nada, el humano gestiona]
        → NO → [Supabase: obtener últimos 20 mensajes de conversations]
              → [Construir array de historial con formato {role, content}]
              → [Añadir mensaje actual del cliente al array]
              → [Continúa al Módulo 3]
```

**El historial se construye como array de objetos `{role, content}` ordenados cronológicamente, que es el formato que esperan las APIs de Groq y Anthropic.**

---

### Módulo 3: Generación de Respuesta con IA

```
[HTTP Request POST a Groq API]
    → Envía: system prompt + historial + mensaje actual
    → Recibe: JSON con response, intent, escalate, confidence
    → [IF: confidence < 0.7 OR intent = complaint/emergency]
        → SÍ → [HTTP Request POST a Claude Sonnet API]
              → Regenera respuesta con mayor calidad
        → NO → [Continúa con respuesta de Groq]
    → [Continúa al Módulo 4]
```

**Método de conexión:** HTTP Request directo a las APIs (no usar nodos AI Agent nativos de n8n).

**Endpoints:**

| Servicio | URL | Método |
|----------|-----|--------|
| Groq | `https://api.groq.com/openai/v1/chat/completions` | POST |
| Claude Sonnet | `https://api.anthropic.com/v1/messages` | POST |

**Formato de respuesta obligatorio del modelo (definido en system prompt):**

```
{
    "response": "mensaje al cliente",
    "intent": "info | booking | support | complaint | emergency",
    "escalate": true/false,
    "confidence": 0.0 - 1.0
}
```

---

### Módulo 4: Post-procesamiento y Envío

```
[Parsear JSON de respuesta del modelo]
    → [Extraer: responseText, intent, escalate, confidence]
    → [IF: escalate = true OR confidence < 0.7 OR intent = emergency/complaint]
        → SÍ → [Telegram: notificar 🟡 con contexto de conversación]
              → [Supabase: actualizar status = 'human']
    → [HTTP Request: enviar responseText por WhatsApp (Meta Cloud API)]
    → [Supabase: guardar mensaje del cliente + respuesta en conversations]
    → [Supabase: actualizar conversation_state (intent, last_interaction)]
```

**Reglas de escalado:**

| Condición | Acción |
|-----------|--------|
| `escalate = true` | Escalar siempre |
| `confidence < 0.7` | Escalar por baja confianza |
| `intent = emergency` | Escalar urgente |
| `intent = complaint` | Escalar siempre |

---

### Módulo 5: Antiflood / Agrupación de Mensajes

```
[Webhook: mensaje entrante]
    → [Supabase: guardar en pending_messages]
    → [Wait: 8 segundos]
    → [Supabase: obtener todos los pending_messages de este cliente en últimos 15 seg]
    → [Concatenar todos en un solo mensaje]
    → [Marcar como processed = true]
    → [Continúa al Módulo 2]
```

**Problema que resuelve:** Los clientes envían varios mensajes seguidos ("Hola" → "Quería preguntar" → "Cuánto cuesta"). Sin antiflood, el bot responde a cada uno por separado. Con el Wait de 8 segundos, se agrupan y procesan como uno solo.

---

## 4. System Prompt — Estructura Técnica

El system prompt es el elemento más crítico del bot. Estructura recomendada:

```
[SECCIÓN 1: IDENTIDAD]
Quién eres, para qué negocio trabajas, tu tono y personalidad.

[SECCIÓN 2: REGLAS DE COMPORTAMIENTO]
- Qué puede y qué no puede hacer el bot.
- Formato de respuesta (JSON interno).
- Cuándo escalar a humano.
- Límites estrictos (no inventar información, no prometer).

[SECCIÓN 3: CONTEXTO DEL NEGOCIO]
Toda la información operativa:
- Precios, tamaños, horarios, ubicación.
- Proceso de reserva paso a paso.
- Políticas de cancelación, objetos prohibidos.
- FAQs completas.

[SECCIÓN 4: GESTIÓN DE IDIOMAS]
- Cómo detectar el idioma del cliente.
- En qué idiomas responder.
- Idioma principal y secundarios.

[SECCIÓN 5: FORMATO DE RESPUESTA]
Estructura JSON obligatoria:
{
    "response": "mensaje al cliente",
    "intent": "info|booking|support|complaint|emergency",
    "escalate": false,
    "confidence": 0.95
}

[SECCIÓN 6: EJEMPLOS (Few-shot)]
3-5 ejemplos de conversaciones ideales que muestren:
- El tono correcto.
- La longitud correcta de respuesta.
- Cómo manejar distintos tipos de consulta.
- Cómo y cuándo escalar.
```

### Reglas de personalidad

- Amable, profesional pero cercano.
- Respuestas cortas adaptadas a WhatsApp (máximo 3-4 líneas por bloque).
- Emojis con moderación (1-2 por mensaje máximo).
- Nunca responde de forma pasivo-agresiva.
- Detectar si el cliente tutea o usa "usted" y adaptarse.

### Límites estrictos

- Nunca inventa información fuera del contexto proporcionado.
- Nunca da precios aproximados si no tiene los exactos.
- Nunca promete algo que el negocio no pueda cumplir.
- Nunca comparte datos de otros clientes.
- Si no sabe algo, lo dice claramente y escala.

---

## 5. Casos de Uso y Comportamiento Esperado

> **Sección dinámica:** Los casos de uso se definen y actualizan de forma continua durante el desarrollo y vida del proyecto. Pueden crecer o reducirse según las necesidades del negocio.

### Formato para definir cada caso de uso

Cada caso de uso debe documentarse con la siguiente estructura:

| Campo | Descripción |
|-------|-------------|
| **Caso** | Nombre del caso de uso |
| **Trigger** | Qué mensaje o intención del cliente lo activa |
| **Acción del bot** | Qué debe hacer el bot |
| **Datos necesarios** | Qué información necesita el bot para resolver |
| **Escala a humano** | Sí / No / Condicional (y bajo qué condición) |
| **Prioridad** | Alta / Media / Baja |

### Ejemplo de caso de uso

| Campo | Valor |
|-------|-------|
| **Caso** | Consulta de precios |
| **Trigger** | Cliente pregunta por precio, coste, tarifas |
| **Acción del bot** | Responde con precios según tamaño solicitado |
| **Datos necesarios** | Lista de precios por tamaño (del contexto del negocio) |
| **Escala a humano** | No |
| **Prioridad** | Alta |

### Categorías sugeridas para organizar los casos

- **Consultas informativas** — Precios, horarios, ubicación, métodos de pago
- **Gestión de reservas** — Nueva reserva, modificación, cancelación, extensión
- **Incidencias y soporte** — Problemas de acceso, objetos olvidados, quejas
- **Interacciones conversacionales** — Saludos, agradecimientos, mensajes ambiguos, multiidioma
- **Casos límite** — Emergencias, abuso, spam, solicitud de humano, reclamaciones legales

---

## 6. Checklist de Desarrollo

> Checklist completo del proyecto. Marcar cada item cuando esté completado.

## 6. Checklist de Desarrollo — Subtareas

> Cada fase corresponde a una subtarea con documentación técnica completa paso a paso.

| # | Subtarea | Documento | Depende de | Estado |
|---|----------|-----------|------------|--------|
| 00 | Planificación | `plan-tecnico-chatbot-n8n.md` (este documento) | — | ✅ |
| 01 | Supabase (Base de datos) | `subtarea-01-supabase.md` | — | ✅ |
| 02 | Meta WhatsApp Cloud API | `subtarea-02-meta-whatsapp-api.md` | — | ✅ |
| 03 | Telegram Bot | `subtarea-03-telegram-bot.md` | — | ✅ |
| 04 | Uptime Kuma | `subtarea-04-uptime-kuma.md` | 03 | ✅ |
| 05 | Contenido del Bot (System Prompt) | `subtarea-05-contenido-bot.md` | 01 | ⬜ |
| 06 | Workflow Core (Módulos 1-4) | `subtarea-06-workflow-core.md` | 01, 02, 05 | ⬜ |
| 07 | Antiflood (Módulo 5) | `subtarea-07-antiflood.md` | 01, 06 | ⬜ |
| 08 | Escalado a Humano | `subtarea-08-escalado-humano.md` | 03, 06 | ⬜ |
| 09 | Monitorización y Alertas | `subtarea-09-monitorizacion-alertas.md` | 03, 04, 06 | ⬜ |
| 10 | Testing | `subtarea-10-testing.md` | 06, 07, 08, 09 | ⬜ |
| 11 | Deploy a Producción | `subtarea-11-deploy.md` | 10 | ⬜ |

### Orden de ejecución recomendado

Las subtareas 01, 02 y 03 se pueden ejecutar en paralelo (no tienen dependencias entre sí).

```
Paralelo:  [01 Supabase] [02 Meta API] [03 Telegram]
                  │              │            │
                  │              │            └──→ [04 Uptime Kuma]
                  │              │
                  └──→ [05 Contenido Bot]
                              │
                  ┌───────────┘
                  ▼
           [06 Workflow Core] ←── 01 + 02 + 05
                  │
          ┌───────┼───────┐
          ▼       ▼       ▼
   [07 Antiflood] [08 Escalado] [09 Monitorización]
          │       │       │
          └───────┼───────┘
                  ▼
           [10 Testing]
                  │
                  ▼
           [11 Deploy]
```

