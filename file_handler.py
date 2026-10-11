import os
from pathlib import Path

def process_file_or_image(file_path: str, user_prompt: str, model_client) -> str:
    """
    Gestisce l'analisi di immagini e file inviati a JARVIS.
    Supporta immagini (OCR e analisi visiva) e documenti di testo/codice con gestione sicura degli errori API.
    """
    if not os.path.exists(file_path):
        return f"Errore: Il file '{file_path}' non esiste."

    ext = Path(file_path).suffix.lower()
    image_extensions = [".png", ".jpg", ".jpeg", ".webp", ".bmp"]
    text_extensions = [".txt", ".md", ".py", ".json", ".csv", ".log", ".html"]

    # ── CASE 1: IMMAGINI & VISION (OCR + DESCRIZIONE) ────────────────────────
    if ext in image_extensions:
        try:
            from PIL import Image
            img = Image.open(file_path)

            system_instruction = (
                "Sei la componente visiva di JARVIS.\n"
                "Analizza l'immagine fornita ed esegui le seguenti operazioni:\n"
                "1. Se nell'immagine c'è del testo (scritto a mano o stampato), trascrivilo con precisione (OCR).\n"
                "2. Rispondi in modo dettagliato ed esaustivo alla richiesta dell'utente basandoti sugli elementi visivi presenti nell'immagine.\n"
            )

            prompt_completo = f"{system_instruction}\nRichiesta Utente: {user_prompt if user_prompt else 'Descrivi cosa vedi ed estrai eventuale testo.'}"

            # Chiamata al modello multimodale protetta da eccezioni di rete/API
            response = model_client.generate_content([prompt_completo, img])
            
            if hasattr(response, "text") and response.text:
                return response.text.strip()
            return "Nessuna risposta generata dal modello visivo."

        except Exception as e:
            error_str = str(e)
            print(f"[JARVIS FileProcessor Warning] Analisi immagine fallita: {error_str}")
            
            # Gestione mirata dell'errore 404 o incompatibilità del modello
            if "404" in error_str or "NOT_FOUND" in error_str:
                return f"⚠️ Analisi visiva non disponibile con la configurazione attuale del modello (Errore 404).\nFile registrato: {os.path.basename(file_path)}"
            
            return f"Errore durante l'analisi visiva dell'immagine: {error_str}"

    # ── CASE 2: FILE DI TESTO & CODICE (FILE Q&A) ─────────────────────────────
    elif ext in text_extensions:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                file_content = f.read()

            system_instruction = (
                f"Sei JARVIS. L'utente ti ha fornito il contenuto del file '{os.path.basename(file_path)}'.\n"
                "Analizza il contenuto del file e rispondi alla domanda o richiesta dell'utente.\n"
            )

            prompt = (
                f"{system_instruction}\n"
                f"--- CONTENUTO DEL FILE ---\n"
                f"{file_content}\n"
                f"---------------------------\n\n"
                f"Domanda/Istruzione Utente: {user_prompt if user_prompt else 'Sintetizza il contenuto di questo file.'}"
            )

            response = model_client.generate_content(prompt)
            
            if hasattr(response, "text") and response.text:
                return response.text.strip()
            return "Nessuna risposta generata dal modello di testo."

        except Exception as e:
            error_str = str(e)
            print(f"[JARVIS FileProcessor Warning] Lettura file fallita: {error_str}")
            return f"Errore durante la lettura del file: {error_str}"

    else:
        return f"Formato file '{ext}' non ancora supportato per l'analisi diretta."