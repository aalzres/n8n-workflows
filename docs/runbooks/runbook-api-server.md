---
title: "Runbook: API Server"
status: approved
tags: [operations, api, server, fastapi, troubleshooting]
created: 2026-02-21
updated: 2026-02-21
---

# Runbook: API Server

## Síntomas Comunes

| Síntoma | Probable Causa |
|---------|---------------|
| `500 Internal Server Error` en todos los endpoints | DB no inicializada o corrupta |
| API devuelve `{"total": 0}` en `/api/stats` | Workflows no indexados todavía |
| Respuestas lentas (>500ms) | Cache SQLite frío o muchas conexiones concurrentes |
| `429 Too Many Requests` | Rate limit de 60 req/min alcanzado |
| Contenedor reiniciando en loop | HEALTHCHECK falla — ver logs |
| CORS error en browser | Origen no incluido en `ALLOWED_ORIGINS` |

---

## Diagnóstico Inicial

```bash
# 1. Verificar que el servidor responde
curl http://localhost:8000/health

# 2. Ver estadísticas de la DB
curl http://localhost:8000/api/stats

# 3. Ver logs del contenedor
docker logs n8n-workflows-docs --tail 50

# 4. Ver logs en tiempo real
docker logs n8n-workflows-docs -f
```

---

## Procedimientos

### P1: Servidor no arranca

1. Verificar logs de startup:
   ```bash
   docker logs n8n-workflows-docs 2>&1 | head -30
   ```
2. Si muestra `Database connection failed`: la DB no existe o está corrupta.
   - Solución: Lanzar el indexado (ver P3) y reiniciar.
3. Si muestra `Port already in use`:
   ```bash
   lsof -i :8000
   kill <PID>
   docker restart n8n-workflows-docs
   ```

---

### P2: Error 500 en endpoints

1. Revisar logs para el traceback:
   ```bash
   docker logs n8n-workflows-docs --tail 100 | grep -A 10 "ERROR\|Exception"
   ```
2. Verificar integridad de la DB:
   ```bash
   docker exec n8n-workflows-docs python -c \
     "import sqlite3; conn=sqlite3.connect('workflows.db'); print(conn.execute('PRAGMA integrity_check').fetchone())"
   ```
3. Si la DB está corrupta → restaurar desde backup (ver P5).

---

### P3: API devuelve 0 workflows

```bash
# Forzar reindexado
curl -X POST http://localhost:8000/api/workflows/index

# Verificar resultado
curl http://localhost:8000/api/stats
```

Si el reindexado falla, ver logs:
```bash
docker logs n8n-workflows-docs --tail 30
```

---

### P4: Rate limiting bloqueando requests legítimos

El rate limiting actual es por IP, 60 req/min.  
Si un cliente legítimo está siendo bloqueado:

1. Verificar en logs el IP del cliente.
2. Temporal: aumentar `MAX_REQUESTS_PER_MINUTE` en `api_server.py`:
   ```python
   MAX_REQUESTS_PER_MINUTE = 120  # Doblar el límite
   ```
3. Rebuild y redeploy del contenedor.
4. Largo plazo: migrar a rate limiting por usuario autenticado.

---

### P5: Restaurar desde backup

```bash
# Detener el servidor
docker stop n8n-workflows-docs

# Restaurar DB desde backup
docker run --rm -v workflows-db:/data -v $(pwd)/backup:/backup \
  alpine sh -c "cp /backup/workflows.db /data/workflows.db"

# Reiniciar
docker start n8n-workflows-docs
```

---

### P6: CORS error en browser

1. Identificar el origen exacto que está siendo bloqueado (ver `Origin` header en request).
2. Añadir a `ALLOWED_ORIGINS` en `api_server.py`.
3. Rebuild y redeploy.

---

## Rollback

Si un despliegue causa problemas:

```bash
# Volver a la imagen anterior
docker stop n8n-workflows-docs
docker run -d --name n8n-workflows-docs \
  -p 8000:8000 \
  -v workflows-db:/app/database \
  workflows-doc:<version-anterior>
```

---

## Escalado

Si el problema no se resuelve:
1. Capturar logs completos: `docker logs n8n-workflows-docs > logs.txt`
2. Capturar estado de la DB: `sqlite3 workflows.db ".dump" > dump.sql`
3. Escalar al equipo de desarrollo con ambos archivos.
