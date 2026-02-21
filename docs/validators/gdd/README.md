# GDD / Agent Definition Validator

Valida que los Design Docs y definiciones de agentes cumplan las reglas DOC-001, DOC-002, DOC-004, DOC-008 definidas en `docs/standards/documentation/rules.json`.

## Reglas aplicadas

- `DOC-001`: front-matter completo (title, status, tags, created, updated)
- `DOC-002`: valor de status válido
- `DOC-004`: documento registrado en manifest.json
- `DOC-008`: secciones obligatorias en Agent Definitions (Rol, Dominio, Lo que NO hace)

## Implementación pendiente

Crear `validate.py` en esta carpeta con la lógica de validación.
