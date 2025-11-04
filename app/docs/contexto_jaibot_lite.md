# JAIBOT LITE — Asistente personal e interfaz inteligente

## Propósito
JAIBOT LITE es una versión simplificada del ecosistema JAIBOT.  
Combina n8n (como cerebro de automatización), Streamlit (como interfaz) y OpenAI (como motor de razonamiento).  
Su misión es ejecutar órdenes naturales (“añade evento”, “crea resumen”, “envía correo”) conectando APIs como Gmail, Google Calendar y Notion.

## Arquitectura
- **Frontend:** Streamlit UI
- **Core automation:** n8n workflows
- **AI Layer:** OpenAI GPT (modelo gpt-4o)
- **Opcional:** Cloudflare Tunnel para exponer endpoints locales

## Uso previsto
- Jaime usa JAIBOT LITE como asistente personal.
- También puede mostrárselo a terceros como ejemplo de IA personalizada y contextualizada.
- Los visitantes pueden hacer preguntas sobre su perfil, pero no ejecutar acciones sin clave.

## Acceso seguro
Para ejecutar tareas (crear eventos, correos o Notion items), se requiere autenticación mediante palabra clave (“clave_jaibot”).

## Estado actual
Versión estable, sincronizada con n8n y Streamlit local.
