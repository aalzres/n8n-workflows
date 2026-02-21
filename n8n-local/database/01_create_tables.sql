-- ============================================================
-- Chatbot Lockers — Esquema de Base de Datos
-- Subtarea 01: Tablas principales
-- ============================================================
-- Ejecutar en Supabase SQL Editor (en orden)
-- ============================================================

-- ─── 1. conversation_state ─────────────────────────────────
-- Estado actual de cada conversación activa por cliente.
-- Es el modelo central, identificado por client_phone.
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS conversation_state (
    client_phone VARCHAR(20) PRIMARY KEY,
    client_name  VARCHAR(100),
    status       VARCHAR(20) DEFAULT 'bot'
                 CHECK (status IN ('bot', 'human', 'closed')),
    current_intent VARCHAR(50)
                 CHECK (current_intent IS NULL OR current_intent IN (
                     'info', 'booking', 'support', 'complaint', 'emergency'
                 )),
    last_interaction TIMESTAMPTZ DEFAULT NOW(),
    metadata     JSONB DEFAULT '{}'::jsonb,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE conversation_state IS 'Estado actual de cada conversación activa por cliente';
COMMENT ON COLUMN conversation_state.status IS 'Quién gestiona: bot / human / closed';
COMMENT ON COLUMN conversation_state.current_intent IS 'Última intención detectada';
COMMENT ON COLUMN conversation_state.metadata IS 'Datos variables: idioma, nº interacciones, etc.';

-- ─── 2. conversations ──────────────────────────────────────
-- Historial completo de todos los mensajes intercambiados.
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS conversations (
    id           SERIAL PRIMARY KEY,
    client_phone VARCHAR(20) NOT NULL
                 REFERENCES conversation_state(client_phone)
                 ON DELETE CASCADE,
    role         VARCHAR(10) NOT NULL
                 CHECK (role IN ('user', 'assistant')),
    message      TEXT NOT NULL,
    timestamp    TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE conversations IS 'Historial completo de mensajes cliente ↔ bot';
COMMENT ON COLUMN conversations.role IS 'user = mensaje del cliente, assistant = respuesta del bot';

-- ─── 3. pending_messages ───────────────────────────────────
-- Buffer temporal para antiflood: agrupa mensajes rápidos
-- del mismo cliente antes de procesarlos como uno solo.
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pending_messages (
    id           SERIAL PRIMARY KEY,
    client_phone VARCHAR(20) NOT NULL
                 REFERENCES conversation_state(client_phone)
                 ON DELETE CASCADE,
    message      TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text'
                 CHECK (message_type IN ('text', 'audio', 'other')),
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    processed    BOOLEAN DEFAULT FALSE
);

COMMENT ON TABLE pending_messages IS 'Buffer antiflood: agrupa mensajes rápidos del mismo cliente';
COMMENT ON COLUMN pending_messages.processed IS 'true cuando ya se procesó como parte de un grupo';
