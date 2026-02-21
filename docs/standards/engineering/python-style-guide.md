---
title: "Python Style Guide"
status: approved
tags: [standards, python, code-style, engineering]
created: 2026-02-21
updated: 2026-02-21
---

# Python Style Guide

Estándares de código Python para el proyecto n8n-workflows.

---

## 1. Formato

- **PEP 8** como base. Sin excepciones.
- Longitud máxima de línea: **88 caracteres** (black default).
- Formatter: `black` (si se instala en el proyecto).
- Indent: 4 espacios (nunca tabs).

---

## 2. Imports

Orden obligatorio (isort):
```python
# 1. Stdlib
import os
import json
from pathlib import Path

# 2. Third-party
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 3. Local
from workflow_db import WorkflowDatabase
```

No usar `from module import *`.

---

## 3. Type Hints

- Usar type hints en **todas** las funciones y métodos públicos.
- Usar `Optional[X]` en lugar de `X | None` (compatibilidad Python 3.9).
- Usar `List`, `Dict`, `Tuple` de `typing` (no built-ins) para Python < 3.10.

```python
# ✅ Correcto
def get_workflows(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    ...

# ❌ Incorrecto
def get_workflows(query, limit=10):
    ...
```

---

## 4. Naming Conventions

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Variables | `snake_case` | `workflow_id` |
| Funciones | `snake_case` | `get_workflow()` |
| Clases | `PascalCase` | `WorkflowDatabase` |
| Constantes | `UPPER_SNAKE_CASE` | `MAX_REQUESTS_PER_MINUTE` |
| Archivos | `snake_case.py` | `workflow_db.py` |
| Módulos | `snake_case` | `analytics_engine` |

---

## 5. Docstrings

Formato Google Style para todas las funciones públicas:

```python
def index_workflows(self, force: bool = False) -> int:
    """Indexa todos los workflows JSON en la base de datos.

    Args:
        force: Si True, reindexar todos los archivos ignorando hashes.

    Returns:
        Número de workflows indexados/actualizados.

    Raises:
        FileNotFoundError: Si el directorio workflows/ no existe.
    """
```

---

## 6. Error Handling

- Siempre usar `raise HTTPException(...)` en handlers FastAPI, nunca `return error`.
- Capturar excepciones específicas, no `except Exception` genérico salvo en top-level.
- Logear el error antes de re-lanzar.

```python
# ✅ Correcto
try:
    result = db.get_workflow(filename)
except FileNotFoundError:
    raise HTTPException(status_code=404, detail=f"Workflow '{filename}' not found")

# ❌ Incorrecto
try:
    result = db.get_workflow(filename)
except:
    return {"error": "something went wrong"}
```

---

## 7. Seguridad

- **Nunca** hardcodear credenciales, API keys, o secretos. Usar `os.environ.get()`.
- **Siempre** validar y sanitizar inputs externos antes de usarlos en queries SQL.
- Usar `parametrized queries` en SQLite (nunca f-strings en SQL con input de usuario).

```python
# ✅ Correcto
cursor.execute("SELECT * FROM workflows WHERE name = ?", (user_input,))

# ❌ PELIGROSO - SQL Injection
cursor.execute(f"SELECT * FROM workflows WHERE name = '{user_input}'")
```

---

## 8. Async

- Usar `async def` para todos los handlers FastAPI.
- Usar `await` para operaciones I/O (HTTP, DB async, filesystem).
- **Nota**: Las operaciones SQLite actuales son síncronas — para alta concurrencia, considerar `aiosqlite`.

---

## 9. Logging

Actual (MVP): `print()` para logs básicos.  
Producción: Migrar a:

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Indexed %d workflows", count)
logger.error("Database error: %s", error)
```

---

## 10. Tests

- Tests de API en `test_api.sh` (bash con curl).
- Tests de estructura JSON en `test_workflows.py`.
- Tests de seguridad en `test_security.sh`.
- Formato de test unitario: `pytest` cuando se añadan tests Python.
