#!/bin/bash
# === JAIBOT LITE Launcher ===

echo "🚀 Iniciando JAIBOT LITE..."

# Activar entorno virtual
source .venv/bin/activate

# Ejecutar Streamlit (headless opcional)
streamlit run app/ui/main.py --server.port 8501
