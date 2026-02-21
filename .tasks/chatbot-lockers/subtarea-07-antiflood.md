# Subtarea 07: Antiflood — Agrupación de Mensajes (Módulo 5)

## Objetivo
Sistema que agrupa mensajes rápidos del mismo cliente en uno solo antes de procesarlos, evitando que el bot responda a cada mensaje individual.

## Dependencias
- **Subtarea 01** — Supabase operativa (tabla pending_messages)
- **Subtarea 06** — Workflow core funcional (el antiflood se integra antes del Módulo 2)

---

## Problema que resuelve

Los clientes de WhatsApp envían mensajes así:

```
[12:00:01] "Hola"
[12:00:03] "Quería preguntar"
[12:00:06] "Cuánto cuesta un locker grande"
[12:00:08] "Para mañana"
```

Sin antiflood, el bot responde 4 veces. Con antiflood, espera unos segundos, agrupa todo en un solo mensaje y responde una vez.

---

## Pasos

### 1. Modificar el Webhook del Módulo 1

El flujo cambia: en lugar de ir directamente al Módulo 2, el mensaje primero se guarda en `pending_messages`:

```
[Webhook: mensaje entrante]
    → [Extraer datos (Módulo 1)]
    → [Supabase: INSERT en pending_messages]
    → [Wait: 8 segundos]
    → [Supabase: SELECT todos los pending_messages de este clientPhone 
        WHERE processed = false AND created_at > NOW() - 15 segundos]
    → [Code: verificar si este es el último mensaje del grupo]
    → [IF: ¿Es el último?]
        → SÍ → [Code: concatenar todos los mensajes en uno]
              → [Supabase: UPDATE processed = true para todos estos mensajes]
              → [Continúa al Módulo 2]
        → NO → [FIN — otro proceso ya se encargará de este grupo]
```

### 2. Lógica de "¿Es el último?"

El problema del nodo Wait es que CADA mensaje entrante dispara su propio flujo con su propio Wait. Si llegan 4 mensajes en 8 segundos, habrá 4 flujos esperando.

**Solución:** Después del Wait, consultar pending_messages y verificar si el mensaje actual es el más reciente del grupo. Solo el flujo del último mensaje procesa el grupo completo.

**Cómo verificar:**
1. Después del Wait, consultar: `SELECT * FROM pending_messages WHERE client_phone = [clientPhone] AND processed = false ORDER BY created_at DESC`
2. Si el `id` del primer resultado coincide con el `id` del mensaje que disparó ESTE flujo → es el último → procesar
3. Si no coincide → otro mensaje más reciente tomará el control → este flujo termina

### 3. Concatenación de mensajes

Cuando se procesan múltiples mensajes, concatenarlos en uno solo separados por un espacio o salto de línea:

**Input:**
```
"Hola"
"Quería preguntar"
"Cuánto cuesta un locker grande"
"Para mañana"
```

**Output:**
```
"Hola. Quería preguntar. Cuánto cuesta un locker grande. Para mañana"
```

### 4. Casos especiales

| Caso | Comportamiento |
|------|---------------|
| Cliente envía 1 solo mensaje | Wait 8s → solo hay 1 pending → se procesa normal |
| Cliente envía texto + audio seguidos | Ambos se guardan como pending, el audio se transcribe antes de guardar |
| Cliente envía 10+ mensajes seguidos | Se agrupan todos (no hay límite, pero en la práctica raramente pasan de 5-6) |
| Dos clientes envían al mismo tiempo | Cada cliente tiene su propio grupo (filtrado por clientPhone) |

### 5. Limpieza de pending_messages

Los mensajes procesados se acumulan en la tabla. Opciones de limpieza:

- **Opción A:** Workflow con cron diario que elimina registros con `processed = true` y `created_at < NOW() - 24 horas`
- **Opción B:** Eliminar inmediatamente después de procesar (en el mismo flujo)

Recomendación: Opción A, para poder debuggear si algo falla.

### 6. Parámetros configurables

| Parámetro | Valor recomendado | Descripción |
|-----------|-------------------|-------------|
| Wait time | 8 segundos | Tiempo de espera antes de procesar |
| Ventana de agrupación | 15 segundos | Mensajes dentro de esta ventana se agrupan |
| Limpieza de pending | Cada 24 horas | Cron que limpia mensajes procesados |

---

## Nodos a crear/modificar

| # | Tipo de nodo | Nombre | Función |
|---|-------------|--------|---------|
| 1 | Postgres | `Guardar Pending` | INSERT en pending_messages |
| 2 | Wait | `Esperar 8s` | Pausa de 8 segundos |
| 3 | Postgres | `Consultar Pending` | SELECT pending del mismo clientPhone |
| 4 | Code | `¿Es último?` | Verifica si este mensaje es el más reciente |
| 5 | IF | `Procesar o no` | Bifurca según resultado |
| 6 | Code | `Concatenar` | Une todos los mensajes en uno |
| 7 | Postgres | `Marcar Procesados` | UPDATE processed = true |

---

## Verificación

```
[ ] Tabla pending_messages operativa en Supabase
[ ] Mensaje individual se guarda en pending_messages
[ ] Wait de 8 segundos funciona correctamente
[ ] Mensajes rápidos (2-3 en <8s) se agrupan en uno solo
[ ] Solo el flujo del último mensaje procesa el grupo
[ ] Mensajes concatenados llegan correctamente al Módulo 2
[ ] Mensajes se marcan como processed = true después de procesar
[ ] Dos clientes simultáneos se procesan independientemente
[ ] Workflow de limpieza diaria configurado (cron)
```
