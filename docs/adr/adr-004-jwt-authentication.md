---
title: "ADR-004: JWT para autenticación"
status: approved
tags: [security, jwt, authentication, bcrypt]
created: 2026-02-21
updated: 2026-02-21
---

# ADR-004: JWT para autenticación

## Contexto

El sistema de comunidad y gestión de usuarios necesita mecanismo de autenticación stateless compatible con la arquitectura REST y desplegable en múltiples instancias.

## Decisión

**Usar JWT (JSON Web Tokens) con HS256** para autenticación.

- Librería: `PyJWT==2.8.0`
- Hash de contraseñas: `passlib[bcrypt]==1.7.4`
- `SECRET_KEY` inyectado vía variable de entorno
- Expiración por defecto: 30 minutos (configurable en env)

## Alternativas Consideradas

| Alternativa | Por qué se descartó |
|-------------|---------------------|
| Sesiones con cookies (server-side) | Requiere almacenamiento de sesiones, no stateless |
| OAuth2 externo (Auth0, Keycloak) | Dependencia externa, complejidad para MVP |
| API Keys simples | Sin expiración nativa, más difícil de revocar |
| mTLS | Demasiada complejidad operacional |

## Consecuencias

**Positivas:**
- Stateless: compatible con múltiples instancias sin shared state
- `SECRET_KEY` desde env var: seguro en producción con orquestación de secretos
- bcrypt para passwords: resistente a ataques de fuerza bruta
- Standard RFC 7519: fácil integración con clientes

**Negativas:**
- Sin revocación de tokens sin una blocklist (los tokens son válidos hasta expiración)
- `SECRET_KEY` con fallback a token random en desarrollo: si el proceso reinicia, los tokens existentes son inválidos
- HS256 es simétrico: la misma clave firma y verifica (adecuado para arquitectura monolítica, no para microservicios distribuidos)

## Notas de Implementación

Para producción es **obligatorio** definir la variable de entorno `JWT_SECRET_KEY`.  
Para multi-instancia, todos los pods/contenedores deben compartir el mismo `SECRET_KEY`.  
Ver [`docs/design/agent-security.md`](../design/agent-security.md) para checklist de seguridad completo.
