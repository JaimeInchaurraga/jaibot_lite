import streamlit as st

def header(title: str = "🤖 JAIBOT LITE"):
    """Encabezado principal."""
    st.markdown(f"# {title}")
    st.markdown("### Tu asistente IA conectado a n8n y OpenAI")

def input_box():
    """Entrada de texto para el usuario."""
    return st.text_input("Escribe tu orden aquí:")

def send_button(label: str = "Enviar"):
    """Botón de envío."""
    return st.button(label)

def divider():
    st.markdown("---")

def info_message(msg: str):
    st.info(msg)
