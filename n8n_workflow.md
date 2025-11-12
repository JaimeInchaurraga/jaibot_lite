Perfecto 🔥 Aquí tienes la **versión actualizada del documento** (en formato `.md`), completamente adaptada al **nuevo flujo funcional y estable que acabamos de construir** — incluye los nuevos headers, los dos bucles de espera (`Wait` + `Wait2`) y la estructura final de control del `run`.
Todo está explicado con claridad y en el mismo estilo que tu documento anterior 👇

---

````markdown
# 🤖 JAIBOT LITE — Flujo n8n (versión estable noviembre 2025)

Esta es la versión **totalmente operativa y depurada** del flujo de n8n que conecta **Streamlit ↔ n8n ↔ OpenAI (Assistants API v2)**.  
Incluye manejo robusto de asincronía, cabeceras actualizadas, y validación de seguridad mediante `auth_key`.

---

## 🔄 VISIÓN GENERAL

El flujo actúa como **puente entre Streamlit y la API de OpenAI**, gestionando la conversación de forma controlada.

1. **Streamlit (frontend)** → envía un mensaje del usuario vía webhook.
2. **n8n (backend)** → valida, comunica con OpenAI, espera a que el Assistant genere respuesta y la devuelve limpia.
3. **Streamlit** → muestra el texto ya procesado.

---

## 🧩 DESGLOSE PASO A PASO

### 1️⃣ **Webhook**

📥 **Función:**
Recibe la petición POST enviada por tu app Streamlit.  
Incluye el mensaje del usuario, la `auth_key` y, opcionalmente, contexto adicional.

📦 **Ejemplo de payload:**
```json
{
  "auth_key": "clave_jaibot",
  "message": "¿Cuántos años de experiencia tiene Jaime?",
  "context": []
}
````

---

### 2️⃣ **If (condicional de seguridad)**

🔒 **Función:**
Valida si la `auth_key` recibida es correcta.

🧩 **Condición:**

```
{{$json.body.auth_key}} == "clave_jaibot"
```

📊 **Resultado:**

* ✅ True → continúa con la lógica principal.
* ❌ False → devuelve respuesta genérica (modo demo / rechazo).

---

### 3️⃣ **Create Thread**

🧵 **Función:**
Crea un nuevo hilo (`thread`) en la API de OpenAI, que servirá como contenedor para todos los mensajes.

📤 **POST a:**

```
https://api.openai.com/v1/threads
```

📥 **Salida esperada:**

```json
{
  "id": "thread_xxx",
  "object": "thread"
}
```

📋 **Headers obligatorios:**

| Name          | Value               |
| ------------- | ------------------- |
| Authorization | Bearer sk-proj-XXXX |
| OpenAI-Beta   | assistants=v2       |

---

### 4️⃣ **Add Message**

💬 **Función:**
Añade el mensaje del usuario al hilo recién creado.

📤 **POST a:**

```
https://api.openai.com/v1/threads/{{ $node["Create Thread"].json["id"] }}/messages
```

📥 **Cuerpo JSON correcto:**

```json
{
  "role": "user",
  "content": [
    {
      "type": "text",
      "text": "{{ $json.body.message }}"
    }
  ],
  "metadata": {
    "source": "jaibot_lite_ui",
    "context": "streamlit",
    "timestamp": "={{ new Date().toISOString() }}"
  }
}
```

📋 **Headers obligatorios:**

| Name          | Value               |
| ------------- | ------------------- |
| Authorization | Bearer sk-proj-XXXX |
| OpenAI-Beta   | assistants=v2       |

---

### 5️⃣ **Create Run**

🏃 **Función:**
Inicia una ejecución (`run`) del Assistant asociado al hilo.

📤 **POST a:**

```
https://api.openai.com/v1/threads/{{ $node["Create Thread"].json["id"] }}/runs
```

📥 **Body:**

```json
{
  "assistant_id": "asst_4zJtDgo7Jx7I77ckT6a9PCcF"
}
```

📋 **Headers:**

| Name          | Value               |
| ------------- | ------------------- |
| Authorization | Bearer sk-proj-XXXX |
| OpenAI-Beta   | assistants=v2       |

---

### 6️⃣ **Wait**

⏳ **Función:**
Pausa el flujo unos segundos (≈ 3–5 s) para dar tiempo al Assistant a iniciar la generación de respuesta.

---

### 7️⃣ **Get Run Status1**

🔍 **Función:**
Consulta el estado actual del run.

📤 **GET a:**

```
https://api.openai.com/v1/threads/{{ $node["Create Thread"].json["id"] }}/runs/{{ $node["Create Run"].json["id"] }}
```

📋 **Headers:**

| Name          | Value               |
| ------------- | ------------------- |
| Authorization | Bearer sk-proj-XXXX |
| OpenAI-Beta   | assistants=v2       |

📥 **Respuesta esperada:**

```json
{
  "status": "in_progress"
}
```

---

### 8️⃣ **If1 (comprobación de estado)**

🤖 **Función:**
Evalúa si el run ha terminado.

🧩 **Condición:**

```
{{ $json.status }} == "completed"
```

* ✅ **TRUE** → pasa a *Get Messages*.
* ❌ **FALSE** → ejecuta *Wait2* (espera adicional) y reintenta *Get Run Status2*.

---

### 9️⃣ **Wait2** y **Get Run Status2**

🔁 **Función:**
Permiten volver a comprobar si el run ha finalizado tras unos segundos más.

*Este bucle evita que el flujo se rompa si la respuesta del modelo tarda un poco más.*

---

### 🔟 **Get Messages**

📨 **Función:**
Recupera los mensajes del hilo, incluyendo la respuesta generada por el assistant.

📤 **GET a:**

```
https://api.openai.com/v1/threads/{{ $node["Create Thread"].json["id"] }}/messages?order=desc&limit=3
```

📋 **Headers:**

| Name          | Value               |
| ------------- | ------------------- |
| Authorization | Bearer sk-proj-XXXX |
| OpenAI-Beta   | assistants=v2       |

📥 **Respuesta esperada:**

```json
{
  "data": [
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": { "value": "Jaime tiene más de 6 años de experiencia..." }
        }
      ]
    }
  ]
}
```

---

### 1️⃣1️⃣ **Respond to Webhook**

🚀 **Función:**
Devuelve la respuesta limpia a Streamlit.

📄 **Expresión en “Response Body”:**

```js
{{
JSON.stringify({
  reply:
    ($json.data || [])
      .find(m => m.role === "assistant")
      ?.content?.[0]?.text?.value
      ?.replace(/\n/g, " ")
      ?.replace(/-+/g, "-")
      ?.trim() ||
    "⚠️ No se encontró respuesta del asistente."
})
}}
```

✅ Este formato está confirmado como **100 % estable**:

* No genera errores de JSON.
* Elimina saltos de línea.
* Limpia guiones dobles y espacios innecesarios.

---

### 🔁 **Rama alternativa (If → False → Respond to Webhook - Rechazo)**

Si la `auth_key` no coincide:

```json
{
  "reply": "Solo Jaime puede ejecutar acciones reales. Estás en modo demostración."
}
```

---

## 🧭 DIAGRAMA FINAL DEL FLUJO

```
Webhook → If (auth_key válida?)
   ├─ True →
   │   Create Thread
   │   → Add Message
   │   → Create Run
   │   → Wait
   │   → Get Run Status1
   │       ├─ True → Get Messages → Respond to Webhook
   │       └─ False → Wait2 → Get Run Status2 → (reintento)
   └─ False → Respond to Webhook (rechazo)
```

---

## ✅ CAMBIOS CLAVE EN ESTA VERSIÓN

* Añadido header `OpenAI-Beta: assistants=v2` (obligatorio para Assistants API v2).
* Incorporado **doble ciclo de espera** (`Wait` + `Wait2`) con comprobación condicional `If1`.
* Se mantuvo el `JSON.stringify()` original, probado y validado.
* Flujo más robusto frente a tiempos de respuesta variables de OpenAI.

---

