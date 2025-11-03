import streamlit as st
import datetime
import logging
import os

# Configurar logs
LOG_PATH = os.path.join(os.path.dirname(__file__), "../logs/app.log")
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format="%(asctime)s — %(message)s")

def init_session():
    """Inicializa las variables de sesión necesarias."""
    if "chat" not in st.session_state:
        st.session_state.chat = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def add_message(sender: str, text: str):
    """Agrega un mensaje al chat y lo guarda en logs."""
    st.session_state.chat.append((sender, text))
    logging.info(f"[{sender}] {text}")

def show_chat():
    """Muestra el historial del chat en la interfaz."""
    for sender, text in st.session_state.chat:
        if sender == "Tú":
            st.markdown(f"🧑‍💻 **{sender}:** {text}")
        else:
            st.markdown(f"🤖 **{sender}:** {text}")
