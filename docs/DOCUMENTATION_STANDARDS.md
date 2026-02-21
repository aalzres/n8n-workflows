# Documentation Standards

---

## 1. Purpose

Define cómo se organiza, estructura y valida la documentación del proyecto **n8n-workflows**.
Este documento complementa el mapa definido en `docs/README.md`.

---

## 2. Canonical Structure

La estructura canónica está definida en `docs/README.md`.
Toda documentación y tooling **deben seguir esa estructura**.
No se permiten carpetas adicionales fuera del mapa definido.

---

## 3. Documentation Indexing

La documentación se indexa en:

- `docs/manifest.json`

Este fichero es el punto de entrada para tooling y sistemas automatizados (incluyendo agentes IA).

---

## 4. Document Types

### Design Doc (GDD)

Explica cómo funciona o debe funcionar el sistema.

**Responde a:**
- Qué problema resolvemos
- Cómo lo vamos a hacer
- Qué partes tiene
- Qué NO vamos a hacer

**Naming:** `docs/design/<slug>.md`  
**Front-matter obligatorio:** `status`, `tags`

---

### ADR (Architecture Decision Record)

Registro corto y permanente de una decisión técnica importante.

**Responde a:**
- Qué decisión tomamos
- Por qué la tomamos
- Qué alternativas consideramos
- Qué consecuencias tiene

**Naming:** `docs/adr/adr-NNN-<slug>.md`  
**Numeración:** secuencial, sin saltos.

---

### Runbook

Guía de acción para operar el sistema en producción.

**Responde a:**
- Qué está pasando (síntomas)
- Qué comprobar primero
- Qué pasos seguir
- Qué hacer si falla (rollback / escalado)

**Naming:** `docs/runbooks/runbook-<slug>.md`

---

### Agent Definition (Design Doc especializado)

Describe el rol, responsabilidades y protocolo de un agente IA.  
Se almacena en `docs/design/agent-<nombre>.md`.

**Responde a:**
- Cuál es el rol del agente
- Qué puede y qué NO puede hacer
- Cómo interactúa con otros agentes
- Qué protocolo de validación usa

---

## 5. Front-matter Metadata

Todo documento debe incluir front-matter YAML en la cabecera:

```yaml
---
title: "Título del documento"
status: draft | review | approved | deprecated
tags: [backend, security, infra, ...]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

### Valores de `status`

| Valor | Significado |
|-------|------------|
| `draft` | En elaboración, no usar como referencia |
| `review` | En revisión, pendiente de aprobación |
| `approved` | Aprobado, es la fuente de verdad |
| `deprecated` | Obsoleto, no usar |

---

## 6. Engineering Standards

Estándares técnicos de código. No describen el sistema, sino **cómo se desarrolla**.

- `docs/standards/engineering/python-style-guide.md`

---

## 7. Validators

Validadores automáticos ubicados en `docs/validators/`:

| Validador | Ruta | Valida |
|-----------|------|--------|
| GDD Validator | `validators/gdd/` | Estructura de Design Docs |
| ADR Validator | `validators/adr/` | Formato y numeración de ADRs |
| Runbook Validator | `validators/runbook/` | Completitud de runbooks |
| Global Validator | `validators/global/` | Front-matter y manifest |

---

## 8. Agent Protocol

Los agentes IA deben:

1. Leer `docs/manifest.json` para conocer todos los documentos disponibles.
2. Consultar el documento relevante antes de actuar.
3. **Nunca actuar sin validación explícita del usuario** (ver `design/agent-main-assistant.md`).
4. Documentar cualquier decisión técnica nueva como ADR.
5. Actualizar `manifest.json` cuando se crea o depreca un documento.
