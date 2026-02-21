# Subtarea 10: Testing

## Objetivo
Probar todos los flujos del bot con casos reales y edge cases antes de activar en producción. Verificar que cada módulo funciona individual y conjuntamente.

## Dependencias
- **Subtarea 06** — Workflow core funcional
- **Subtarea 07** — Antiflood implementado
- **Subtarea 08** — Escalado a humano implementado
- **Subtarea 09** — Monitorización configurada

---

## Requisitos previos

- Número de WhatsApp secundario para pruebas (no usar el número de producción)
- Acceso al panel de Supabase para verificar datos
- Telegram abierto para verificar notificaciones

---

## Plan de Testing

### Test 1: Flujo básico completo

| # | Acción | Resultado esperado | ✓ |
|---|--------|--------------------|---|
| 1.1 | Enviar "Hola" desde WhatsApp de prueba | Bot responde con saludo y pregunta en qué puede ayudar | [ ] |
| 1.2 | Verificar en Supabase: tabla conversations | Hay 2 registros: mensaje del cliente (role=user) y respuesta (role=assistant) | [ ] |
| 1.3 | Verificar en Supabase: tabla conversation_state | Hay 1 registro con status=bot, intent=info | [ ] |
| 1.4 | Enviar "Cuánto cuesta un locker grande?" | Bot responde con el precio correcto del contexto | [ ] |
| 1.5 | Verificar que el historial crece en conversations | 4 registros (2 del cliente, 2 del bot) | [ ] |

### Test 2: Transcripción de audio

| # | Acción | Resultado esperado | ✓ |
|---|--------|--------------------|---|
| 2.1 | Enviar nota de voz diciendo "¿Cuáles son los horarios?" | Bot responde con los horarios correctos | [ ] |
| 2.2 | Verificar en conversations | El mensaje del cliente se guardó como texto (transcrito) | [ ] |

### Test 3: Tipo de mensaje no soportado

| # | Acción | Resultado esperado | ✓ |
|---|--------|--------------------|---|
| 3.1 | Enviar una imagen | Bot responde que solo procesa texto y audio | [ ] |
| 3.2 | Enviar un sticker | Bot responde que solo procesa texto y audio | [ ] |
| 3.3 | Enviar un documento | Bot responde que solo procesa texto y audio | [ ] |

### Test 4: Antiflood

| # | Acción | Resultado esperado | ✓ |
|---|--------|--------------------|---|
| 4.1 | Enviar rápidamente: "Hola" → "Quería saber" → "El precio del grande" | Bot responde UNA sola vez al mensaje concatenado | [ ] |
| 4.2 | Verificar en pending_messages | Los 3 mensajes están marcados como processed=true | [ ] |
| 4.3 | Verificar en conversations | 1 solo mensaje del cliente (concatenado) y 1 respuesta del bot | [ ] |

### Test 5: Historial y contexto

| # | Acción | Resultado esperado | ✓ |
|---|--------|--------------------|---|
| 5.1 | Enviar "¿Cuánto cuesta el grande?" | Bot responde con precio del grande | [ ] |
| 5.2 | Enviar "¿Y el mediano?" | Bot entiende por contexto que preguntas por precio y responde el del mediano | [ ] |
| 5.3 | Enviar "Sí" | Bot interpreta según contexto previo (ej: ¿quieres reservar?) | [ ] |

### Test 6: Fallback a Claude Sonnet

| # | Acción | Resultado esperado | ✓ |
|---|--------|--------------------|---|
| 6.1 | Enviar una queja: "Llevo 30 minutos esperando, esto es inaceptable" | La respuesta viene de Claude (intent=complaint, confidence alto) | [ ] |
| 6.2 | Enviar algo ambiguo: "Mmm no sé, depende de varias cosas..." | Groq responde con confidence < 0.7, fallback a Claude | [ ] |
| 6.3 | Verificar en message_metadata (si implementada) | model_used = 'claude-sonnet' para estos casos | [ ] |

### Test 7: Escalado a humano

| # | Acción | Resultado esperado | ✓ |
|---|--------|--------------------|---|
| 7.1 | Enviar "Quiero hablar con una persona" | Bot responde que pasa a un agente, notificación 🟡 en Telegram | [ ] |
| 7.2 | Verificar conversation_state | status = 'human' | [ ] |
| 7.3 | Enviar otro mensaje desde el mismo número | Bot NO responde (human takeover activo) | [ ] |
| 7.4 | Enviar `/bot [teléfono]` en Telegram | Bot confirma ✅, status vuelve a 'bot' | [ ] |
| 7.5 | Enviar mensaje desde el mismo número | Bot responde de nuevo normalmente | [ ] |
| 7.6 | Enviar queja agresiva | Escalado automático + notificación 🟡 con contexto | [ ] |
| 7.7 | Verificar que la notificación incluye historial | Últimos mensajes visibles en Telegram | [ ] |
| 7.8 | Verificar link wa.me/ en la notificación | Abre WhatsApp con el cliente correcto | [ ] |

### Test 8: Multiidioma

| # | Acción | Resultado esperado | ✓ |
|---|--------|--------------------|---|
| 8.1 | Enviar "Hi, what are your prices?" | Bot responde en inglés con los precios | [ ] |
| 8.2 | Enviar "Bonjour, quels sont vos horaires?" | Bot intenta responder en francés o responde en inglés | [ ] |
| 8.3 | Continuar conversación en inglés | Bot mantiene el inglés durante toda la conversación | [ ] |

### Test 9: Edge cases

| # | Acción | Resultado esperado | ✓ |
|---|--------|--------------------|---|
| 9.1 | Enviar mensaje vacío o solo espacios | Bot no crashea, ignora o pide que reformule | [ ] |
| 9.2 | Enviar un mensaje muy largo (+500 palabras) | Bot responde sin error | [ ] |
| 9.3 | Enviar emojis solos "😂😂😂" | Bot responde algo sensato o pide en qué puede ayudar | [ ] |
| 9.4 | Enviar pregunta fuera de contexto: "¿Cuál es la capital de Francia?" | Bot responde que no tiene esa info pero ofrece ayudar con lockers | [ ] |
| 9.5 | Enviar mensaje con caracteres especiales: "Cuesta < 10€? ¿O > 20€?" | Bot no crashea, responde correctamente | [ ] |

### Test 10: Error handling

| # | Acción | Resultado esperado | ✓ |
|---|--------|--------------------|---|
| 10.1 | Desactivar temporalmente credencial de Groq | Error handling se activa, fallback a Claude o mensaje genérico | [ ] |
| 10.2 | Verificar Telegram | Alerta 🔴 recibida con detalle del error | [ ] |
| 10.3 | Reactivar credencial de Groq | Bot vuelve a funcionar normalmente | [ ] |
| 10.4 | Desactivar temporalmente AMBAS APIs (Groq + Claude) | Cliente recibe mensaje genérico de error + alerta 🔴 | [ ] |

### Test 11: Monitorización

| # | Acción | Resultado esperado | ✓ |
|---|--------|--------------------|---|
| 11.1 | Ejecutar manualmente el resumen diario | Resumen 🟢 llega a Telegram con datos correctos | [ ] |
| 11.2 | Verificar que los números del resumen coinciden con Supabase | Mensajes, escalados, conversaciones coinciden | [ ] |
| 11.3 | Parar n8n temporalmente | Uptime Kuma alerta por Telegram | [ ] |
| 11.4 | Reiniciar n8n | Uptime Kuma notifica recuperación | [ ] |

### Test 12: Expiración de conversación

| # | Acción | Resultado esperado | ✓ |
|---|--------|--------------------|---|
| 12.1 | Escalar una conversación a humano | status = 'human' | [ ] |
| 12.2 | Esperar expiración automática (o ejecutar cron manualmente) | status vuelve a 'bot' + notificación ⏰ | [ ] |
| 12.3 | Verificar que el bot responde de nuevo | Bot funciona normalmente con ese cliente | [ ] |

---

## Resultado del Testing

Después de completar todos los tests, documentar:

- **Tests pasados:** [N] / [Total]
- **Tests fallidos:** Lista con detalle de cada fallo
- **Acciones correctivas:** Qué se ajustó para resolver cada fallo
- **Re-test:** Confirmar que los ajustes resuelven los fallos

---

## Verificación

```
[ ] Todos los tests del 1 al 12 ejecutados
[ ] Todos los tests pasados (o fallos documentados y corregidos)
[ ] Re-test de fallos completado
[ ] Bot estable durante al menos 1 hora de pruebas continuas
[ ] Sin errores no manejados en los logs de n8n
```
