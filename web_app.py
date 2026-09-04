import streamlit as st
import os
from google import genai

# Configurazione della pagina
st.set_page_config(
    page_title="J.A.R.V.I.S. AI",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Styling CSS personalizzato per ricreare il tema dark/cyberpunk di J.A.R.V.I.S.
st.markdown("""
    <style>
    /* Sfondo generale e font */
    .stApp {
        background-color: #0b0e14;
        color: #e0e6ed;
    }
    
    /* Intestazione personalizzata */
    .jarvis-header {
        text-align: center;
        padding: 15px;
        border-bottom: 2px solid #00f0ff;
        margin-bottom: 25px;
    }
    .jarvis-title {
        font-family: 'Courier New', Courier, monospace;
        color: #00f0ff;
        font-size: 2.2rem;
        font-weight: bold;
        letter-spacing: 3px;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
    }
    .jarvis-subtitle {
        color: #8a99ad;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Stile dei messaggi in chat */
    .stChatMessage {
        background-color: #151a23 !important;
        border: 1px solid #1f2937 !important;
        border-radius: 12px !important;
        padding: 10px !important;
        margin-bottom: 10px !important;
    }
    
    /* Evidenzia il bordo dei messaggi di Jarvis */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
        border-left: 4px solid #00f0ff !important;
    }

    /* Input di testo in basso */
    .stChatInputContainer {
        border-radius: 20px !important;
        border: 1px solid #00f0ff !important;
    }
    </style>
""", unsafe_allow_html=True)

# Header di J.A.R.V.I.S.
st.markdown("""
    <div class="jarvis-header">
        <div class="jarvis-title">⚡ J.A.R.V.I.S.</div>
        <div class="jarvis-subtitle">System Online • Cloud Interface</div>
    </div>
""", unsafe_allow_html=True)

# Recupera la chiave API dai Secrets di Streamlit o dall'ambiente
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Chiave API di Gemini non trovata nei Secrets di Streamlit Cloud.")
    st.stop()

# Inizializza il client di Gemini
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Errore di connessione con Gemini: {e}")
    st.stop()

# Inizializza la cronologia dei messaggi nella sessione
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Sistemi operativi. Come posso assisterti oggi?"}
    ]

# Mostra tutti i messaggi della conversazione
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Gestione dell'input dall'utente
if prompt := st.chat_input("Invia un comando a J.A.R.V.I.S..."):
    # Mostra e salva il messaggio dell'utente
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Elaborazione della risposta da parte di J.A.R.V.I.S.
    with st.chat_message("assistant"):
        with st.spinner("Elaborazione in corso..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                bot_response = response.text if response.text else "Nessuna risposta ricevuta."
                st.markdown(bot_response)
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
            except Exception as e:
                st.error(f"Errore durante l'esecuzione del comando: {e}")