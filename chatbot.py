import streamlit as st
import requests
from PIL import Image

# --- Configuración general ---
API_CHAT_URL = "https://mi-app-591630341746.us-central1.run.app/insight"
API_SYNC_URL = "https://mi-app-591630341746.us-central1.run.app/sync-drive-to-pinecone"
NAMESPACES = [
    "APEC","Kingspan", "Bancoppel", "Bioderma", "Esthederm", "Etat-Pur",
    "Honeywell", "Lexema", "Sanfer", "Zoomlion"
]

st.set_page_config(page_title="Lexema AI", layout="centered")

# --- Estilos personalizados ---
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #0f0526 0%, #190e50 100%) !important;
        color: white !important;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
        margin: auto;
    }
    .stChatMessage {
        background-color: #1d1b3a !important;
        color: #e6e6e6 !important;
        border-left: 4px solid #3affc3;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .stButton button {
        background-color: #3affc3;
        color: #000000;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
        transition: background-color 0.3s;
    }
    .stButton button:hover {
        background-color: #30e6b0;
    }
    section[data-testid="stSidebar"] {
        background-color: #10042d;
        border-right: 1px solid #2e1f6b;
    }
    .stSelectbox, .stSlider, .stTextInput, .stChatInput {
        color: #ffffff !important;
        background-color: #1e1c3b !important;
    }
    h1, h2, h3, h4 {
        color: #3affc3 !important;
        font-weight: 700;
    }
    a {
        color: #7df9ff !important;
        text-decoration: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Logo y título ---
logo = Image.open("logo.png")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo, width=100)
st.markdown("<h1 style='text-align: center;'>✨ Asistente Lexema</h1>", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.header("🔧 Configuración")

selected_namespace = st.sidebar.selectbox("Selecciona una empresa", NAMESPACES)
top_k = st.sidebar.slider("Cantidad de resultados (top_k)", min_value=5, max_value=30, value=30)

# Sincronización
st.sidebar.markdown("---")
st.sidebar.subheader("📄 Sincronizar documentos")

if st.sidebar.button("🔄 Sincronizar con Pinecone"):
    sync_url = f"{API_SYNC_URL}/{selected_namespace}"
    try:
        sync_response = requests.post(sync_url, timeout=60)
        if sync_response.status_code == 200:
            st.sidebar.success(f"✅ Sincronización completada para {selected_namespace}")
        else:
            st.sidebar.error(f"⚠️ Error {sync_response.status_code}: {sync_response.text}")
    except Exception as e:
        st.sidebar.error(f"🚨 Error al sincronizar: {e}")

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
            response = requests.post(
                f"{API_CHAT_URL}/{selected_namespace}",
                json={"query": user_input, "top_k": top_k},
                timeout=30
            )
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No se recibió respuesta.")
        else:
            answer = f"⚠️ Error {response.status_code}: {response.text}"
    except Exception as e:
        answer = f"🚨 Error al conectar con la API: {e}"

    st.chat_message("assistant").markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
