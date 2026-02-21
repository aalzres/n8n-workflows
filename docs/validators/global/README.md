# Global Validator

Valida toda la documentación de forma global: sincronía con manifest.json, ausencia de secretos, estructura de carpetas.

## Reglas aplicadas

- `DOC-004`: todos los documentos .md en subdirectorios deben estar en manifest.json
- `DOC-005`: no hay carpetas fuera de la estructura canónica
- `DOC-009`: no hay secrets/credentials hardcodeados en documentos

## Implementación pendiente

Crear `validate.py` en esta carpeta que:

1. Lee `docs/manifest.json`
2. Escanea todos los `.md` en `docs/`
3. Detecta documentos no listados en manifest (orphans)
4. Detecta entradas en manifest que no tienen archivo correspondiente (broken refs)
5. Busca patrones de secrets con la regex de DOC-009
6. Verifica que solo existen las carpetas permitidas bajo `docs/`
