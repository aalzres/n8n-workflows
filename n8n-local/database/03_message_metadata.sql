-- ============================================================
-- Chatbot Lockers — Tabla de Analítica de Mensajes
-- Subtarea 09: Metadata para monitorización avanzada
-- ============================================================
-- OPCIONAL: Ejecutar si se quiere analítica detallada.
-- Permite rastrear confidence, modelo usado, escalados, etc.
-- ============================================================

CREATE TABLE IF NOT EXISTS message_metadata (
    id              SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL
                    REFERENCES conversations(id)
                    ON DELETE CASCADE,
    intent          VARCHAR(50)
                    CHECK (intent IS NULL OR intent IN (
                        'info', 'booking', 'support', 'complaint', 'emergency'
                    )),
    confidence      DECIMAL(3,2)
                    CHECK (confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)),
    escalated       BOOLEAN DEFAULT FALSE,
    model_used      VARCHAR(50)
                    CHECK (model_used IS NULL OR model_used IN (
                        'groq-llama-4-scout', 'claude-sonnet', 'error-fallback'
                    )),
    tokens_input    INTEGER,
    tokens_output   INTEGER,
    response_time_ms INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE message_metadata IS 'Analítica detallada por mensaje: modelo, confianza, tiempos';
COMMENT ON COLUMN message_metadata.model_used IS 'Qué modelo generó la respuesta';
COMMENT ON COLUMN message_metadata.response_time_ms IS 'Tiempo de respuesta del modelo en ms';

-- ─── Índices para analítica ────────────────────────────────

-- Buscar por modelo usado (estadísticas de uso Groq vs Claude)
CREATE INDEX IF NOT EXISTS idx_meta_model
    ON message_metadata(model_used);

-- Buscar escalados (correlacionar con telegram notifications)
CREATE INDEX IF NOT EXISTS idx_meta_escalated
    ON message_metadata(escalated)
    WHERE escalated = TRUE;

-- Analítica por fecha
CREATE INDEX IF NOT EXISTS idx_meta_created
    ON message_metadata(created_at);

-- Buscar respuestas de baja confianza
CREATE INDEX IF NOT EXISTS idx_meta_low_confidence
    ON message_metadata(confidence)
    WHERE confidence < 0.7;
