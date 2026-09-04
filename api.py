import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from google import genai
from google.genai import types
from pydantic import BaseModel
import uvicorn

# Importiamo la gestione della memoria e le azioni da main.py
import main
import obsidian_memory

app = FastAPI(
    title="Jarvis Enterprise API (Full Engine)",
    description="Backend aziendale collegato al motore completo di Jarvis",
    version="2.0.0",
)

BASE_DIR = Path(__file__).resolve().parent


def get_api_key() -> str:
    """Recupera l'API Key usando la stessa logica di main.py."""
    try:
        return main._get_api_key()
    except Exception:
        return os.getenv("GEMINI_API_KEY", "")


# Inizializzazione Client Gemini
api_key = get_api_key()
client = genai.Client(api_key=api_key) if api_key else None


# Mappatura dei tool dichiarati in main.py verso le funzioni reali
def esegui_tool_main(name: str, args: dict) -> str:
    """Esegue le azioni dei tool definiti dentro main.py senza interfaccia grafica."""
    try:
        if name == "open_app":
            return main.open_app(parameters=args, response=None, player=None)
        elif name == "web_search":
            return main.web_search_action(parameters=args, player=None)
        elif name == "weather_report":
            return main.weather_action(parameters=args, player=None)
        elif name == "system_status":
            return str(main.get_system_status())
        elif name == "computer_settings":
            return main.computer_settings(
                parameters=args, response=None, player=None
            )
        elif name == "file_controller":
            return main.file_controller(parameters=args, player=None)
        elif name == "salva_nota":
            titolo = args.get("titolo", "Appunti Jarvis")
            contenuto = args.get("contenuto", "")
            return obsidian_memory.salva_nota(titolo, contenuto)
        else:
            return f"Tool '{name}' eseguito o non direttamente supportato via HTTP API."
    except Exception as e:
        return f"Errore durante l'esecuzione del tool {name}: {e}"


class ChatRequest(BaseModel):
    prompt: str
    user_pin: int = 151010


@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    if req.user_pin != 151010:
        raise HTTPException(status_code=401, detail="PIN errato.")
    if not client:
        raise HTTPException(
            status_code=500, detail="Client Gemini non configurato."
        )

    # Carica il system prompt originale (con memoria Obsidian completa inclusa)
    system_prompt = main._load_system_prompt()

    try:
        # Invoca Gemini passando le TOOL_DECLARATIONS ufficiali di main.py
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=req.prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=[
                    {"function_declarations": main.TOOL_DECLARATIONS}
                ],  # Tool da main.py
                temperature=0.7,
            ),
        )

        # Gestione Function Calling
        if response.candidates:
            for candidate in response.candidates:
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if part.function_call:
                            fn_name = part.function_call.name
                            fn_args = dict(part.function_call.args or {})

                            # Esegue l'azione reale dal motore
                            esito = esegui_tool_main(fn_name, fn_args)

                            messaggio = (
                                f"Eseguita azione **{fn_name}**: {esito}"
                            )
                            obsidian_memory.appendi_conversazione(
                                req.prompt, messaggio
                            )
                            return {
                                "response": messaggio,
                                "status": "success",
                            }

        testo_risposta = (
            response.text if response.text else "Elaborazione completata."
        )
        obsidian_memory.appendi_conversazione(req.prompt, testo_risposta)
        return {"response": testo_risposta, "status": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)