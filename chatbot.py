import streamlit as st
import requests
from PIL import Image
import base64

# --- Configuración general ---
API_CHAT_URL = "https://mi-app-591630341746.us-central1.run.app/insight"
API_TABULAR_URL = "https://mi-app-591630341746.us-central1.run.app/tabular-insight"
API_TABULAR_FILES = "https://mi-app-591630341746.us-central1.run.app/tabular-files"
NAMESPACES = [
    "APEC", "Kingspan", "Bancoppel", "Bioderma", "Esthederm", "Etat-Pur",
    "Honeywell", "Lexema", "Sanfer", "Zoomlion"
]

st.set_page_config(page_title="Lexema AI", layout="centered")

# --- Logo y título ---
logo = Image.open("logo.png")
st.image(logo, width=100)
st.markdown("<h1>Asistente Lexema</h1>", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.header("🔧 Configuración")

selected_namespace = st.sidebar.selectbox("Selecciona una empresa", NAMESPACES)

# 🔁 Modo de análisis
modo = st.sidebar.radio("Modo de análisis", ["📚 Preguntas", "📊 Insights"])

file_name = None
if modo == "📊 Tabular (Excel/CSV)":
    try:
        files_response = requests.get(f"{API_TABULAR_FILES}/{selected_namespace}")
        if files_response.status_code == 200:
            file_options = files_response.json().get("files", [])
            if file_options:
                file_name = st.sidebar.selectbox("Selecciona archivo tabular", file_options)
            else:
                st.sidebar.warning("No se encontraron archivos tabulares.")
        else:
            st.sidebar.warning("No se pudieron cargar los archivos.")
    except Exception as e:
        st.sidebar.error(f"Error al obtener archivos: {e}")

# --- Historial de conversación ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Entrada del usuario ---
user_input = st.chat_input("Hazme una pregunta sobre la empresa, productos o procesos...")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        with st.spinner("⏳ Pensando..."):
            if modo == "📚 Documental (Pinecone)":
                url = f"{API_CHAT_URL}/{selected_namespace}"
                payload = {"query": user_input}
            else:
                url = f"{API_TABULAR_URL}/{selected_namespace}"
                payload = {"query": user_input, "file_name": file_name}

            response = requests.post(url, json=payload, timeout=60)

        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No se recibió respuesta.")
            source = data.get("source", "desconocido")
            full_response = f"**Fuente:** `{source}`\n\n{answer}"

            st.chat_message("assistant").markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # 📈 Mostrar gráfico si está presente
            if "chart" in data:
                st.markdown("### 📊 Gráfico generado automáticamente")
                img_bytes = base64.b64decode(data["chart"])
                st.image(img_bytes) 
        else:
            full_response = f"⚠️ Error {response.status_code}: {response.text}"
            st.chat_message("assistant").markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

    except Exception as e:
        full_response = f"🚨 Error al conectar con la API: {e}"
        st.chat_message("assistant").markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
