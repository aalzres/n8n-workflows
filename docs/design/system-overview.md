---
title: "Visión General del Sistema — n8n-workflows"
status: approved
tags: [architecture, overview, system]
created: 2026-02-21
updated: 2026-02-21
---

# Visión General del Sistema

## 1. Problema que resolvemos

Gestionar, descubrir y documentar más de 4 343 workflows de automatización n8n de forma eficiente.
El repositorio sin indexado es innavegable. Se necesita:

- Búsqueda rápida (full-text + filtros).
- Documentación navegable online (GitHub Pages).
- Interfaz de consulta en lenguaje natural (chat AI).
- Analíticas de patrones de uso y complejidad.
- Comunidad: ratings, reviews, descargas.
- Gestión de usuarios y acceso.

---

## 2. Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE / USUARIO                        │
│   Browser (static/index.html)   ·   Mobile (mobile-app.html)   │
│   GitHub Pages (docs/)          ·   API clients directos        │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP / REST
┌────────────────────────────▼────────────────────────────────────┐
│                    TRAEFIK (Reverse Proxy)                       │
│                    Ports: 80, 443, 8080                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                   FastAPI Application :8000                      │
│                                                                 │
│  api_server.py          ← Core API (search, list, detail)      │
│  src/enhanced_api.py    ← API v2 (advanced filters, community) │
│  src/ai_assistant.py    ← Chat AI (workflow discovery)         │
│  src/analytics_engine.py← Analytics engine                     │
│  src/user_management.py ← Auth / JWT / Users                   │
│  src/community_features.py ← Ratings, Reviews                  │
│  src/integration_hub.py ← GitHub sync + external platforms     │
│  src/performance_monitor.py ← Metrics + health                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    PERSISTENCE LAYER                             │
│                                                                 │
│  workflow_db.py         ← WorkflowDatabase (SQLite + FTS5)     │
│  workflows.db           ← Indexed workflow metadata            │
│  users.db               ← User accounts                        │
│  workflows/ (4343 JSON) ← Source of truth (raw files)         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Componentes Principales

### 3.1 API Core (`api_server.py`)

FastAPI con:
- Endpoints: `/api/workflows`, `/api/search`, `/api/stats`, `/api/workflow/{file}`
- Rate limiting por IP (60 req/min)
- CORS restringido a dominios conocidos
- GZip middleware para performance
- Validación de filenames contra path traversal
- Startup: verifica conectividad DB

### 3.2 Base de Datos (`workflow_db.py`)

- SQLite con WAL mode y cache en memoria
- Tabla `workflows` con metadatos indexados
- Tabla virtual FTS5 `workflows_fts` para búsqueda full-text
- Triggers para mantener FTS en sinc
- Índices en: `trigger_type`, `complexity`, `active`, `node_count`, `filename`
- Hash de archivo para detección incremental de cambios

### 3.3 AI Assistant (`src/ai_assistant.py`)

- Búsqueda inteligente por intención (automation / integration / manual)
- Extracción de keywords por dominio
- Historial de conversación por `user_id`
- Respuesta incluye: texto, workflows sugeridos, suggestions, confidence score

### 3.4 Analytics Engine (`src/analytics_engine.py`)

- Estadísticas globales: total, activos, distribución por trigger y complejidad
- Estadísticas de nodos: avg, min, max
- Análisis de integraciones: top integrations, únicos
- Patrones de workflow: más complejos, con más integraciones

### 3.5 Enhanced API v2 (`src/enhanced_api.py`)

- Búsqueda avanzada: filtros múltiples, sort, pagination
- Recomendaciones por intereses del usuario
- Integra `CommunityFeatures`

### 3.6 Community Features (`src/community_features.py`)

- Ratings 1–5 estrellas por workflow y usuario
- Reviews con votos "helpful"
- Estadísticas de vistas y descargas por workflow
- Tablas: `workflow_ratings`, `workflow_stats`

### 3.7 User Management (`src/user_management.py`)

- Registro y login con hash bcrypt
- JWT con expiración configurable (30 min default via env)
- Roles: `user`, `admin`
- `SECRET_KEY` desde env var o token aleatorio generado en arranque

### 3.8 Integration Hub (`src/integration_hub.py`)

- Sincronización con repositorios GitHub (lista de workflow JSONs)
- Registro de integraciones externas (API key + base URL)
- Webhook dispatcher

---

## 4. Flujo de Indexado

```
workflows/*.json
      │
      ▼
workflow_db.py :: index_workflows()
  - Lee cada JSON
  - Extrae metadatos (name, nodes, triggers, tags, complejidad)
  - Calcula file_hash (SHA-256)
  - Salta archivos sin cambios (incremental)
  - Inserta/actualiza en tabla 'workflows'
  - Triggers actualizan FTS5
      │
      ▼
workflows.db (tabla: workflows + workflows_fts)
```

---

## 5. Frontend

| Archivo | Descripción |
|---------|-------------|
| `static/index.html` | SPA principal (búsqueda, browse, detalle) |
| `static/mobile-interface.html` | Interfaz optimizada para móvil |
| `static/mobile-app.html` | App móvil PWA |
| `static/index-nodejs.html` | Versión Node.js del frontend |
| `docs/` | Sitio GitHub Pages (HTML + CSS + JS estático) |

---

## 6. Infraestructura

### Docker Compose

| Archivo | Entorno |
|---------|---------|
| `docker-compose.yml` | Base |
| `docker-compose.dev.yml` | Dev (auto-reload) |
| `docker-compose.prod.yml` | Producción (Traefik + SSL) |

### Kubernetes

```
k8s/
├── namespace.yaml
├── configmap.yaml
├── deployment.yaml
├── service.yaml
└── ingress.yaml
```

### Helm Chart

```
helm/workflows-docs/
```

---

## 7. AI Stack Independiente (`ai-stack/`)

Stack Docker auto-contenido con:

| Servicio | Puerto | Rol |
|---------|--------|-----|
| n8n | 5678 | Motor de workflows |
| Agent Zero | 50080 | Runtime de agentes IA + UI de planificación |
| ComfyUI | 8188 | Generación de imágenes/video con IA |

Lanzamiento: `./start.sh` (Linux/macOS) o `.\start.ps1` (Windows).

---

## 8. Subproyecto MEDCARDS.AI (`medcards-ai/`)

Plataforma independiente de preparación para residencia médica brasileña.
Ver [`docs/brands/medcards-ai.md`](../brands/medcards-ai.md) para detalles completos.

Stack: Next.js 14 · Supabase · Tailwind · Shadcn UI · Claude (Anthropic).

---

## 9. Lo que NO hace este sistema

- No ejecuta workflows n8n (solo los documenta y sirve búsqueda).
- No gestiona credenciales de los workflows (las credenciales están en n8n, no en los JSON).
- No es un editor visual de workflows (para eso existe el propio n8n).
- La AI Assistant no usa LLM externo; usa búsqueda heurística en SQLite.
