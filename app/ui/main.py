import streamlit as st
import requests
import os
import re
from dotenv import load_dotenv
from pathlib import Path
import html

# ===========================
# ⚙️ CONFIGURACIÓN INICIAL
# ===========================
st.set_page_config(page_title="JAIBOT LITE", page_icon="🤖", layout="centered")

st.title("🤖 JAIBOT LITE — Demo Interactiva")
st.caption("🧩 Versión interfaz: 2025-11-06-v7 (modo texto plano total)")
st.caption("Un asistente creado por **Jaime Inchaurraga** con n8n + Streamlit + OpenAI")

# ===========================
# 🔑 VARIABLES DE ENTORNO
# ===========================
env_path = Path("app/config/secrets.env")
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
AUTH_KEY = os.getenv("JAIBOT_AUTH_KEY", "clave_jaibot")

# ===========================
# 🧽 FUNCIÓN LIMPIEZA
# ===========================
def clean_reply(text: str) -> str:
    """Elimina cualquier bloque [ ... ] y caracteres invisibles."""
    if not text:
        return text
    import unicodedata
    text = unicodedata.normalize("NFKD", text)
    text = text.replace("\u200b", "").replace("\ufeff", "").replace("\xa0", " ")
    text = text.replace("［", "[").replace("］", "]")
    while re.search(r"\[[^\]]*\]", text):
        text = re.sub(r"\[[^\]]*\]", "", text)
    return re.sub(r"\s+", " ", text).strip()

# ===========================
# 💾 SESIÓN
# ===========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ===========================
# 💬 HISTORIAL
# ===========================
for role, text in st.session_state.chat_history:
    if role == "user":
        st.text(f"🧑 Tú: {text}")
    else:
        cleaned = clean_reply(text)
        st.text(f"🤖 JAIBOT: {cleaned}")

# ===========================
# INPUT
# ===========================
user_message = st.text_area("Tu mensaje:", placeholder="Ejemplo: ¿Qué hace JAIBOT LITE?", key="input_area")

c1, c2 = st.columns(2)
with c1:
    send_btn = st.button("Enviar")
with c2:
    clear_btn = st.button("🧹 Nueva conversación")

if clear_btn:
    st.session_state.chat_history = []
    st.experimental_rerun()

# ===========================
# 🚀 ENVIAR A N8N
# ===========================
if send_btn and user_message.strip():
    try:
        payload = {
            "auth_key": AUTH_KEY,
            "message": user_message,
            "context": [{"role": r, "content": t} for r, t in st.session_state.chat_history[-5:]],
        }
        response = requests.post(N8N_WEBHOOK_URL, headers={"Content-Type": "application/json"}, json=payload, timeout=40)

        if response.status_code == 200:
            data = response.json()
            reply_raw = data.get("reply", "⚠️ Sin respuesta del asistente.")
            reply_clean = clean_reply(reply_raw)
            st.session_state.chat_history.append(("user", user_message))
            st.session_state.chat_history.append(("assistant", reply_clean))
            st.experimental_rerun()
        else:
            st.error(f"❌ Error {response.status_code}: {response.text}")

    except Exception as e:
        st.error(f"⚠️ Error al conectar con n8n: {e}")
