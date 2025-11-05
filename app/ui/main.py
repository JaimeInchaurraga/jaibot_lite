import streamlit as st
import requests
import os
from dotenv import load_dotenv
from pathlib import Path
import subprocess

# ===========================
# ⚙️ CONFIGURACIÓN INICIAL
# ===========================

st.set_page_config(page_title="JAIBOT LITE", page_icon="🤖", layout="centered")

st.title("🤖 JAIBOT LITE — Demo Interactiva")
st.caption("Habla con tu asistente conectado a n8n + OpenAI")

# ===========================
# 🔑 CARGAR VARIABLES DE ENTORNO
# ===========================

# Si existe secrets.env local → lo carga
if Path("app/config/secrets.env").exists():
    load_dotenv("app/config/secrets.env")

# Carga variables desde entorno o desde st.secrets (para Streamlit Cloud)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL") or st.secrets.get("N8N_WEBHOOK_URL")
AUTH_KEY = os.getenv("JAIBOT_AUTH_KEY", "clave_jaibot")

# ===========================
# 🧠 FUNCIÓN PARA DETECTAR O CREAR TÚNEL CLOUDFLARE
# ===========================
def get_or_create_tunnel_url():
    """
    Detecta si hay un túnel Cloudflare activo o lanza uno nuevo.
    Devuelve la URL pública (https://xxx.trycloudflare.com).
    """
    tunnel_file = Path("tunnel_url.txt")
    if tunnel_file.exists():
        url = tunnel_file.read_text().strip()
        if url.startswith("https://"):
            return url

    try:
        # Inicia cloudflared y captura la URL del túnel temporal
        result = subprocess.run(
            ["cloudflared", "tunnel", "--url", "http://127.0.0.1:5678", "--no-autoupdate"],
            capture_output=True,
            text=True,
            timeout=15
        )
        lines = result.stdout.splitlines()
        for line in lines:
            if "trycloudflare.com" in line:
                url = line.split(" ")[-1].strip()
                tunnel_file.write_text(url)
                return url
    except Exception as e:
        st.warning(f"No se pudo crear el túnel automáticamente: {e}")

    return None

# ===========================
# 🌐 DETERMINAR URL DE N8N
# ===========================

if not N8N_WEBHOOK_URL:
    tunnel_url = get_or_create_tunnel_url()
    if tunnel_url:
        N8N_WEBHOOK_URL = f"{tunnel_url}/webhook-test/jaibot_router"
        st.info(f"🌍 Usando túnel activo: {N8N_WEBHOOK_URL}")
    else:
        N8N_WEBHOOK_URL = "http://127.0.0.1:5678/webhook-test/jaibot_router"
        st.warning("⚠️ No se detectó túnel activo, usando entorno local.")

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
        payload = {
            "auth_key": AUTH_KEY,
            "message": user_message,
            "context": [
                {"role": role, "content": text}
                for role, text in st.session_state.chat_history[-5:]
            ]
        }

        response = requests.post(
            N8N_WEBHOOK_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=40
        )

        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "⚠️ Sin respuesta del asistente.")
            st.session_state.chat_history.append(("user", user_message))
            st.session_state.chat_history.append(("assistant", reply))
            st.experimental_rerun()
        else:
            st.error(f"❌ Error {response.status_code}: {response.text}")

    except Exception as e:
        st.error(f"⚠️ Error al conectar con n8n: {e}")

