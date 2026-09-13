import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

app = FastAPI(title="JARVIS API Core")

# Abilita CORS per permettere al telefono/web app di comunicare con il server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurazione API Key e Client Gemini
API_KEY = os.environ.get("GEMINI_API_KEY")
PIN_SEGRETO = os.environ.get("JARVIS_PIN", "2530")

client = genai.Client(api_key=API_KEY) if API_KEY else None

class ChatRequest(BaseModel):
    message: str

# Middleware / Controllo PIN
def verifica_pin(x_pin: str = Header(None)):
    if x_pin != PIN_SEGRETO:
        raise HTTPException(status_code=401, detail="PIN Non Valido")

@app.get("/")
def home():
    return {"status": "ONLINE", "system": "J.A.R.V.I.S. Core API"}

@app.post("/api/chat")
def chat(req: ChatRequest, x_pin: str = Header(None)):
    verifica_pin(x_pin)
    if not client:
        raise HTTPException(status_code=500, detail="Gemini API Key non configurata.")
    
    prompt = req.message
    try:
        # Tentativo con modello primario
        res = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )
        return {"response": res.text}
    except Exception:
        try:
            # Fallback automatico
            res = client.models.generate_content(
                model="gemini-3.1-pro-preview",
                contents=prompt
            )
            return {"response": res.text}
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Errore server AI: {str(e)}")