---
title: "Runbook: Despliegue Docker"
status: approved
tags: [operations, docker, deployment]
created: 2026-02-21
updated: 2026-02-21
---

# Runbook: Despliegue Docker

## Pre-requisitos

- Docker Engine 24+ y Docker Compose v2 instalados
- Puerto 8000 libre en el host
- Variables de entorno configuradas (ver sección Variables)

---

## Variables de Entorno Requeridas

| Variable | Descripción | Requerida en producción |
|----------|-------------|------------------------|
| `JWT_SECRET_KEY` | Clave secreta para firmar JWT | ✅ Sí |
| `ENVIRONMENT` | `development` \| `production` | Recomendado |
| `LOG_LEVEL` | `debug` \| `info` \| `warning` | Opcional |
| `WORKFLOW_DB_PATH` | Ruta personalizada para la DB | Opcional |

Configurar antes del despliegue:
```bash
export JWT_SECRET_KEY="tu-clave-secreta-aleatoria-min-32-chars"
export ENVIRONMENT="production"
```

---

## Procedimientos

### P1: Despliegue en Desarrollo

```bash
# 1. Build + start
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# 2. Indexar workflows (primera vez)
curl -X POST http://localhost:8000/api/workflows/index

# 3. Verificar
curl http://localhost:8000/health
```

---

### P2: Despliegue en Producción

```bash
# 1. Build de imagen
docker build -t workflows-doc:latest .

# 2. Escanear vulnerabilidades (obligatorio antes de producción)
trivy image workflows-doc:latest

# 3. Start en modo producción
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# 4. Verificar que el contenedor está healthy
docker ps | grep n8n-workflows-docs
# Debe mostrar: (healthy)

# 5. Indexar si es primer despliegue
curl -X POST http://localhost:8000/api/workflows/index

# 6. Verificar desde exterior
curl https://tudominio.com/health
```

---

### P3: Actualización (zero-downtime)

```bash
# 1. Build nueva imagen con tag de versión
docker build -t workflows-doc:v2.1.0 .

# 2. Test de la nueva imagen en staging
docker run --rm -p 8001:8000 workflows-doc:v2.1.0 &
curl http://localhost:8001/health
docker stop <contenedor-staging>

# 3. Desplegar con rolling update
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps --build workflows-docs

# 4. Verificar logs post-deploy
docker logs n8n-workflows-docs --tail 20
```

---

### P4: Backup de Datos

```bash
# Backup manual de la DB
bash scripts/backup.sh

# O manualmente
docker exec n8n-workflows-docs sqlite3 /app/database/workflows.db ".dump" > backup_$(date +%Y%m%d).sql
```

---

### P5: Rollback

```bash
# 1. Parar contenedor actual
docker stop n8n-workflows-docs && docker rm n8n-workflows-docs

# 2. Levantar versión anterior
docker run -d \
  --name n8n-workflows-docs \
  -p 8000:8000 \
  -v workflows-db:/app/database \
  -e JWT_SECRET_KEY="${JWT_SECRET_KEY}" \
  -e ENVIRONMENT="production" \
  workflows-doc:<version-anterior>

# 3. Verificar
curl http://localhost:8000/health
```

---

### P6: Parar el servicio

```bash
docker compose down
# Los volúmenes se conservan (no uses docker compose down -v en producción)
```

---

## Verificación Post-Despliegue

```bash
# Health check
curl http://localhost:8000/health

# Stats (confirmar DB conectada)
curl http://localhost:8000/api/stats | python -m json.tool

# Test de búsqueda
curl "http://localhost:8000/api/search?q=slack" | python -m json.tool

# Test de seguridad
bash test_security.sh
```
