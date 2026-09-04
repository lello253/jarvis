import streamlit as st
import os
import json
from google import genai
import streamlit.components.v1 as components

# Configurazione della pagina
st.set_page_config(
    page_title="J.A.R.V.I.S. System",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# PIN di sicurezza
PIN_SICUREZZA = "2530"  # Cambialo se necessario

if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

if not st.session_state.autenticato:
    st.markdown("<style>.stApp { background-color: #0b0e14; color: #00f0ff; }</style>", unsafe_allow_html=True)
    st.title("🔒 J.A.R.V.I.S. - Autenticazione")
    pin_inserito = st.text_input("Inserisci il PIN di sicurezza", type="password")
    if st.button("Accedi"):
        if pin_inserito == PIN_SICUREZZA:
            st.session_state.autenticato = True
            st.rerun()
        else:
            st.error("PIN errato.")
    st.stop()

# Styling Cyberpunk
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e0e6ed; }
    .jarvis-header { text-align: center; padding: 10px; border-bottom: 2px solid #00f0ff; margin-bottom: 20px; }
    .jarvis-title { font-family: 'Courier New', monospace; color: #00f0ff; font-size: 2rem; font-weight: bold; }
    .stChatMessage { background-color: #151a23 !important; border: 1px solid #1f2937 !important; border-radius: 10px !important; }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) { border-left: 4px solid #00f0ff !important; }
    </style>
""", unsafe_allow_html=True)

# Inizializzazione API Key
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ API Key di Gemini non configurata.")
    st.stop()

client = genai.Client(api_key=api_key)

# FUNZIONI GESTIONE MEMORIA A LUNGO TERMINE
MEMORY_FILE = "long_term.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

memory_data = load_memory()

# Sidebar
st.sidebar.title("⚙️ NUCLEO J.A.R.V.I.S.")
page = st.sidebar.radio("Seleziona Schermata", ["🤖 Assistente Vocale / Chat", "🧠 Memoria & Note"])

if page == "🤖 Assistente Vocale / Chat":
    st.markdown('<div class="jarvis-header"><div class="jarvis-title">⚡ J.A.R.V.I.S.</div></div>', unsafe_allow_html=True)

    # Componente Vocale
    components.html("""
        <div style="text-align: center;">
            <button id="micBtn" style="background-color: #00f0ff; color: #0b0e14; border: none; padding: 10px 20px; font-weight: bold; border-radius: 20px; cursor: pointer;">
                🎤 Premi e Parla
            </button>
            <p id="status" style="color: #8a99ad; font-size: 11px; margin-top: 5px;">In attesa...</p>
        </div>
        <script>
            const btn = document.getElementById('micBtn');
            const status = document.getElementById('status');
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const recognition = new SpeechRecognition();
                recognition.lang = 'it-IT';
                btn.onclick = () => { recognition.start(); status.innerText = "Ascolto..."; };
                recognition.onresult = (e) => {
                    const text = e.results[0][0].transcript;
                    navigator.clipboard.writeText(text);
                    alert("Copiato: " + text + "\\nIncollalo nella chat.");
                };
            }
        </script>
    """, height=80)

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Sistemi operativi, Signore. Memoria caricata."}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Comando per J.A.R.V.I.S..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Costruzione del contesto con la memoria a lungo termine
        system_context = f"Sei J.A.R.V.I.S., un assistente AI avanzato. Ecco la tua memoria a lungo termine attuale: {json.dumps(memory_data, ensure_ascii=False)}. Rispondi tenendo conto di questo contesto.\nRichiesta utente: {prompt}"

        with st.chat_message("assistant"):
            with st.spinner("Elaborazione..."):
                reply = ""
                try:
                    res = client.models.generate_content(model="gemini-3.6-flash", contents=system_context)
                    reply = res.text if res.text else "Nessuna risposta."
                except Exception:
                    try:
                        res = client.models.generate_content(model="gemini-3.1-pro-preview", contents=system_context)
                        reply = res.text if res.text else "Nessuna risposta."
                    except Exception as err:
                        st.error(f"Errore: {err}")

                if reply:
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})

elif page == "🧠 Memoria & Note":
    st.markdown('<div class="jarvis-header"><div class="jarvis-title">🧠 MEMORIA SISTEMA</div></div>', unsafe_allow_html=True)
    st.subheader("Dati Memoria a Lungo Termine")
    st.json(memory_data)
    
    st.markdown("---")
    st.subheader("Aggiungi Informazione alla Memoria")
    with st.form("add_mem"):
        key = st.text_input("Chiave / Argomento (es: 'preferenze', 'progetto')")
        val = st.text_area("Informazione da ricordare")
        if st.form_submit_button("💾 Salva in Memoria") and key and val:
            memory_data[key] = val
            save_memory(memory_data)
            st.success("Memoria aggiornata!")
            st.rerun()