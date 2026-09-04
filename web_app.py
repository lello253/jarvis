import streamlit as st
import os
import json
from google import genai
import streamlit.components.v1 as components

# PIN di accesso personale per Jarvis
PIN_SICUREZZA = "151010"  # Sostituisci con il PIN che preferisci

if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

if not st.session_state.autenticato:
    st.markdown("""
        <style>
        .stApp { background-color: #0b0e14; color: #00f0ff; }
        </style>
    """, unsafe_allow_html=True)
    st.title("🔒 J.A.R.V.I.S. - Autenticazione")
    pin_inserito = st.text_input("Inserisci il PIN di sicurezza", type="password")
    if st.button("Accedi"):
        if pin_inserito == PIN_SICUREZZA:
            st.session_state.autenticato = True
            st.rerun()
        else:
            st.error("PIN errato. Accesso negato.")
    st.stop()

# Configurazione della pagina Streamlit
st.set_page_config(
    page_title="J.A.R.V.I.S. System",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Styling CSS per riprodurre il tema Dark / Cyberpunk con comandi e navigazione
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
        color: #e0e6ed;
    }
    .jarvis-header {
        text-align: center;
        padding: 10px;
        border-bottom: 2px solid #00f0ff;
        margin-bottom: 20px;
    }
    .jarvis-title {
        font-family: 'Courier New', Courier, monospace;
        color: #00f0ff;
        font-size: 2rem;
        font-weight: bold;
        letter-spacing: 2px;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
    }
    .stChatMessage {
        background-color: #151a23 !important;
        border: 1px solid #1f2937 !important;
        border-radius: 10px !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
        border-left: 4px solid #00f0ff !important;
    }
    .note-card {
        background-color: #151a23;
        border: 1px solid #00f0ff;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Inizializzazione API Key e Client Gemini
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ API Key di Gemini non configurata.")
    st.stop()

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Errore connessione Gemini: {e}")
    st.stop()

# Gestione Stato Note e Messaggi
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Sistemi operativi, Signore. In cosa posso assisterla?"}
    ]

if "notes" not in st.session_state:
    if os.path.exists("notes.json"):
        try:
            with open("notes.json", "r", encoding="utf-8") as f:
                st.session_state.notes = json.load(f)
        except Exception:
            st.session_state.notes = []
    else:
        st.session_state.notes = []

def save_notes():
    with open("notes.json", "w", encoding="utf-8") as f:
        json.dump(st.session_state.notes, f, ensure_ascii=False, indent=2)

# Navigation Menu (Rotella / Sidebar)
st.sidebar.title("⚙️ NUCLEO J.A.R.V.I.S.")
page = st.sidebar.radio("Seleziona Schermata", ["🤖 Assistente Vocale / Chat", "📝 Gestione Note"])

st.sidebar.markdown("---")
st.sidebar.info("Stato Sistema: ONLINE 24/7 (Cloud)")

# --- SCHERMATA 1: ASSISTENTE VOCALE E CHAT ---
if page == "🤖 Assistente Vocale / Chat":
    st.markdown("""
        <div class="jarvis-header">
            <div class="jarvis-title">⚡ J.A.R.V.I.S.</div>
            <small style="color: #8a99ad;">INTERFACCIA VOCALE E TESTUALE</small>
        </div>
    """, unsafe_allow_html=True)

    # Componente Web Speech API per dettatura vocale su smartphone
    st.subheader("🎙️ Comando Vocale")
    components.html("""
        <div style="text-align: center; font-family: sans-serif;">
            <button id="micBtn" style="background-color: #00f0ff; color: #0b0e14; border: none; padding: 12px 24px; font-weight: bold; border-radius: 20px; cursor: pointer;">
                🎤 Premi e Parla
            </button>
            <p id="status" style="color: #8a99ad; font-size: 12px; margin-top: 8px;">In attesa di input vocale...</p>
        </div>
        <script>
            const btn = document.getElementById('micBtn');
            const status = document.getElementById('status');
            
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const recognition = new SpeechRecognition();
                recognition.lang = 'it-IT';
                recognition.interimResults = false;

                btn.onclick = () => {
                    recognition.start();
                    status.innerText = "Ascolto in corso...";
                };

                recognition.onresult = (event) => {
                    const text = event.results[0][0].transcript;
                    status.innerText = "Riconosciuto: " + text;
                    window.navigator.clipboard.writeText(text);
                    alert("Testo vocale copiato: " + text + "\\nIncollalo nella chat sottostante.");
                };

                recognition.onerror = (event) => {
                    status.innerText = "Errore vocale: " + event.error;
                };
            } else {
                status.innerText = "Riconoscimento vocale non supportato da questo browser.";
            }
        </script>
    """, height=90)

    # Visualizzazione Cronologia Chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input Testuale
    if prompt := st.chat_input("Invia un comando a J.A.R.V.I.S..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Elaborazione in corso..."):
                try:
                    res = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt
                    )
                    reply = res.text if res.text else "Nessuna risposta generata."
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as err:
                    st.error(f"Errore: {err}")

# --- SCHERMATA 2: GESTIONE NOTE ---
elif page == "📝 Gestione Note":
    st.markdown("""
        <div class="jarvis-header">
            <div class="jarvis-title">📝 ARCHIVIO NOTE</div>
            <small style="color: #8a99ad;">GESTIONE MEMORIA LOCALE</small>
        </div>
    """, unsafe_allow_html=True)

    # Aggiunta nuova nota
    with st.form("new_note_form", clear_on_submit=True):
        note_title = st.text_input("Titolo Nota")
        note_content = st.text_area("Contenuto Nota")
        submitted = st.form_submit_button("💾 Salva Nota")
        
        if submitted and note_title and note_content:
            st.session_state.notes.append({"title": note_title, "content": note_content})
            save_notes()
            st.success(f"Nota '{note_title}' salvata con successo!")

    st.markdown("---")
    st.subheader("Note Archiviate")

    if not st.session_state.notes:
        st.info("Nessuna nota presente in archivio.")
    else:
        for idx, note in enumerate(st.session_state.notes):
            with st.expander(f"📌 {note['title']}"):
                st.write(note["content"])
                if st.button("❌ Elimina", key=f"del_{idx}"):
                    st.session_state.notes.pop(idx)
                    save_notes()
                    st.rerun()