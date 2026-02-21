# n8n-workflows Repository

## Overview

Repositorio de automatización n8n con 4343+ workflows, API de búsqueda FastAPI, y documentación en GitHub Pages.

## Stack Tecnológico

- **Backend**: Python FastAPI + SQLite FTS5 (Full-Text Search)
- **Frontend**: HTML vanilla + CSS + JS puro (sin frameworks)
- **Infraestructura**: Docker + Kubernetes + Helm
- **AI Stack**: n8n + Agent Zero + ComfyUI (en `ai-stack/`)
- **Publicación**: GitHub Pages (`docs/`)

## Estructura del Repositorio

```
n8n-workflows/
├── .claude/agents/          # Sub-agentes de Claude (detección automática)
├── api_server.py            # API REST principal (FastAPI)
├── run.py                   # Entry point del servidor
├── workflow_db.py           # Capa de acceso a datos SQLite
├── src/                     # Módulos Python (AI, analytics, community, users)
├── static/                  # SPA del buscador de workflows (HTML puro)
├── workflows/               # 4343+ JSONs de n8n organizados por integración
├── context/                 # Categorías y datos de índice de búsqueda
├── docs/                    # GitHub Pages + documentación API
├── k8s/                     # Manifests Kubernetes
├── helm/                    # Helm chart
├── ai-stack/                # Stack IA local (n8n + Agent Zero + ComfyUI)
├── scripts/                 # Deploy, backup, health-check, indexado
├── templates/               # Templates de workflows reutilizables
├── Dockerfile               # Imagen de producción
├── docker-compose*.yml      # Entornos Docker (base, dev, prod)
└── test_*.sh / test_*.py    # Tests de API y seguridad
```

## URLs del Proyecto

| Entorno | URL |
|---------|-----|
| API local | `http://localhost:8000` |
| GitHub Pages | `https://zie619.github.io/n8n-workflows` |
| AI Stack (n8n) | `http://localhost:5678` |
| AI Stack (Agent Zero) | `http://localhost:50080` |

## Formato de Workflows n8n

Cada JSON en `workflows/` contiene: `name`, `nodes` (array de operaciones), `connections` (flujo entre nodos), `settings`, `tags`, `createdAt/updatedAt`.

### Tipos de Nodo Comunes
- **Trigger**: webhook, cron, manual
- **Integración**: HTTP Request, conectores de BD, APIs
- **Lógica**: IF, Switch, Merge, Loop
- **Datos**: Function, Set, Transform Data
- **Comunicación**: Email, Slack, Discord

### Patrones Comunes
- **Data Pipeline**: Trigger → Fetch → Transform → Store/Send
- **Integration Sync**: Cron → API Call → Compare → Update
- **Automation**: Webhook → Process → Conditional → Actions
- **Monitoring**: Schedule → Check Status → Alert

## Seguridad

- Rate limiting: 60 req/min por IP (in-memory)
- Path traversal: `validate_filename()` con triple decodificación URL
- CORS restringido a orígenes específicos
- JWT con HS256 + bcrypt para contraseñas
- Docker: usuario no-root `appuser` (UID 1001)
- Credenciales de workflows almacenadas en n8n, no en los JSON

# Agentes Sub-Especializados

Este proyecto usa **sub-agentes de Claude** ubicados en `.claude/agents/`. Cada agente tiene un dominio claro de responsabilidad.

## Estructura de Agentes

```
.claude/agents/
├── main-assistant.md   # Orquestador principal — punto de entrada para toda tarea
├── backend-api.md      # API FastAPI, Python, endpoints, middleware
├── database.md         # SQLite, FTS5, esquema, migraciones
├── frontend.md         # HTML/CSS/JS, GitHub Pages, UI estática
├── ai-ml.md            # IA conversacional, analytics, ai-stack
├── security.md         # Auth JWT, rate limiting, CVEs, hardening
├── devops.md           # Docker, Kubernetes, Helm, CI/CD, scripts
├── community.md        # Ratings, reviews, gestión de usuarios
└── workflows.md        # Colección JSON n8n, categorías, indexado
```

**Documentación técnica del sistema**: `docs/design/system-overview.md`

## Cómo Operan los Agentes

- El **main-assistant** es el orquestador: analiza la petición, elige el especialista y ejecuta de forma autónoma hasta completar la tarea.
- Los agentes **no bloquean el flujo** pidiendo confirmación en cada paso — actúan y reportan al final.
- Solo piden confirmación explícita ante acciones destructivas e irreversibles.

## Helpful Context for AI Assistants

When assisting with this repository:

1. **Workflow Analysis**: Focus on understanding the business purpose by examining the node flow, not just individual nodes.

2. **Documentation Generation**: Create descriptions that explain what the workflow accomplishes, not just what nodes it contains.

3. **Troubleshooting**: Common issues include:
   - Incorrect node connections
   - Missing error handling
   - Inefficient data processing in loops
   - Hardcoded values that should be parameters

4. **Optimization Suggestions**:
   - Identify redundant operations
   - Suggest batch processing where applicable
   - Recommend error handling additions
   - Propose splitting complex workflows

5. **Code Generation**: When creating tools to analyze these workflows:
   - Handle various n8n format versions
   - Account for custom nodes
   - Parse expressions in node parameters
   - Consider node execution order

# Repository-Specific Information

- **Stack**: Python FastAPI + SQLite FTS5 + HTML vanilla + Docker
- **Workflows**: 4343+ JSONs n8n organizados por integración en `workflows/`
- **API URL local**: `http://localhost:8000`
- **GitHub Pages**: `https://zie619.github.io/n8n-workflows`

# Version Compatibility

- n8n version: Compatible con n8n v1.x
- Last updated: 2026-02-21

[中文](./CLAUDE_ZH.md)