import streamlit as st
import requests
import os

# ===========================
# 🔧 CONFIGURACIÓN INICIAL
# ===========================
st.set_page_config(page_title="JAIBOT LITE", page_icon="🤖", layout="centered")

st.title("🤖 JAIBOT LITE — Demo Local")
st.caption("Habla con tu asistente conectado a n8n + OpenAI")

# ===========================
# 💾 SESIÓN Y ESTADO
# ===========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # lista de (role, text)

# ===========================
# 💬 MOSTRAR HISTORIAL
# ===========================
for role, text in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"🧑 **Tú:** {text}")
    else:
        st.markdown(f"🤖 **JAIBOT:** {text}")

# ===========================
# ✍️ ENTRADA DEL USUARIO
# ===========================
user_message = st.text_area("Tu mensaje:", placeholder="Ejemplo: crea un evento mañana a las 10")

col1, col2 = st.columns([1, 1])
with col1:
    send_btn = st.button("Enviar")
with col2:
    clear_btn = st.button("🧹 Nueva conversación")

# ===========================
# 🧹 BORRAR CONVERSACIÓN
# ===========================
if clear_btn:
    st.session_state.chat_history = []
    st.experimental_rerun()

# ===========================
# 🚀 PROCESAR MENSAJE
# ===========================
if send_btn and user_message.strip():
    try:
        # URL del Webhook de n8n
        N8N_URL = "http://127.0.0.1:5678/webhook-test/jaibot_router"

        # Clave de autenticación (puede venir del entorno o usar valor por defecto)
        AUTH_KEY = os.getenv("JAIBOT_AUTH_KEY", "clave_jaibot")

        # Construimos el contexto con los últimos mensajes
        context_messages = [
            {"role": role, "content": text} for role, text in st.session_state.chat_history[-5:]
        ]

        # Enviamos mensaje con contexto y clave
        payload = {
            "auth_key": AUTH_KEY,
            "message": user_message,
            "context": context_messages
        }

        response = requests.post(
            N8N_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "Sin respuesta")

            # Guardamos en la sesión
            st.session_state.chat_history.append(("user", user_message))
            st.session_state.chat_history.append(("assistant", reply))

            st.rerun()
        else:
            st.error(f"Error {response.status_code}: {response.text}")

    except Exception as e:
        st.error(f"⚠️ Error al conectar con n8n: {e}")
