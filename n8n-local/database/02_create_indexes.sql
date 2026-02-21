-- ============================================================
-- Chatbot Lockers — Índices de Rendimiento
-- Subtarea 01: Índices para consultas frecuentes
-- ============================================================
-- Ejecutar DESPUÉS de 01_create_tables.sql
-- ============================================================

-- ─── Índices para conversations ────────────────────────────

-- Búsqueda de historial por teléfono (usado en cada request)
CREATE INDEX IF NOT EXISTS idx_conv_phone
    ON conversations(client_phone);

-- Ordenar por timestamp (obtener últimos 20 mensajes)
CREATE INDEX IF NOT EXISTS idx_conv_timestamp
    ON conversations(timestamp DESC);

-- Índice compuesto: historial de un cliente ordenado (consulta más frecuente)
CREATE INDEX IF NOT EXISTS idx_conv_phone_timestamp
    ON conversations(client_phone, timestamp DESC);

-- Contar mensajes por día (resumen diario)
CREATE INDEX IF NOT EXISTS idx_conv_role_timestamp
    ON conversations(role, timestamp);

-- ─── Índices para pending_messages ─────────────────────────

-- Buscar pendientes de un cliente (antiflood)
CREATE INDEX IF NOT EXISTS idx_pending_phone
    ON pending_messages(client_phone);

-- Filtrar por procesados (limpieza diaria)
CREATE INDEX IF NOT EXISTS idx_pending_processed
    ON pending_messages(processed);

-- Índice compuesto: pendientes sin procesar de un cliente (consulta antiflood)
CREATE INDEX IF NOT EXISTS idx_pending_phone_unprocessed
    ON pending_messages(client_phone, processed)
    WHERE processed = FALSE;

-- ─── Índices para conversation_state ───────────────────────

-- Buscar conversaciones escaladas a humano
CREATE INDEX IF NOT EXISTS idx_state_status
    ON conversation_state(status);

-- Buscar conversaciones expiradas (cron de expiración)
CREATE INDEX IF NOT EXISTS idx_state_last_interaction
    ON conversation_state(last_interaction);
