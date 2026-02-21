# Documentación del Proyecto — n8n-workflows

> Punto de entrada y mapa de navegación de toda la documentación.

---

## Descripción del Proyecto

**n8n-workflows** es una plataforma de documentación y búsqueda para una colección de más de 4 343 workflows de automatización n8n. El sistema incluye:

- Una **API REST de alto rendimiento** (FastAPI + SQLite FTS5) para indexar, buscar y explorar workflows.
- Un **asistente de IA conversacional** para búsqueda en lenguaje natural.
- Un **motor de analíticas** sobre uso y patrones de workflows.
- Un sistema de **comunidad** (ratings, reviews, descargas).
- Un sistema de **gestión de usuarios** con autenticación JWT.
- Un **hub de integraciones** para sincronización con plataformas externas.
- Un **stack de IA local** (`ai-stack/`) con n8n + Agent Zero + ComfyUI.
- Un **subproyecto MEDCARDS.AI** (`medcards-ai/`): plataforma de preparación de residencia médica con Claude AI.
- Infraestructura completa: Docker, Kubernetes, Helm, GitHub Pages.

---

## Mapa de Navegación

```text
docs/
├─ README.md                        → Este archivo. Punto de entrada.
├─ DOCUMENTATION_STANDARDS.md       → Reglas y estándares de documentación.
├─ manifest.json                    → Índice de documentación (tooling / IA).
│
├─ design/                          → Design Docs (GDD). Sistema y arquitectura.
│  ├─ system-overview.md            → Visión general del sistema completo.
│  ├─ agent-main-assistant.md       → Agente orquestador principal (LEER PRIMERO).
│  ├─ agent-backend-api.md          → Agente especialista en API / Backend Python.
│  ├─ agent-devops.md               → Agente especialista en infraestructura / DevOps.
│  ├─ agent-frontend.md             → Agente especialista en Frontend / UI.
│  ├─ agent-ai-ml.md                → Agente especialista en IA y ML.
│  ├─ agent-security.md             → Agente especialista en seguridad.
│  ├─ agent-workflows.md            → Agente especialista en gestión de workflows n8n.
│  ├─ agent-database.md             → Agente especialista en base de datos.
│  └─ agent-community.md            → Agente especialista en comunidad y usuarios.
│
├─ adr/                             → Architecture Decision Records.
│  ├─ adr-001-sqlite-fts5.md
│  ├─ adr-002-fastapi-framework.md
│  ├─ adr-003-docker-containerization.md
│  └─ adr-004-jwt-authentication.md
│
├─ runbooks/                        → Guías operativas.
│  ├─ runbook-api-server.md
│  ├─ runbook-workflow-indexing.md
│  ├─ runbook-docker-deployment.md
│  └─ runbook-k8s-deployment.md
│
├─ brands/                          → Documentación por marca / subproyecto.
│  └─ medcards-ai.md
│
├─ standards/
│  ├─ documentation/
│  │  └─ rules.json                 → Reglas en formato machine-readable.
│  └─ engineering/
│     └─ python-style-guide.md
│
└─ validators/
   ├─ gdd/
   ├─ adr/
   ├─ runbook/
   └─ global/
```

---

## Stack Tecnológico Resumido

| Capa | Tecnología |
|------|-----------|
| API / Backend | Python 3.11, FastAPI, Uvicorn, Pydantic v2 |
| Base de datos | SQLite con FTS5 (full-text search) |
| Autenticación | JWT (PyJWT + passlib/bcrypt) |
| Frontend | HTML5 estático + GitHub Pages |
| Contenedores | Docker, Docker Compose (dev/prod) |
| Orquestación | Kubernetes + Helm |
| Proxy inverso | Traefik v2 |
| AI Stack | n8n 5678 · Agent Zero 50080 · ComfyUI 8188 |
| Subproyecto | Next.js 14, Supabase, Claude (Anthropic) |

---

## Flujo de Trabajo con los Agentes

```
Usuario
  │
  ▼
[agent-main-assistant] ← Orquestador. Valida cada acción con el usuario.
  │
  ├──► [agent-backend-api]       Para cambios en API / Python
  ├──► [agent-devops]            Para Docker / K8s / CI-CD
  ├──► [agent-frontend]          Para UI / estáticos / GitHub Pages
  ├──► [agent-ai-ml]             Para IA, analíticas, Agent Zero
  ├──► [agent-security]          Para seguridad, auth, vulnerabilidades
  ├──► [agent-workflows]         Para gestión de JSONs n8n
  ├──► [agent-database]          Para esquema SQLite, migraciones
  └──► [agent-community]         Para features comunitarias y usuarios
```

> **REGLA DE ORO**: Ningún agente especialista actúa sin la validación explícita del usuario a través del agente principal.

---

## Cómo empezar

1. Lee [`design/agent-main-assistant.md`](design/agent-main-assistant.md) — define el protocolo de trabajo.
2. Lee [`design/system-overview.md`](design/system-overview.md) — arquitectura general.
3. Consulta el agente especialista según el área de trabajo.
4. Ante cualquier duda técnica, revisa los ADRs correspondientes.
5. Para operaciones en producción, usa los runbooks.
