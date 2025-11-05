#!/bin/bash
echo "🚀 Iniciando n8n con el mismo entorno de Streamlit (secrets.env)..."
cd /Users/jaime/Documents/jaibot_lite/Github_25/jaibot_lite
n8n start --dotenv app/config/secrets.env
