# Subtarea 02: Configuración de Meta WhatsApp Cloud API

## Objetivo
WhatsApp Business API operativa con webhook recibiendo mensajes en n8n y capacidad de enviar respuestas.

## Dependencias
Ninguna — puede ejecutarse en paralelo con las subtareas 01 y 03.

---

## Pasos

### 1. Crear cuenta en Meta Business Suite

1. Ir a [https://business.facebook.com](https://business.facebook.com)
2. Crear cuenta de empresa (o usar una existente)
3. Completar la verificación de la empresa si no está hecha

### 2. Crear App en Meta Developers

1. Ir a [https://developers.facebook.com](https://developers.facebook.com)
2. **My Apps → Create App**
3. Seleccionar tipo: **Business**
4. Nombre de la app: `Chatbot Lockers` (o nombre del negocio)
5. Asociar a la cuenta de empresa creada en el paso 1
6. Una vez creada la app, ir a **Add Products** y añadir **WhatsApp**

### 3. Configurar número de teléfono

1. En el panel de WhatsApp dentro de la app → **Getting Started**
2. Meta proporciona un número de prueba temporal — sirve para desarrollo
3. Para producción: añadir tu número de teléfono real
   - Ir a **WhatsApp → Configuration → Phone Numbers**
   - **Add Phone Number** → Verificar con código SMS
   - El número no puede estar asociado a otra cuenta de WhatsApp (ni personal ni Business App)

> **Nota:** Si el número ya está en uso en WhatsApp, hay que desvincularlo primero (eliminar la cuenta de WhatsApp de ese número).

### 4. Obtener credenciales

| Credencial | Dónde encontrarla | Para qué |
|-----------|-------------------|----------|
| **Phone Number ID** | WhatsApp → Getting Started | Identificar desde qué número envías |
| **WhatsApp Business Account ID** | WhatsApp → Getting Started | Identificar tu cuenta de negocio |
| **Temporary Access Token** | WhatsApp → Getting Started | Token temporal (expira en 24h, solo para pruebas) |
| **App ID** | Settings → Basic | Identificador de la app |
| **App Secret** | Settings → Basic | Secreto de la app |

### 5. Generar token de acceso permanente

El token temporal expira en 24h. Para producción se necesita uno permanente:

1. Ir a [https://developers.facebook.com/tools/explorer/](https://developers.facebook.com/tools/explorer/)
2. Seleccionar tu app
3. En **User or Page** seleccionar **Get Page Access Token**
4. Seleccionar los permisos: `whatsapp_business_messaging`, `whatsapp_business_management`
5. Generar token
6. Ir a [https://developers.facebook.com/tools/debug/accesstoken/](https://developers.facebook.com/tools/debug/accesstoken/)
7. Pegar el token y hacer **Debug**
8. Clic en **Extend Access Token** para obtener un token de larga duración

**Alternativa más fiable — System User Token:**

1. Ir a Meta Business Suite → **Settings → Business Settings → System Users**
2. Crear un System User con rol **Admin**
3. Asignar la app de WhatsApp al System User
4. Generar token con permisos: `whatsapp_business_messaging`, `whatsapp_business_management`
5. Este token no expira

### 6. Configurar Webhook en Meta

El webhook es lo que permite que Meta envíe los mensajes de los clientes a tu n8n.

1. En Meta Developers → Tu App → **WhatsApp → Configuration**
2. En la sección **Webhook**:
   - **Callback URL:** `https://[tu-dominio-n8n]/webhook/whatsapp` (la URL del webhook de n8n)
   - **Verify Token:** Un string secreto que tú defines (ej: `mi_token_secreto_123`)
3. Clic en **Verify and Save**

> **Importante:** Antes de verificar, el webhook de n8n debe estar activo y responder al challenge GET de Meta. Meta envía un GET con `hub.mode=subscribe`, `hub.verify_token=[tu token]` y `hub.challenge=[un número]`. n8n debe responder con el valor de `hub.challenge`.

**Configurar webhook en n8n para responder al challenge:**

Crear un workflow con:
1. Nodo **Webhook** → Path: `/whatsapp` → Método: GET y POST
2. Para el GET (verificación): Responder con el valor de `hub.challenge` del query parameter
3. Para el POST (mensajes): Procesar el mensaje entrante

### 7. Suscribirse a eventos del webhook

Después de verificar el webhook:

1. En la sección **Webhook Fields**, suscribirse a: **messages**
2. Esto hará que Meta envíe un POST a tu webhook cada vez que un cliente envíe un mensaje

### 8. Configurar templates de mensaje (para mensajes iniciados por el negocio)

Meta exige templates aprobados para mensajes que inicia el negocio (fuera de la ventana de 24h).

1. Ir a **WhatsApp → Message Templates**
2. Crear templates necesarios:
   - **Confirmación de reserva:** "Hola {{1}}, tu reserva de locker {{2}} está confirmada. Tu código de acceso es: {{3}}"
   - **Recordatorio:** "Hola {{1}}, tu locker {{2}} expira en {{3}} horas. ¿Necesitas extender?"
   - **Escalado a humano:** "Hola {{1}}, un agente revisará tu consulta y te responderá pronto."
3. Enviar templates para aprobación (Meta los revisa, tarda 24-48h)

> **Nota:** Para responder dentro de la ventana de 24h (cuando el cliente escribe primero), no se necesitan templates. Se puede enviar texto libre. Los templates solo son necesarios si el negocio inicia la conversación.

### 9. Formato de envío de mensajes (respuestas del bot)

Para enviar una respuesta al cliente desde n8n, el HTTP Request debe ser:

- **Método:** POST
- **URL:** `https://graph.facebook.com/v21.0/[PHONE_NUMBER_ID]/messages`
- **Headers:**
  - `Authorization`: `Bearer [ACCESS_TOKEN]`
  - `Content-Type`: `application/json`
- **Body:**

```json
{
    "messaging_product": "whatsapp",
    "to": "[NUMERO_CLIENTE]",
    "type": "text",
    "text": {
        "body": "[MENSAJE_DE_RESPUESTA]"
    }
}
```

### 10. Formato de descarga de audio (para Whisper)

Cuando un cliente envía una nota de voz, Meta proporciona un `media_id`. Para descargar el audio:

1. **GET** `https://graph.facebook.com/v21.0/[MEDIA_ID]` con header `Authorization: Bearer [TOKEN]`
2. La respuesta incluye un campo `url` con la URL temporal del archivo
3. **GET** a esa URL para descargar el archivo de audio
4. Enviar el audio a Groq Whisper para transcripción

### 11. Configurar credenciales en n8n

Guardar en n8n como credenciales o variables de entorno:

- `META_PHONE_NUMBER_ID`
- `META_ACCESS_TOKEN`
- `META_WEBHOOK_VERIFY_TOKEN`
- `META_WHATSAPP_BUSINESS_ACCOUNT_ID`

### 12. Test completo

1. Enviar un mensaje desde el número de prueba al número de WhatsApp Business
2. Verificar que el webhook de n8n recibe el POST con el mensaje
3. Verificar que puedes enviar una respuesta usando el HTTP Request
4. Verificar que el mensaje de respuesta llega al cliente

---

## Verificación

```
[ ] Cuenta Meta Business Suite creada y verificada
[ ] App creada en Meta Developers con producto WhatsApp añadido
[ ] Número de teléfono verificado y asociado
[ ] Token de acceso permanente generado (System User Token)
[ ] Webhook configurado y verificado (challenge respondido)
[ ] Suscrito a eventos: messages
[ ] Templates de mensaje creados y enviados para aprobación
[ ] Credenciales guardadas en n8n
[ ] Test: enviar mensaje al bot → webhook recibe el POST
[ ] Test: enviar respuesta desde n8n → cliente recibe el mensaje
[ ] Número de WhatsApp secundario disponible para pruebas
```
