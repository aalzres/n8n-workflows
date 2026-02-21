# Uptime Kuma — Configuración de Monitorización

## Acceso

| Recurso | URL |
|---------|-----|
| Panel web | http://localhost:3001 |
| Admin | Credenciales creadas en el primer acceso |

## Monitores Configurados

### 1. n8n - Chatbot Lockers
- **Tipo:** HTTP(s)
- **URL:** `http://host.docker.internal:5678/healthz`
- **Intervalo:** 60 segundos
- **Reintentos:** 3 antes de marcar DOWN
- **Alertas:** Telegram (DOWN + recuperación UP)

## Alertas

| Canal | Configuración |
|-------|---------------|
| Telegram | Bot de @BotFather (mismo de subtarea 03) → Chat ID personal |

## Gestión del contenedor

```bash
# Ver estado
docker ps --filter name=uptime-kuma

# Parar
docker stop uptime-kuma

# Iniciar
docker start uptime-kuma

# Reiniciar
docker restart uptime-kuma

# Ver logs
docker logs uptime-kuma --tail 50

# Recrear desde docker-compose
docker compose -f n8n-local/monitoring/docker-compose.yml up -d

# Eliminar (los datos se mantienen en el volumen)
docker stop uptime-kuma && docker rm uptime-kuma
```

## ¿Por qué `host.docker.internal`?

Uptime Kuma corre **dentro de Docker**, pero n8n corre **en tu Mac** (instalado con npx).

```
┌─────────────────────────┐
│      Tu Mac (macOS)     │
│                         │
│  n8n (port 5678)  ◄──── host.docker.internal:5678
│                         │           ▲
│  ┌───────────────────┐  │           │
│  │     Docker        │  │    ping cada 60s
│  │  ┌─────────────┐  │  │           │
│  │  │ Uptime Kuma ├──┼──┼───────────┘
│  │  │ (port 3001) │  │  │
│  │  └─────────────┘  │  │
│  └───────────────────┘  │
└─────────────────────────┘
```

`host.docker.internal` es un alias especial de Docker Desktop que apunta a la máquina host (tu Mac). Desde dentro del contenedor, `localhost` apuntaría al propio contenedor, no a tu Mac.
