---
title: "ADR-003: Docker para contenedorización"
status: approved
tags: [docker, infrastructure, deployment, security]
created: 2026-02-21
updated: 2026-02-21
---

# ADR-003: Docker para contenedorización

## Contexto

El proyecto necesita una forma de empaquetar y desplegar la aplicación de forma reproducible en distintos entornos (local, VPS, cloud, K8s).

## Decisión

**Usar Docker con Docker Compose** como estrategia de contenedorización.

- Imagen base: `python:3.11-slim-bookworm` (balanceo seguridad/tamaño)
- Multi-environment: `docker-compose.yml` (base) + overrides `dev` y `prod`
- Traefik como reverse proxy en producción
- Kubernetes + Helm para orquestación avanzada

## Alternativas Consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| Despliegue bare-metal (systemd) | Menos portable, gestión de dependencias compleja |
| PaaS (Heroku, Railway) | Vendor lock-in, coste a escala |
| Podman | Ecosistema más pequeño, Docker es el estándar de facto |

## Consecuencias

**Positivas:**
- Entorno reproducible en cualquier máquina con Docker instalado
- Separación clara dev/prod con override files
- Non-root user en contenedor reduce superficie de ataque
- HEALTHCHECK integrado para restart automático en fallos
- Volúmenes nombrados para persistencia de datos

**Negativas:**
- Requiere Docker Desktop en macOS/Windows (licencia commercial para empresas grandes)
- El HEALTHCHECK usa `requests` dentro del contenedor — añade pequeña latencia en startup

## Notas de Implementación

Ver [`docs/design/agent-devops.md`](../design/agent-devops.md) y [`docs/runbooks/runbook-docker-deployment.md`](../runbooks/runbook-docker-deployment.md) para instrucciones detalladas.
