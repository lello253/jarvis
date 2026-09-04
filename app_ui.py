import glob
import json
import os
from pathlib import Path
import asyncio
import psutil
import streamlit as st
import websockets

# Configurazione della pagina
st.set_page_config(
    page_title="Jarvis Enterprise HUD",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Styling Sci-Fi Custom
st.markdown(
    """
    <style>
    .stApp { background-color: #0b0f19; color: #00e5ff; }
    .hud-card {
        background: rgba(16, 26, 44, 0.8);
        border: 1px solid #00e5ff;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.2);
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    .hud-title { font-family: 'Courier New', monospace; font-size: 1.1rem; font-weight: bold; color: #00e5ff; margin-bottom: 10px; }
    .metric-val { font-size: 1.4rem; color: #ffffff; font-weight: bold; }
    </style>
""",
    unsafe_allow_html=True,
)

VAULT_PATH = Path("./app_memory")
VAULT_PATH.mkdir(parents=True, exist_ok=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Layout a 3 Colonne: HUD System | Chat | Memoria
col_hud, col_chat, col_memory = st.columns([1, 1.4, 1.2])

# ---------------------------------------------------------
# COLONNA 1: HUD & SYSTEM MONITOR
# ---------------------------------------------------------
with col_hud:
    st.markdown(
        "<div class='hud-title'>🛡️ JARVIS CORE STATUS</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class='hud-card' style='text-align: center;'>
            <h2 style='color:#00e5ff; margin:0; font-size: 1.5rem;'>JARVIS ONLINE</h2>
            <p style='color:#888; font-size:0.8rem; margin-top:5px;'>Protocollo Enterprise Attivo</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='hud-title'>📊 METRICHE SISTEMA</div>",
        unsafe_allow_html=True,
    )

    cpu_use = psutil.cpu_percent()
    ram_use = psutil.virtual_memory().percent

    st.markdown(
        f"""
        <div class='hud-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span>CPU LOAD</span>
                <span class='metric-val'>{cpu_use}%</span>
            </div>
        </div>
        <div class='hud-card'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span>RAM USAGE</span>
                <span class='metric-val'>{ram_use}%</span>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# COLONNA 2: CHAT & COMANDI
# ---------------------------------------------------------
with col_chat:
    st.markdown(
        "<div class='hud-title'>💬 CONVERSAZIONE</div>", unsafe_allow_html=True
    )

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    async def send_to_jarvis_ws(text_prompt):
        uri = "ws://127.0.0.1:8000/ws"
        try:
            async with websockets.connect(uri) as websocket:
                payload = json.dumps({"type": "command", "text": text_prompt})
                await websocket.send(payload)
                return "Comando elaborato dal motore di Jarvis, Signore."
        except Exception as e:
            return f"Errore di connessione a Jarvis Core: {e}"

    if prompt := st.chat_input("Chiedi qualcosa a Jarvis..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Elaborazione..."):
                risposta = asyncio.run(send_to_jarvis_ws(prompt))
                st.write(risposta)
                st.session_state.messages.append(
                    {"role": "assistant", "content": risposta}
                )
                st.rerun()

# ---------------------------------------------------------
# COLONNA 3: MEMORIA (.md)
# ---------------------------------------------------------
with col_memory:
    st.markdown(
        "<div class='hud-title'>🧠 MEMORIA AZIENDALE</div>",
        unsafe_allow_html=True,
    )

    files = glob.glob(os.path.join(VAULT_PATH, "*.md"))
    file_names = [os.path.basename(f) for f in files]

    if not file_names:
        st.info("Nessuna nota presente.")
    else:
        selected_file = st.selectbox("Seleziona nota:", file_names)
        if selected_file:
            filepath = VAULT_PATH / selected_file
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            new_content = st.text_area(
                "Editor", value=content, height=420, label_visibility="collapsed"
            )

            c1, c2 = st.columns(2)
            with c1:
                if st.button("💾 Salva", use_container_width=True):
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    st.success("Salvato!")
            with c2:
                if st.button("🔄 Ricarica", use_container_width=True):
                    st.rerun()