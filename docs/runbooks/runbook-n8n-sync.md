---
title: "Runbook: n8n Workflow Sync"
status: approved
tags: [operations, n8n, sync, api, workflows]
created: 2026-02-21
updated: 2026-02-21
---

# Runbook: n8n Workflow Sync

## Objetivo

Procedimientos operativos para sincronizar workflows entre la instancia de n8n local y el repositorio de archivos JSON.

---

## Prerequisitos

1. n8n instalado y corriendo (`n8n start` o Docker)
2. API Key de n8n configurado en `.env`
3. Python con `requests` instalado

### Verificar que n8n está corriendo

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:5678/
# Debe devolver 200
```

### Verificar API Key

```bash
curl -s -H "X-N8N-API-KEY: <tu-key>" http://localhost:5678/api/v1/workflows | python3 -m json.tool | head -5
```

---

## Procedimientos

### 1. Exportar todos los workflows de n8n

**Cuándo**: Tras crear o modificar workflows en la UI de n8n.

```bash
python scripts/n8n_sync.py export
```

Resultado esperado:
```
  ✅ Webhook/Mi_workflow.json
  ✅ Telegram/Otro_workflow.json
Exported: 2, Skipped (unchanged): 0
```

### 2. Importar un workflow editado a n8n

**Cuándo**: Tras editar un JSON con la IA o manualmente en VS Code.

```bash
python scripts/n8n_sync.py import workflows/Webhook/Mi_workflow.json
```

Resultado esperado:
```
  🔄 Updated: Mi workflow (id:xxx)
Created: 0, Updated: 1, Errors: 0
```

### 3. Verificar diferencias

**Cuándo**: Para saber qué está en n8n vs qué está en archivos locales.

```bash
python scripts/n8n_sync.py diff
```

### 4. Modo Watch (auto-sync)

**Cuándo**: Mientras trabajas en n8n y quieres que los cambios se exporten automáticamente.

```bash
python scripts/n8n_sync.py watch --interval 10
# Ctrl+C para detener
```

### 5. Backup completo

```bash
python scripts/n8n_sync.py export
git add workflows/
git commit -m "chore: sync n8n workflows $(date +%Y-%m-%d)"
git push
```

---

## Troubleshooting

### Error: "Cannot connect to n8n"

```
ERROR: Cannot connect to n8n at http://localhost:5678. Is n8n running?
```

**Solución**: Iniciar n8n con `n8n start` o verificar que Docker está corriendo.

### Error: "'X-N8N-API-KEY' header required"

**Solución**: Verificar que `.env` existe con `N8N_API_KEY` válido.

```bash
cat .env | grep N8N_API_KEY
```

Si no existe, generar uno nuevo en n8n Settings → API.

### Error: "'requests' package required"

```bash
pip install requests
```

### Export no detecta cambios

Si `export` marca todo como "Skipped" pero sabes que hay cambios, el hash coincide por el contenido significativo (nodes, connections, settings). Si solo cambió metadata (timestamps), se ignora intencionalmente.

### Workflow exportado en categoría incorrecta

La categoría se detecta del primer nodo de integración significativo. Si el workflow tiene nodos genéricos únicamente (Set, IF, Code), se clasifica como `General/`. Para reclasificar, mover el archivo manualmente a la subcarpeta correcta.

---

## Configuración

| Variable | Default | Descripción |
|----------|---------|-------------|
| `N8N_API_URL` | `http://localhost:5678` | URL de la instancia n8n |
| `N8N_API_KEY` | (requerido) | API Key generado en n8n Settings → API |
| `N8N_SYNC_DIR` | `workflows` | Directorio local para los JSONs |
