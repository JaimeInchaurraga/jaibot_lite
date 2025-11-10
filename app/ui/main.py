import streamlit as st
import requests
import os
import re
import unicodedata
from dotenv import load_dotenv
from pathlib import Path

# ===========================
# ⚙️ CONFIGURACIÓN INICIAL
# ===========================
st.set_page_config(page_title="JAIBOT LITE", page_icon="🤖", layout="centered")

st.title("🤖 JAIBOT LITE — Demo Interactiva")
st.caption("🍀 Versión interfaz: 2025-11-10-v9 (Unicode brackets → ASCII + Cf-strip)")
st.caption("Un asistente creado por **Jaime Inchaurraga** con n8n + Streamlit + OpenAI")

# ===========================
# 🔑 VARIABLES DE ENTORNO
# ===========================
env_path = Path("app/config/secrets.env")
if env_path.exists():
    load_dotenv(env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
AUTH_KEY = os.getenv("JAIBOT_AUTH_KEY", "clave_jaibot")

# ===========================
# 💅 ESTILO GLOBAL (bocadillos)
# ===========================
st.markdown("""
<style>
body { background: linear-gradient(180deg, #f8f9fc 0%, #eef1f8 100%); font-family: 'Inter', sans-serif; }
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
.demo-chip button { width:100%; }
</style>
""", unsafe_allow_html=True)

# ===========================
# 🧽 LIMPIEZA DE TEXTO — ROBUSTA
# ===========================
_BRACKET_TRANSLATION = str.maketrans({
    # Fullwidth
    '［': '[', '］': ']',
    # Black lenticular
    '【': '[', '】': ']',
    # Mathematical/technical
    '⟦': '[', '⟧': ']',
    '⟮': '(', '⟯': ')',
    # Corner/ornament
    '「': '[', '」': ']',
    '『': '[', '』': ']',
    '〖': '[', '〗': ']',
    '〘': '[', '〙': ']',
    '〔': '[', '〕': ']',
    '﹝': '[', '﹞': ']',
    '｟': '(', '｠': ')',
})

def _strip_invisible(s: str) -> str:
    """Elimina todos los caracteres invisibles de categoría Unicode 'Cf'."""
    return ''.join(ch for ch in s if unicodedata.category(ch) != 'Cf')

def clean_reply(text: str) -> str:
    """Elimina cualquier bloque [ ... ] (en ASCII o Unicode), limpia invisibles y espacios."""
    if not text:
        return text

    # 1️⃣ Normaliza Unicode y elimina invisibles
    text = unicodedata.normalize("NFKC", text)
    text = _strip_invisible(text)

    # 2️⃣ Traduce variantes de corchetes a ASCII
    text = text.translate(_BRACKET_TRANSLATION)

    # 3️⃣ Elimina cualquier bloque entre corchetes (doble pasada)
    text = re.sub(r"\[[^\]]*?\]", "", text)
    text = re.sub(r"\[[^\]]*?\]", "", text)

    # 4️⃣ Limpieza de espacios y puntuación
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    text = re.sub(r"([(\[]) +", r"\1", text)
    text = re.sub(r" +([)\]])", r"\1", text)

    return text.strip()

# ===========================
# 💾 ESTADO DE SESIÓN
# ===========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ===========================
# 💬 HISTORIAL DE MENSAJES
# ===========================
for role, text in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"<div class='chat-bubble-user'>🧑 <b>Tú:</b> {text}</div>", unsafe_allow_html=True)
    else:
        cleaned_text = clean_reply(text)
        st.markdown(f"<div class='chat-bubble-bot'>🤖 <b>JAIBOT:</b> {cleaned_text}</div>", unsafe_allow_html=True)

# ===========================
# 💡 PREGUNTAS SUGERIDAS
# ===========================
st.markdown("### 💬 Preguntas sugeridas (modo demo)")
c1, c2, c3 = st.columns(3, gap="small")
with c1:
    if st.button("📅 ¿Cuántos años de experiencia tiene Jaime?", use_container_width=True):
        st.session_state.input_area = "¿Cuántos años de experiencia tiene Jaime?"
with c2:
    if st.button("💡 ¿Qué aficiones tiene Jaime?", use_container_width=True):
        st.session_state.input_area = "¿Qué aficiones tiene Jaime?"
with c3:
    if st.button("📊 ¿En qué proyectos ha trabajado Jaime?", use_container_width=True):
        st.session_state.input_area = "¿En qué proyectos ha trabajado Jaime?"

# ===========================
# ✍️ INPUT DEL USUARIO
# ===========================
user_message = st.text_area(
    "Tu mensaje:",
    placeholder="Ejemplo: ¿Qué hace JAIBOT LITE?",
    key="input_area"
)

c1, c2 = st.columns([1, 1])
with c1:
    send_btn = st.button("Enviar", type="primary")
with c2:
    clear_btn = st.button("🧹 Nueva conversación")

# ===========================
# 🧹 REINICIAR HISTORIAL
# ===========================
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
            reply_raw = data.get("reply", "⚠️ Sin respuesta del asistente.")
            reply_clean = clean_reply(reply_raw)
            st.session_state.chat_history.append(("user", user_message))
            st.session_state.chat_history.append(("assistant", reply_clean))
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
