---
title: "Runbook: Indexado de Workflows"
status: approved
tags: [operations, indexing, database, workflows]
created: 2026-02-21
updated: 2026-02-21
---

# Runbook: Indexado de Workflows

## Síntomas que requieren este runbook

| Síntoma | Cuándo actuar |
|---------|--------------|
| `/api/stats` devuelve `total: 0` | Primer despliegue o DB nueva |
| Workflows nuevos no aparecen en búsqueda | Tras añadir archivos JSON |
| Búsqueda FTS devuelve resultados desactualizados | Tras modificar archivos JSON |
| `Warning: No workflows found in database` en startup | DB vacía |

---

## Diagnóstico

```bash
# ¿Cuántos workflows hay en la DB?
curl http://localhost:8000/api/stats | python -m json.tool

# ¿Cuántos JSON hay en disco?
find workflows/ -name "*.json" | wc -l

# Si los números no coinciden → necesitas reindexar
```

---

## Procedimientos

### P1: Indexado Completo (primer despliegue)

```bash
# Via API
curl -X POST http://localhost:8000/api/workflows/index

# Verificar progreso en logs
docker logs n8n-workflows-docs -f

# Esperar a que aparezca: "✅ Indexed N workflows"
# Verificar resultado
curl http://localhost:8000/api/stats
```

---

### P2: Reindexado Incremental (tras añadir/modificar workflows)

El indexado es incremental por defecto (usa SHA-256 para detectar cambios).

```bash
# Simplemente llamar al mismo endpoint — sólo procesa los archivos modificados
curl -X POST http://localhost:8000/api/workflows/index
```

---

### P3: Reindexado Forzado (ignorar hashes)

Si sospechas que los hashes están desincronizados:

```bash
# Dentro del contenedor
docker exec -it n8n-workflows-docs python -c "
from workflow_db import WorkflowDatabase
db = WorkflowDatabase()
# Limpiar tabla para forzar reindexado completo
import sqlite3
conn = sqlite3.connect(db.db_path)
conn.execute('DELETE FROM workflows')
conn.execute('DELETE FROM workflows_fts')
conn.commit()
conn.close()
print('Tabla limpiada')
"

# Ahora reindexar
curl -X POST http://localhost:8000/api/workflows/index
```

---

### P4: Rebuild del índice FTS5

Si la búsqueda full-text da resultados inconsistentes:

```bash
docker exec -it n8n-workflows-docs python -c "
import sqlite3
conn = sqlite3.connect('workflows.db')
conn.execute(\"INSERT INTO workflows_fts(workflows_fts) VALUES('rebuild')\")
conn.commit()
conn.close()
print('FTS5 index rebuilt')
"
```

---

### P5: Añadir workflows nuevos al repositorio

1. Copiar los `.json` a la subcarpeta correcta de `workflows/`:
   ```bash
   cp nuevo_workflow.json workflows/NuevaCategoria/
   ```
2. Validar estructura:
   ```bash
   python test_workflows.py
   ```
3. Reindexar:
   ```bash
   curl -X POST http://localhost:8000/api/workflows/index
   ```
4. Verificar en búsqueda:
   ```bash
   curl "http://localhost:8000/api/search?q=nombre_del_workflow"
   ```

---

## Tiempos Esperados

| Operación | Tiempo estimado |
|-----------|----------------|
| Indexado completo de 4343 workflows | 2–5 minutos |
| Reindexado incremental (sin cambios) | < 10 segundos |
| Rebuild FTS5 | < 30 segundos |

---

## Rollback

Si el indexado corrompe la DB:

```bash
# Parar el servidor
docker stop n8n-workflows-docs

# Restaurar desde backup
bash scripts/backup.sh restore

# Reiniciar
docker start n8n-workflows-docs
```
