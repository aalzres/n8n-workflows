---
title: "ADR-001: SQLite con FTS5 para indexado y búsqueda de workflows"
status: approved
tags: [database, sqlite, fts5, search, performance]
created: 2026-02-21
updated: 2026-02-21
---

# ADR-001: SQLite con FTS5 para indexado y búsqueda de workflows

## Contexto

El repositorio contiene más de 4 343 archivos JSON de workflows n8n.  
Se necesita una solución de búsqueda que sea:
- Rápida (sub-100ms para el caso típico)
- Sin dependencias externas de servidor
- Full-text search sobre nombre, descripción, integraciones y tags
- Portable (funciona en Docker, VPS, K8s, GitHub Actions)

## Decisión

**Usar SQLite con extensión FTS5** como único motor de datos y búsqueda.

- Base: SQLite 3.x (incluida en Python stdlib)
- Tabla principal `workflows` con metadatos extraídos de los JSON
- Tabla virtual `workflows_fts` con FTS5 para búsqueda full-text
- WAL mode + cache en memoria para rendimiento
- Triggers para mantener FTS en sincronía

## Alternativas Consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| Elasticsearch | Dependencia de servidor externo, complejidad operacional |
| PostgreSQL | Sobrecarga para un repositorio estático/semi-estático |
| Meilisearch | Dependencia de proceso separado |
| Búsqueda en archivos (grep) | Demasiado lento para 4343 archivos |
| Redis Search | Sin persistencia nativa adecuada para este caso |

## Consecuencias

**Positivas:**
- Zero dependencias externas de base de datos
- Rendimiento sub-100ms verificado para búsquedas típicas
- Backup trivial: copiar un fichero `.db`
- Funciona sin conexión y en entornos con recursos limitados
- Indexado incremental via SHA-256 (solo reindexar lo que cambia)

**Negativas:**
- Sin soporte para búsqueda semántica/vectorial (requeriría pgvector u otro motor)
- Rate limiting por IP en memoria (no distribuido — problema para múltiples instancias)
- Escrituras serializadas (no apto para cargas de escritura muy intensas)

## Notas de Implementación

Ver [`docs/design/agent-database.md`](../design/agent-database.md) para el esquema completo y configuración de PRAGMAs.
