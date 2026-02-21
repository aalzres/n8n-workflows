# Subtarea 08: Escalado a Humano

## Objetivo
Sistema completo de escalado: detección automática, notificación al propietario por Telegram con contexto, respuesta al cliente, y mecanismo para devolver el control al bot.

## Dependencias
- **Subtarea 03** — Telegram Bot configurado y conectado a n8n
- **Subtarea 06** — Workflow core funcional (el escalado se integra en el Módulo 4)

---

## Pasos

### 1. Condiciones de escalado

El escalado se activa cuando se cumple CUALQUIERA de estas condiciones (definidas en el Módulo 4 del workflow core):

| Condición | Origen | Prioridad |
|-----------|--------|-----------|
| `escalate = true` | El modelo decide que necesita humano | Alta |
| `confidence < 0.7` | El modelo no está seguro de su respuesta | Media |
| `intent = emergency` | Emergencia detectada | Urgente |
| `intent = complaint` | Queja o reclamación | Alta |
| Cliente dice "quiero hablar con una persona" (o similar) | Detectado por el modelo | Alta |

### 2. Flujo de escalado

```
[Condición de escalado detectada]
    → [Supabase: UPDATE conversation_state SET status = 'human']
    → [Supabase: SELECT últimos 5 mensajes de este cliente]
    → [Code: construir mensaje de notificación]
    → [Telegram: enviar notificación 🟡]
    → [HTTP Request: enviar mensaje de escalado al cliente por WhatsApp]
```

### 3. Mensaje al cliente cuando se escala

Adaptar según el motivo:

| Motivo | Mensaje al cliente |
|--------|--------------------|
| Queja | "Lamento la situación. Paso tu caso a un agente que te responderá lo antes posible 🙏" |
| Emergencia | "Entiendo la urgencia. Un agente está siendo notificado ahora mismo. Si necesitas contacto inmediato: [TELÉFONO]" |
| Baja confianza | "Para asegurarme de darte la información correcta, paso tu consulta a un agente. Te responderá pronto 😊" |
| Cliente lo pide | "Por supuesto, paso tu conversación a un agente. Te responderá lo antes posible 🙏" |

> **Nota:** Este mensaje lo genera el propio modelo en el campo `response` del JSON. Las frases de arriba son orientativas para el system prompt.

### 4. Formato de notificación a Telegram

El mensaje a Telegram debe contener todo el contexto necesario para que el propietario pueda responder sin tener que buscar información:

```
🟡 ESCALADO A HUMANO

👤 Cliente: [clientName] ([clientPhone])
🏷️ Intent: [intent]
📊 Confidence: [confidence]
📌 Motivo: [escalate=true / confidence<0.7 / intent=emergency/complaint]

💬 Últimos mensajes:
───────────────────
👤 [mensaje cliente 1]
🤖 [respuesta bot 1]
👤 [mensaje cliente 2]
🤖 [respuesta bot 2]
👤 [mensaje cliente actual]
🤖 [respuesta bot actual (la de escalado)]
───────────────────

📱 Responder directamente al cliente: wa.me/[clientPhone]
```

El link `wa.me/[clientPhone]` permite al propietario abrir WhatsApp directamente con ese cliente.

### 5. Mecanismo para devolver el control al bot

Cuando el propietario termina de gestionar el caso, necesita devolver el control al bot. Opciones:

**Opción A — Comando por Telegram (recomendado):**

Crear un segundo workflow en n8n con un **Telegram Trigger** que escuche comandos:

```
[Telegram Trigger: nuevo mensaje al bot]
    → [Code: parsear comando]
    → [IF: ¿Es comando /bot?]
        → SÍ → [Extraer número de teléfono del comando]
              → [Supabase: UPDATE conversation_state SET status = 'bot' WHERE client_phone = X]
              → [Telegram: responder "✅ Control devuelto al bot para [clientPhone]"]
        → NO → [Ignorar]
```

**Uso:** El propietario envía al bot de Telegram: `/bot 34612345678`

**Opción B — Expiración automática:**

Si no hay interacción en la conversación escalada durante X horas (ej: 4 horas), devolver automáticamente el control al bot:

- Workflow con cron cada hora
- Consulta: `SELECT * FROM conversation_state WHERE status = 'human' AND last_interaction < NOW() - INTERVAL '4 hours'`
- UPDATE status = 'bot' para esos registros
- Notificar por Telegram: "⏰ Conversación con [clientPhone] devuelta al bot por inactividad"

**Recomendación:** Implementar ambas opciones. La opción A para control manual inmediato, la opción B como red de seguridad para no olvidar conversaciones en estado 'human'.

### 6. Comandos de Telegram para gestión

Ampliar el workflow de Telegram Trigger para soportar estos comandos:

| Comando | Función |
|---------|---------|
| `/bot [teléfono]` | Devuelve control al bot para ese cliente |
| `/status [teléfono]` | Muestra el estado actual de la conversación con ese cliente |
| `/escalados` | Lista todas las conversaciones actualmente en estado 'human' |

### 7. Nodos a crear

**En el workflow principal (integrado en Módulo 4):**

| # | Tipo de nodo | Nombre | Función |
|---|-------------|--------|---------|
| 1 | Postgres | `Marcar Human Takeover` | UPDATE status='human' |
| 2 | Postgres | `Obtener Contexto Escalado` | SELECT últimos 5 mensajes |
| 3 | Code | `Construir Notificación` | Arma el mensaje 🟡 con formato completo |
| 4 | Telegram | `Notificar Escalado` | Envía a Telegram |

**Workflow separado — Comandos de Telegram:**

| # | Tipo de nodo | Nombre | Función |
|---|-------------|--------|---------|
| 1 | Telegram Trigger | `Comando Telegram` | Escucha mensajes al bot |
| 2 | Code | `Parsear Comando` | Extrae comando y parámetros |
| 3 | Switch | `¿Qué comando?` | Bifurca según /bot, /status, /escalados |
| 4 | Postgres | `Ejecutar Acción` | Consulta o actualiza conversation_state |
| 5 | Telegram | `Responder` | Confirma la acción al propietario |

**Workflow separado — Expiración automática:**

| # | Tipo de nodo | Nombre | Función |
|---|-------------|--------|---------|
| 1 | Cron | `Cada hora` | Dispara cada hora |
| 2 | Postgres | `Buscar Expirados` | SELECT status='human' AND last_interaction < 4h |
| 3 | Postgres | `Devolver a Bot` | UPDATE status='bot' |
| 4 | Telegram | `Notificar Expiración` | Envía ⏰ a Telegram |

---

## Verificación

```
[ ] Escalado se activa cuando escalate = true
[ ] Escalado se activa cuando confidence < 0.7
[ ] Escalado se activa cuando intent = emergency
[ ] Escalado se activa cuando intent = complaint
[ ] conversation_state se actualiza a status = 'human'
[ ] Bot NO responde cuando status = 'human'
[ ] Notificación 🟡 llega a Telegram con contexto completo
[ ] Link wa.me/[phone] funciona correctamente
[ ] Mensaje de escalado llega al cliente por WhatsApp
[ ] Comando /bot [teléfono] devuelve control al bot
[ ] Comando /status [teléfono] muestra estado de la conversación
[ ] Comando /escalados lista conversaciones escaladas
[ ] Expiración automática funciona (4h sin interacción → vuelve a bot)
[ ] Notificación ⏰ llega a Telegram cuando expira
```
