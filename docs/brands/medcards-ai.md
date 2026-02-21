---
title: "MEDCARDS.AI — Documentación del Subproyecto"
status: approved
tags: [brand, medcards, nextjs, supabase, claude, medical, brazil]
created: 2026-02-21
updated: 2026-02-21
---

# MEDCARDS.AI

> Plataforma de preparación para residencia médica brasileña con IA.

---

## 1. Visión del Producto

**MEDCARDS.AI** es un compañero de estudio inteligente que se adapta al recorrido de aprendizaje de cada estudiante.  
No es un curso tradicional: es un coach de IA con memoria completa del alumno.

### Tres pantallas core

| Pantalla | Nombre | Función |
|----------|--------|---------|
| 1 | **Battle Dashboard** | Métricas de competencia clínica en tiempo real |
| 2 | **Training Arena** | Casos clínicos adaptativos con feedback de IA |
| 3 | **War Room** | Tutor personal IA con memoria completa |

---

## 2. Stack Tecnológico

```
Frontend:  Next.js 14 (App Router) + Tailwind CSS + Shadcn UI
Backend:   Next.js Server Actions (fullstack en un solo codebase)
Database:  Supabase (PostgreSQL + Auth + RLS + Real-time)
AI:        Anthropic Claude Sonnet 4
Deploy:    Vercel (push-to-deploy)
```

### Por qué este stack

| Decisión | Razón |
|----------|-------|
| Next.js 14 App Router | Server Components + Server Actions = fullstack sin API layer separada |
| Supabase | Auth built-in, RLS para multi-tenant, real-time subscriptions |
| Shadcn UI | Componentes copy-paste, fácil customización |
| Claude AI | Mejor razonamiento para educación médica |
| Vercel | Deploy en 30 min desde cero a producción |

---

## 3. Estructura del Proyecto

```
medcards-ai/
├── src/
│   ├── app/
│   │   ├── (auth)/          → Login / Register
│   │   ├── dashboard/       → Battle Dashboard
│   │   ├── arena/           → Training Arena
│   │   ├── war-room/        → AI Tutor Chat
│   │   └── layout.tsx       → Root layout
│   ├── components/
│   │   ├── ui/              → Shadcn UI components
│   │   ├── dashboard/       → Componentes del dashboard
│   │   └── arena/           → Componentes del arena
│   └── lib/
│       ├── supabase/        → Client y Server Supabase clients
│       ├── claude/          → Integración con Anthropic Claude API
│       └── utils/           → Utilidades compartidas
├── supabase/
│   ├── migrations/          → Migraciones de esquema
│   └── seed.sql             → Datos iniciales
├── prompts/                 → Prompts del sistema para Claude
├── next.config.ts           → Configuración Next.js
├── tailwind.config.ts       → Configuración Tailwind
└── package.json
```

---

## 4. Modelo de Datos (Supabase/PostgreSQL)

Entidades principales:
- **users** (auth.users via Supabase Auth)
- **profiles** — Perfil extendido del estudiante
- **sessions** — Sesiones de estudio
- **clinical_cases** — Casos clínicos generados
- **responses** — Respuestas del estudiante
- **competencies** — Métricas de competencia por área médica
- **conversations** — Historial del War Room (AI Tutor)

---

## 5. Integración con Claude AI

Los prompts del sistema se encuentran en `medcards-ai/prompts/`.

El modelo utilizado: **Claude Sonnet 4** (claude-sonnet-4-20250514 o más reciente).

### Casos de uso de IA

| Caso | Descripción |
|------|-------------|
| Generación de casos clínicos | Claude genera casos adaptados al nivel del estudiante |
| Evaluación de respuestas | Claude evalúa y da feedback detallado |
| War Room (tutor) | Conversación continua con memoria de sesión |
| Análisis de patrones | Identifica áreas débiles del estudiante |

---

## 6. Despliegue

```bash
# Desarrollo local
cd medcards-ai
npm install
cp .env.example .env.local    # Configurar NEXT_PUBLIC_SUPABASE_URL, etc.
npm run dev                   # http://localhost:3000

# Producción (Vercel)
# Push a main branch → Vercel auto-despliega
```

Variables de entorno requeridas:
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
ANTHROPIC_API_KEY=
```

---

## 7. Relación con el Proyecto Principal

MEDCARDS.AI es un **subproyecto independiente** que convive en el mismo repositorio.  
No comparte código con el backend FastAPI ni con la colección de workflows n8n.  
Tiene su propio ciclo de despliegue, base de datos, y stack tecnológico.

---

## 8. Links de Referencia

- `medcards-ai/EXECUTIVE_SUMMARY.md` — Resumen ejecutivo del producto
- `medcards-ai/PRODUCT_STRATEGY.md` — Estrategia de producto
- `medcards-ai/SCALABILITY_ARCHITECTURE.md` — Arquitectura de escalabilidad
