# Subtarea 09: Monitorización y Alertas

## Objetivo
Sistema completo de monitorización que envía alertas de errores, alertas de límites de uso y resumen diario de actividad a Telegram.

## Dependencias
- **Subtarea 03** — Telegram Bot configurado
- **Subtarea 04** — Uptime Kuma configurado (vigilancia externa)
- **Subtarea 06** — Workflow core funcional

---

## Pasos

### 1. Error Workflow (Alertas 🔴)

Configurar un workflow de error global en n8n que capture cualquier fallo no manejado.

**Configuración:**

1. Crear un nuevo workflow en n8n: `Error Handler`
2. Nodo **Error Trigger** como inicio
3. Ir a **Settings → Error Workflow** y seleccionar este workflow

**Nodos del Error Workflow:**

| # | Tipo de nodo | Nombre | Función |
|---|-------------|--------|---------|
| 1 | Error Trigger | `Error Detectado` | Captura el error |
| 2 | Code | `Formatear Alerta` | Construye mensaje 🔴 |
| 3 | Telegram | `Enviar Alerta` | Envía a Telegram |

**Información a incluir en la alerta 🔴:**

- Nombre del workflow que falló
- Nombre del nodo que falló
- Mensaje de error
- Timestamp
- Si es posible, datos del cliente afectado (clientPhone)

**Formato del mensaje:**

```
🔴 ERROR DE SISTEMA

⚙️ Workflow: [nombre del workflow]
📍 Nodo: [nombre del nodo que falló]
❌ Error: [mensaje de error]
🕐 Hora: [timestamp]
👤 Cliente afectado: [clientPhone si disponible]

⚠️ El bot puede no estar respondiendo a este cliente.
```

### 2. Alerta de Límites de Groq (⚠️)

Crear un workflow que monitorice el uso de la API de Groq y alerte cuando se acerque a los límites.

**Enfoque:** Contar las llamadas a Groq registradas en Supabase y comparar con los límites.

**Nodos del workflow:**

| # | Tipo de nodo | Nombre | Función |
|---|-------------|--------|---------|
| 1 | Cron | `Cada 2 horas` | Dispara cada 2 horas |
| 2 | Postgres | `Contar Mensajes Hoy` | COUNT de conversations de hoy con role='assistant' |
| 3 | Code | `Calcular Uso` | Compara con límite de 30K requests/día |
| 4 | IF | `¿Supera 80%?` | Si uso > 24K requests |
| 5 | Telegram | `Enviar Alerta` | Envía ⚠️ a Telegram |

**Consulta para contar uso diario:**

```sql
SELECT COUNT(*) as total_requests
FROM conversations
WHERE role = 'assistant'
AND timestamp >= CURRENT_DATE;
```

**Umbrales de alerta:**

| Uso | Acción |
|-----|--------|
| < 80% (< 24K) | No hacer nada |
| 80-95% (24K-28.5K) | Alerta ⚠️ "Acercándose al límite" |
| > 95% (> 28.5K) | Alerta ⚠️ urgente "Límite casi alcanzado, considerar activar solo Claude" |

### 3. Resumen Diario (🟢)

Workflow con cron que genera un resumen de actividad y lo envía a Telegram cada noche.

**Nodos del workflow:**

| # | Tipo de nodo | Nombre | Función |
|---|-------------|--------|---------|
| 1 | Cron | `Diario 23:00` | Se ejecuta cada día a las 23:00 |
| 2 | Postgres | `Total Mensajes` | COUNT conversations de hoy |
| 3 | Postgres | `Conversaciones Únicas` | COUNT DISTINCT client_phone de hoy |
| 4 | Postgres | `Escalados` | COUNT conversation_state donde status cambió a 'human' hoy |
| 5 | Postgres | `Preguntas Sin Respuesta` | SELECT mensajes con confidence < 0.7 de hoy |
| 6 | Code | `Calcular Estadísticas` | Procesa los datos y calcula porcentajes |
| 7 | Telegram | `Enviar Resumen` | Envía 🟢 a Telegram |

**Queries necesarias:**

Total mensajes procesados hoy:
```sql
SELECT COUNT(*) FROM conversations
WHERE role = 'assistant' AND timestamp >= CURRENT_DATE;
```

Conversaciones únicas hoy:
```sql
SELECT COUNT(DISTINCT client_phone) FROM conversations
WHERE timestamp >= CURRENT_DATE;
```

Conversaciones escaladas hoy:
```sql
SELECT COUNT(*) FROM conversation_state
WHERE status = 'human' AND last_interaction >= CURRENT_DATE;
```

Mensajes con baja confianza (para detectar gaps en el conocimiento):
```sql
SELECT c.message FROM conversations c
WHERE c.role = 'user'
AND c.timestamp >= CURRENT_DATE
AND c.client_phone IN (
    SELECT DISTINCT client_phone FROM conversations
    WHERE role = 'assistant' AND timestamp >= CURRENT_DATE
)
ORDER BY c.timestamp DESC
LIMIT 10;
```

> **Nota:** Para rastrear confidence por mensaje, considerar añadir un campo `confidence` a la tabla conversations o crear una tabla separada `message_metadata`.

**Tabla adicional sugerida (opcional pero recomendada):**

```sql
CREATE TABLE message_metadata (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    intent VARCHAR(50),
    confidence DECIMAL(3,2),
    escalated BOOLEAN DEFAULT FALSE,
    model_used VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

Esta tabla permite hacer analítica detallada sin modificar la estructura principal.

### 4. Workflows a crear

| Workflow | Trigger | Frecuencia |
|----------|---------|-----------|
| `Error Handler` | Error Trigger | Cada vez que hay un error |
| `Alerta Límites Groq` | Cron | Cada 2 horas |
| `Resumen Diario` | Cron | Diario a las 23:00 |

### 5. Verificar Uptime Kuma

Confirmar que Uptime Kuma (configurado en subtarea 04) está:
- Haciendo ping a n8n cada 60 segundos
- Alertando por Telegram si n8n no responde
- Alertando cuando n8n se recupera

---

## Verificación

```
[ ] Error Workflow configurado como workflow de error global en n8n
[ ] Test: provocar un error → alerta 🔴 llega a Telegram
[ ] Workflow de alerta de límites creado y activo
[ ] Test: simular uso alto → alerta ⚠️ llega a Telegram
[ ] Workflow de resumen diario creado y activo
[ ] Test: ejecutar manualmente → resumen 🟢 llega a Telegram con datos correctos
[ ] Tabla message_metadata creada (si se decidió implementar)
[ ] Uptime Kuma sigue operativo y alertando correctamente
[ ] Todos los workflows de monitorización están ACTIVOS en n8n
```
