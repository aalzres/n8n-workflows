# Subtarea 11: Deploy a Producción

## Objetivo
Bot activado en producción con el número real de WhatsApp, monitorización activa y plan de rollback.

## Dependencias
- **Subtarea 10** — Todos los tests pasados

---

## Pasos

### 1. Pre-deploy checklist

Verificar antes de activar:

```
[ ] Todos los tests de la subtarea 10 pasados
[ ] System prompt revisado y probado con datos reales del negocio
[ ] Número de WhatsApp de producción verificado en Meta
[ ] Webhook apuntando al workflow correcto
[ ] Todas las credenciales son de producción (no de test)
[ ] Templates de mensaje aprobados por Meta
[ ] Uptime Kuma monitorizando
[ ] Error Workflow activo
[ ] Workflows de monitorización activos (resumen diario, alertas de límites)
[ ] Workflow de expiración automática activo
[ ] Workflow de comandos de Telegram activo
```

### 2. Activar el workflow principal

1. Verificar que el workflow principal está en modo **Active**
2. Verificar que todos los workflows auxiliares están activos:
   - Error Handler
   - Comandos de Telegram
   - Expiración automática
   - Alerta de límites Groq
   - Resumen diario
   - Limpieza de pending_messages

### 3. Primer mensaje de prueba en producción

1. Enviar un mensaje real desde un número de prueba al número de producción
2. Verificar respuesta
3. Verificar que se guarda en Supabase
4. Verificar que no hay errores en los logs de n8n

### 4. Monitorización día 1

Durante las primeras 24 horas, monitorizar activamente:

| Qué vigilar | Cómo | Frecuencia |
|-------------|------|-----------|
| Errores en n8n | Logs de n8n + alertas 🔴 en Telegram | Continuo |
| Respuestas del bot | Revisar conversations en Supabase | Cada 2-3 horas |
| Calidad de respuestas | Leer respuestas reales del bot | Cada 2-3 horas |
| Escalados | Notificaciones 🟡 en Telegram | Continuo |
| Uso de Groq | Alerta ⚠️ en Telegram | Automático |
| Uptime de n8n | Uptime Kuma | Automático |

### 5. Ajustes post-deploy

Es normal tener que ajustar después de las primeras conversaciones reales:

| Problema detectado | Acción |
|-------------------|--------|
| Bot responde algo incorrecto | Ajustar system prompt o contexto del negocio |
| Pregunta frecuente que no sabe responder | Añadir al documento de contexto |
| Escalado innecesario (confidence bajo en algo fácil) | Añadir ejemplo few-shot al system prompt |
| No escala cuando debería | Ajustar reglas de escalado o añadir ejemplo |
| Formato de respuesta inadecuado (muy largo, muy formal) | Ajustar instrucciones de tono en system prompt |

### 6. Plan de rollback

Si algo va gravemente mal:

1. **Desactivar** el workflow principal en n8n (el bot deja de responder)
2. Los clientes que escriban no recibirán respuesta
3. Revisar el problema en los logs
4. Corregir
5. Reactivar

**Alternativa — Mensaje de mantenimiento:**

En lugar de desactivar completamente, modificar el workflow para que responda con un mensaje genérico:

> "Estamos realizando mejoras en nuestro sistema. Por favor, contacta con nosotros en [TELÉFONO] o inténtalo de nuevo en unos minutos. Disculpa las molestias 🙏"

---

## Verificación

```
[ ] Pre-deploy checklist completado
[ ] Workflow principal activo en producción
[ ] Todos los workflows auxiliares activos
[ ] Primer mensaje de prueba en producción exitoso
[ ] Primeras 24h monitorizadas
[ ] Resumen diario del día 1 recibido en Telegram
[ ] Ajustes post-deploy documentados y aplicados
[ ] Plan de rollback probado (desactivar/reactivar)
[ ] Bot estable y operativo
```
