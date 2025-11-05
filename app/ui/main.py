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

# ===========================
# 💅 ESTILO GLOBAL
# ===========================
st.markdown("""
<style>
body {
    background: linear-gradient(180deg, #f8f9fc 0%, #eef1f8 100%);
    font-family: 'Inter', sans-serif;
}
.chat-bubble-user {
    background-color: #e8f0fe;
    padding: 0.6rem 1rem;
    border-radius: 1rem;
    margin-bottom: 0.4rem;
    max-width: 85%;
}
.chat-bubble-bot {
    background-color: #f1f3f4;
    padding: 0.6rem 1rem;
    border-radius: 1rem;
    margin-bottom: 0.4rem;
    max-width: 85%;
}
</style>
""", unsafe_allow_html=True)

st.title("🤖 JAIBOT LITE — Demo Interactiva")
st.caption("Un asistente creado por **Jaime Inchaurraga** con n8n + Streamlit + OpenAI")

# ===========================
# 🔑 CARGAR VARIABLES DE ENTORNO
# ===========================
env_path = Path("app/config/secrets.env")
if env_path.exists():
    load_dotenv(env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL") or st.secrets.get("N8N_WEBHOOK_URL", None)
AUTH_KEY = os.getenv("JAIBOT_AUTH_KEY", "clave_jaibot")

# ===========================
# 💾 ESTADO DE SESIÓN
# ===========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "is_jaime" not in st.session_state:
    st.session_state.is_jaime = False

# ===========================
# 🚪 FASE DE IDENTIFICACIÓN
# ===========================
if not st.session_state.authenticated:
    st.subheader("👋 Antes de empezar...")
    user_type = st.radio(
        "¿Eres Jaime o un visitante?",
        ["Visitante", "Soy Jaime"],
        horizontal=True
    )

    if user_type == "Soy Jaime":
        password = st.text_input("Introduce tu clave secreta:", type="password")
        if password == "clave_jaibot":  # Clave temporal
            st.session_state.authenticated = True
            st.session_state.is_jaime = True
            st.success("✅ Autenticado como Jaime")
        elif password:
            st.error("❌ Clave incorrecta")
    else:
        st.session_state.authenticated = True
        st.session_state.is_jaime = False
        st.info("🔹 Modo visitante activado")

    st.stop()

# ===========================
# 💬 MOSTRAR HISTORIAL DE CHAT
# ===========================
for role, text in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"<div class='chat-bubble-user'>🧑 <b>Tú:</b> {text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bubble-bot'>🤖 <b>JAIBOT:</b> {text}</div>", unsafe_allow_html=True)

# ===========================
# ✍️ PROMPTS PREDEFINIDOS (DEMO)
# ===========================
st.markdown("### 💬 Preguntas sugeridas (modo demo)")
col1, col2, col3 = st.columns(3)
if col1.button("📅 ¿Cuántos años de experiencia tiene Jaime?"):
    st.session_state.input_area = "¿Cuántos años de experiencia tiene Jaime?"
if col2.button("💡 ¿Qué aficiones tiene Jaime?"):
    st.session_state.input_area = "¿Qué aficiones tiene Jaime?"
if col3.button("📊 ¿En qué proyectos ha trabajado Jaime?"):
    st.session_state.input_area = "¿En qué proyectos ha trabajado Jaime?"

# ===========================
# ✍️ ENTRADA DEL USUARIO
# ===========================
user_message = st.text_area(
    "Tu mensaje:",
    placeholder="Ejemplo: ¿Qué hace JAIBOT LITE?",
    key="input_area"
)

col1, col2 = st.columns([1, 1])
with col1:
    send_btn = st.button("Enviar", type="primary")
with col2:
    clear_btn = st.button("🧹 Nueva conversación")

# ===========================
# 🧹 LIMPIAR CHAT
# ===========================
if clear_btn:
    st.session_state.chat_history = []
    st.experimental_rerun()

# ===========================
# 🚀 PROCESAR MENSAJE
# ===========================
if send_btn and user_message.strip():
    try:
        prefix = ""
        if st.session_state.is_jaime:
            prefix = "(Soy Jaime, puedes hablarme en modo personal) "
        else:
            prefix = "(Usuario visitante, responde de forma informativa sobre Jaime) "

        payload = {
            "auth_key": AUTH_KEY,
            "message": prefix + user_message,
            "context": [
                {"role": role, "content": text}
                for role, text in st.session_state.chat_history[-5:]
            ],
        }

        response = requests.post(
            N8N_WEBHOOK_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=40,
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

# ===========================
# 🧠 SECCIÓN EXPLICATIVA
# ===========================
with st.expander("🧩 ¿Quieres saber cómo funciona JAIBOT LITE?"):
    st.markdown("""
    JAIBOT LITE es una demo interactiva creada por **Jaime Inchaurraga**.

    Combina:
    - 🧠 **OpenAI** como motor de lenguaje  
    - ⚙️ **n8n** para la lógica y orquestación  
    - 🌐 **Streamlit** como interfaz visual  
    - ☁️ **Cloudflare Tunnel** para exponer el backend local  

    El flujo permite enviar mensajes desde la interfaz, procesarlos en n8n
    y devolver respuestas inteligentes o ejecutar acciones automatizadas.
    """)

    img_path = Path("app/assets/arquitectura_jaibot.png")
    if img_path.exists():
        st.image(str(img_path), caption="Arquitectura del sistema")
    else:
        st.info("🖼️ Diagrama de arquitectura no disponible en este entorno.")
