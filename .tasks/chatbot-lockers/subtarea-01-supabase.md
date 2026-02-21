# Subtarea 01: Configuración de Supabase (Postgres)

## Objetivo
Base de datos operativa con todas las tablas, índices y conexión verificada con n8n.

## Dependencias
Ninguna — puede ejecutarse en paralelo con las subtareas 02 y 03.

---

## Pasos

### 1. Crear cuenta y proyecto en Supabase

1. Ir a [https://supabase.com](https://supabase.com)
2. Crear cuenta (se puede usar GitHub, Google o email)
3. Crear nuevo proyecto:
   - **Nombre:** chatbot-lockers (o el nombre del negocio)
   - **Contraseña de base de datos:** Generar una segura y guardarla
   - **Región:** Elegir la más cercana al servidor de n8n (Europe West si el servidor está en Europa)
4. Esperar a que el proyecto se aprovisione (~2 minutos)

### 2. Obtener credenciales de conexión

Ir a **Project Settings → API** y anotar:

| Credencial | Dónde encontrarla | Para qué |
|-----------|-------------------|----------|
| **Project URL** | Settings → API → Project URL | Conexión desde n8n |
| **anon/public key** | Settings → API → Project API keys | Autenticación REST API |
| **service_role key** | Settings → API → Project API keys | Autenticación con permisos completos (usar esta en n8n) |
| **Connection string** | Settings → Database → Connection string | Conexión directa Postgres desde n8n |

> **Importante:** La `service_role key` tiene permisos completos sobre la BD. No exponerla en frontend ni repositorios públicos.

### 3. Crear las tablas

Ir a **SQL Editor** en el panel de Supabase y ejecutar:

**Tabla conversations:**

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    client_phone VARCHAR(20) NOT NULL,
    role VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
```

**Tabla conversation_state:**

```sql
CREATE TABLE conversation_state (
    client_phone VARCHAR(20) PRIMARY KEY,
    status VARCHAR(20) DEFAULT 'bot',
    current_intent VARCHAR(50),
    last_interaction TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);
```

**Tabla pending_messages (antiflood):**

```sql
CREATE TABLE pending_messages (
    id SERIAL PRIMARY KEY,
    client_phone VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE
);
```

### 4. Crear índices

```sql
CREATE INDEX idx_conv_phone ON conversations(client_phone);
CREATE INDEX idx_conv_timestamp ON conversations(timestamp);
CREATE INDEX idx_pending_phone ON pending_messages(client_phone);
CREATE INDEX idx_pending_processed ON pending_messages(processed);
```

### 5. Verificar tablas

Ir a **Table Editor** en Supabase y confirmar que aparecen las 3 tablas con todos sus campos.

### 6. Configurar conexión en n8n

**Opción A — Nodo Postgres (recomendado):**

1. En n8n → **Credentials → New Credential → Postgres**
2. Configurar:
   - **Host:** `db.[tu-project-ref].supabase.co`
   - **Database:** `postgres`
   - **User:** `postgres`
   - **Password:** La contraseña generada al crear el proyecto
   - **Port:** `5432`
   - **SSL:** Activar (Supabase requiere SSL)
3. Guardar y probar conexión

**Opción B — HTTP Request a la API REST de Supabase:**

- **URL base:** `https://[tu-project-ref].supabase.co/rest/v1/`
- **Headers:**
  - `apikey`: tu `service_role key`
  - `Authorization`: `Bearer [tu service_role key]`
  - `Content-Type`: `application/json`

Ejemplo INSERT:
- **POST** a `https://[project-ref].supabase.co/rest/v1/conversations`
- **Body:** `{"client_phone": "34612345678", "role": "user", "message": "Hola"}`

Ejemplo SELECT historial:
- **GET** a `https://[project-ref].supabase.co/rest/v1/conversations?client_phone=eq.34612345678&order=timestamp.desc&limit=20`

### 7. Test de conexión desde n8n

Crear un workflow temporal de prueba:

1. Nodo **Manual Trigger**
2. Nodo **Postgres** → INSERT un registro de prueba en `conversations`
3. Nodo **Postgres** → SELECT para verificar que se guardó
4. Ejecutar y confirmar
5. Eliminar el registro de prueba

---

## Verificación

```
[ ] Proyecto Supabase creado y accesible
[ ] 3 tablas creadas: conversations, conversation_state, pending_messages
[ ] Índices creados
[ ] Credenciales guardadas en n8n
[ ] INSERT desde n8n funciona
[ ] SELECT desde n8n funciona
[ ] Registro de prueba eliminado
```
