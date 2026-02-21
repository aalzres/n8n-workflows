---
title: "ADR-002: FastAPI como framework de API"
status: approved
tags: [api, fastapi, python, async, pydantic]
created: 2026-02-21
updated: 2026-02-21
---

# ADR-002: FastAPI como framework de API

## Contexto

Se necesita un framework Python para exponer la colección de workflows como una API REST performante, con validación de datos, documentación automática y soporte async.

## Decisión

**Usar FastAPI 0.109.x** como framework principal de API.

Stack:
- FastAPI + Uvicorn (ASGI server)
- Pydantic v2 para validación y serialización
- Gunicorn como gestor de procesos en producción

## Alternativas Consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| Flask | Sin async nativo, validación manual, sin OpenAPI auto |
| Django REST Framework | Demasiado opinionado y pesado para este caso de uso |
| Starlette (raw) | FastAPI es Starlette + extras útiles; no había razón para bajar de nivel |
| aiohttp | Menos ergonómico, sin validación automática |

## Consecuencias

**Positivas:**
- Documentación OpenAPI/Swagger generada automáticamente en `/docs`
- Validación de inputs y outputs via Pydantic v2 (rápido, tipado)
- Async/await nativo para operaciones I/O sin bloquear
- GZip middleware incluido para comprimir respuestas grandes
- CORS middleware configurable

**Negativas:**
- Pydantic v2 tiene breaking changes respecto a v1 (migración resuelta con `field_validator`)
- El logging con `print()` no es robusto para producción — pendiente de migrar a `logging`

## Notas de Implementación

- `@app.on_event("startup")` valida la conectividad con la DB al arrancar.
- Los endpoints usan modelos Pydantic como tipo de retorno — Pydantic serializa automáticamente.
- Rate limiting implementado manualmente (no con middleware externo) para evitar dependencias.
