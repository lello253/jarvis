import streamlit as st
import os
from google import genai

# Configurazione della pagina
st.set_page_config(page_title="J.A.R.V.I.S. AI", page_icon="🤖", layout="centered")

st.title("🤖 J.A.R.V.I.S. AI")
st.caption("Assistente Virtuale Personalizzato")

# Recupera la chiave dalle variabili d'ambiente (impostate sul cloud) o da un input
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Inserisci la tua Gemini API Key:", type="password")

if api_key:
    client = genai.Client(api_key=api_key)

    # Inizializza la cronologia della chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostra i messaggi precedenti
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input dell'utente
    if prompt := st.chat_input("Chiedi qualcosa a Jarvis..."):
        # Mostra il messaggio dell'utente
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Risposta di Jarvis
        with st.chat_message("assistant"):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Errore durante l'elaborazione: {e}")
else:
    st.warning("Inserisci una chiave API valida nella barra laterale per iniziare.")