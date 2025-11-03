import streamlit as st
import requests
import os

# Configuración inicial
st.set_page_config(page_title="JAIBOT LITE", page_icon="🤖", layout="centered")

st.title("🤖 JAIBOT LITE — Demo Local")
st.write("Habla con tu asistente conectado a n8n + OpenAI")

# Campo de entrada
user_message = st.text_area("Escribe tu mensaje:", placeholder="Ejemplo: crea un evento mañana a las 10")

if st.button("Enviar") and user_message.strip():
    try:
        # URL del Webhook de n8n (modo test o prod)
        N8N_URL = "http://127.0.0.1:5678/webhook-test/jaibot_router"

        # Enviar petición POST al flujo
        response = requests.post(
            N8N_URL,
            headers={"Content-Type": "application/json"},
            json={"message": user_message},
            timeout=30
        )

        # Mostrar resultado
        if response.status_code == 200:
            data = response.json()
            st.success(data.get("reply", "Sin respuesta"))
        else:
            st.error(f"Error {response.status_code}: {response.text}")

    except Exception as e:
        st.error(f"⚠️ Error al conectar con n8n: {e}")
