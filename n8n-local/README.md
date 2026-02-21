# Chatbot IA — Servicio de Alquiler de Lockers

Chatbot inteligente para WhatsApp con n8n como orquestador, IA híbrida (Groq + Claude Sonnet), y Supabase como base de datos.

## Stack

| Componente | Herramienta |
|-----------|-------------|
| Orquestador | n8n (self-hosted) |
| Canal | WhatsApp Business API (Meta Cloud API) |
| IA principal | Groq (llama-4-scout-17b-16e-instruct) |
| IA fallback | Claude Sonnet (Anthropic) |
| Audio → Texto | Groq Whisper (whisper-large-v3-turbo) |
| Base de datos | Supabase (Postgres) |
| Gestión | Telegram Bot |
| Vigilancia | Uptime Kuma |

## Estructura

```
n8n-local/
├── README.md                            # Este archivo
├── WhatsApp_starter_workflow.json       # Workflow existente (base)
├── database/
│   ├── 01_create_tables.sql             # Tablas principales
│   ├── 02_create_indexes.sql            # Índices de rendimiento
│   └── 03_message_metadata.sql          # Tabla de analítica (opcional)
├── workflows/
│   ├── chatbot-main.json                # Workflow principal (Módulos 1-5)
│   ├── error-handler.json               # Error workflow global
│   ├── telegram-commands.json           # Comandos de gestión por Telegram
│   ├── auto-expiration.json             # Expiración automática human takeover
│   ├── daily-summary.json               # Resumen diario de actividad
│   ├── groq-limits-alert.json           # Alerta de límites de Groq
│   └── cleanup-pending.json             # Limpieza diaria de pending_messages
├── prompts/
│   └── system-prompt.md                 # System prompt completo del bot
└── config/
    └── env.example                      # Variables de entorno necesarias
```

## Documentación Técnica

- Plan completo: `../.tasks/plan-tecnico-chatbot-n8n.md`
- Subtareas detalladas: `../.tasks/subtarea-XX-*.md`

## Estado del Proyecto

| # | Subtarea | Estado |
|---|----------|--------|
| 01 | Supabase (Base de datos) | ✅ Completada |
| 02 | Meta WhatsApp Cloud API | ⬜ Pendiente |
| 03 | Telegram Bot | ⬜ Pendiente |
| 04 | Uptime Kuma | ⬜ Pendiente |
| 05 | Contenido del Bot (System Prompt) | ⬜ Pendiente |
| 06 | Workflow Core (Módulos 1-4) | ⬜ Pendiente |
| 07 | Antiflood (Módulo 5) | ⬜ Pendiente |
| 08 | Escalado a Humano | ⬜ Pendiente |
| 09 | Monitorización y Alertas | ⬜ Pendiente |
| 10 | Testing | ⬜ Pendiente |
| 11 | Deploy a Producción | ⬜ Pendiente |
