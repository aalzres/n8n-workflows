# Validators

Esta carpeta contiene validadores automáticos que comprueban que la documentación cumple los estándares definidos en `docs/standards/documentation/rules.json`.

## Estructura

```
validators/
├── gdd/       → Valida Design Docs (GDDs) y Agent Definitions
├── adr/       → Valida ADRs (numeración, secciones)
├── runbook/   → Valida Runbooks (secciones obligatorias)
└── global/    → Valida front-matter y sincronía con manifest.json
```

## Cómo ejecutar los validadores

```bash
# Global (todos los documentos)
python docs/validators/global/validate.py

# Por tipo
python docs/validators/adr/validate.py
python docs/validators/runbook/validate.py
python docs/validators/gdd/validate.py
```

## Estado

Los validadores están definidos con sus reglas en `docs/standards/documentation/rules.json`.  
Los scripts de validación están pendientes de implementación.

Al implementarlos, deben:
1. Leer `docs/manifest.json` para obtener la lista de documentos.
2. Para cada documento, verificar las reglas aplicables según su tipo.
3. Reportar errores y warnings con ruta de archivo y número de línea.
4. Devolver exit code 0 (éxito) o 1 (errores encontrados).
