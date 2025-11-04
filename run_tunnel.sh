#!/bin/bash
echo "🚀 Iniciando túnel Cloudflare para JAIBOT..."
# Ejecutar el túnel y capturar la URL generada
cloudflared tunnel --url http://127.0.0.1:5678 --no-autoupdate 2>&1 | tee ~/Documents/Github_25/jai_assistant/tunnel_log.txt | while read line
do
    if [[ $line == *"trycloudflare.com"* ]]; then
        URL=$(echo $line | grep -o 'https://[^ ]*trycloudflare.com')
        echo $URL > ~/Documents/Github_25/jai_assistant/tunnel_url.txt
        echo "🌐 URL del túnel: $URL"
        echo $URL | pbcopy
        echo "📋 Copiada al portapapeles ✅"
    fi
done

