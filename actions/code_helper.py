import subprocess
import sys
import json
import re
import time
from pathlib import Path


def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR           = get_base_dir()
API_CONFIG_PATH    = BASE_DIR / "config" / "api_keys.json"
DESKTOP            = Path.home() / "Desktop"
MAX_BUILD_ATTEMPTS = 3
GEMINI_MODEL       = "gemini-2.5-flash"


def _get_api_key() -> str:
    try:
        with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)["gemini_api_key"]
    except Exception:
        return ""


def _get_gemini(model: str = GEMINI_MODEL):
    from google import genai
    _c = genai.Client(api_key=_get_api_key())

    class _W:
        def generate_content(self, contents):
            return _c.models.generate_content(model=model, contents=contents)

    return _W()


def _clean_code(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    return text.strip()


def _resolve_save_path(output_path: str, language: str) -> Path:
    ext_map = {
        "python": ".py", "py": ".py",
        "javascript": ".js", "js": ".js",
        "typescript": ".ts", "ts": ".ts",
        "html": ".html", "css": ".css",
        "java": ".java", "cpp": ".cpp", "c": ".c",
        "bash": ".sh", "shell": ".sh", "powershell": ".ps1",
        "sql": ".sql", "json": ".json", "rust": ".rs", "go": ".go",
    }
    if output_path:
        p = Path(output_path)
        return p if p.is_absolute() else DESKTOP / p
    ext = ext_map.get((language or "python").lower(), ".py")
    return DESKTOP / f"jarvis_code{ext}"


def _read_file(file_path: str) -> tuple[str, str]:
    if not file_path:
        return "", "Nessun percorso file fornito."
    p = Path(file_path)
    if not p.exists():
        return "", f"File non trovato: {file_path}"
    try:
        return p.read_text(encoding="utf-8", errors="ignore"), ""
    except Exception as e:
        return "", f"Impossibile leggere il file: {e}"


def _save_file(path: Path, content: str) -> str:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Salvato in: {path}"
    except Exception as e:
        return f"Impossibile salvare: {e}"


def _preview(code: str, lines: int = 10) -> str:
    all_lines = code.splitlines()
    preview   = "\n".join(all_lines[:lines])
    suffix    = f"\n... (altre {len(all_lines) - lines} righe)" if len(all_lines) > lines else ""
    return preview + suffix


def _has_error(output: str) -> bool:
    error_signals = ["error", "exception", "traceback", "syntaxerror",
                     "nameerror", "typeerror", "stderr", "failed", "crash"]
    return any(s in output.lower() for s in error_signals)


def _take_screenshot() -> Path | None:
    try:
        import pyautogui
        screenshot_path = Path.home() / "Desktop" / f"jarvis_debug_{int(time.time())}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(str(screenshot_path))
        print(f"[Code] 📸 Screenshot salvato: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"[Code] ⚠️ Screenshot fallito: {e}")
        return None


def _image_to_base64(path: Path) -> str:
    import base64
    return base64.b64encode(path.read_bytes()).decode("utf-8")


_VALID_INTENTS = {"write", "edit", "explain", "run", "build", "screen_debug", "optimize"}


def _detect_intent(description: str, file_path: str, code: str) -> str:
    desc        = (description or "").strip()
    file_exists = bool(file_path) and Path(file_path).exists()

    if desc:
        try:
            ctx = []
            if file_path:
                ctx.append(f"a file path is provided (exists on disk: {file_exists})")
            if code:
                ctx.append("an inline code snippet is provided")
            prompt = (
                "Classify a coding assistant request into exactly ONE intent word.\n"
                "The request may be written in ANY language.\n\n"
                f"Request: {desc}\n"
                + (f"Context: {'; '.join(ctx)}\n" if ctx else "")
                + "\nIntents:\n"
                "  write        = create new code from scratch\n"
                "  edit         = modify an existing file\n"
                "  explain      = describe what given code/file does\n"
                "  run          = execute an existing file\n"
                "  build        = write code, run it, and iterate until it works\n"
                "  screen_debug = analyze an error currently visible on the user's screen\n"
                "  optimize     = refactor / clean up / speed up existing code\n\n"
                "Reply with ONLY the intent word, nothing else."
            )
            ans = _get_gemini().generate_content(prompt).text.strip().lower()
            ans = ans.strip("`'\". \n")
            if ans in _VALID_INTENTS:
                return ans
        except Exception as e:
            print(f"[Code] Riconoscimento intenzione fallito ({e}) — fallback strutturale")

    if file_exists:
        return "edit" if desc else "explain"
    if code:
        return "explain"
    return "write"

def _write(description: str, language: str, output_path: str, player=None) -> tuple[str, Path]:
    lang  = language or "python"
    model = _get_gemini()

    prompt = f"""Sei uno sviluppatore esperto in {lang}.
Scrivi codice {lang} pulito, funzionante e ben commentato in base alla descrizione.

Regole:
- Restituisci SOLO il codice. Nessuna spiegazione, nessun markdown, nessun backtick.
- Aggiungi commenti utili nel codice.
- Gestisci gli errori in modo corretto.

Descrizione: {description}

Codice:"""

    response = model.generate_content(prompt)
    code     = _clean_code(response.text)
    path     = _resolve_save_path(output_path, lang)
    _save_file(path, code)
    return code, path


def _fix_code(code: str, error_output: str, description: str) -> str:
    model  = _get_gemini()
    prompt = f"""Sei un esperto di debugging.
Il codice seguente ha generato un errore. Correggilo.
Restituisci SOLO il codice corretto — nessuna spiegazione, nessun markdown.

Obiettivo: {description}

Errore:
{error_output[:2000]}

Codice errato:
{code}

Codice corretto:"""

    response = model.generate_content(prompt)
    return _clean_code(response.text)


def _run_file(path: Path, args: list, timeout: int) -> str:
    interpreters = {
        ".py":  [sys.executable],
        ".js":  ["node"],
        ".ts":  ["ts-node"],
        ".sh":  ["bash"],
        ".ps1": ["powershell", "-File"],
        ".rb":  ["ruby"],
        ".php": ["php"],
    }
    interp = interpreters.get(path.suffix.lower())
    if not interp:
        return f"Nessun interprete trovato per {path.suffix}."

    try:
        result = subprocess.run(
            interp + [str(path)] + (args or []),
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            timeout=timeout, cwd=str(path.parent)
        )
        output = result.stdout.strip()
        error  = result.stderr.strip()
        parts  = []
        if output: parts.append(f"Output:\n{output}")
        if error:  parts.append(f"Stderr:\n{error}")
        return "\n\n".join(parts) if parts else "Eseguito senza output."

    except subprocess.TimeoutExpired:
        return f"Esecuzione scaduta (timeout {timeout}s)."
    except FileNotFoundError:
        return f"Interprete non trovato: {interp[0]}."
    except Exception as e:
        return f"Errore di esecuzione: {e}"


def _build(description, language, output_path, args, timeout, speak=None, player=None) -> str:
    if not description:
        return "Descrivi cosa vuoi creare."

    if player:
        player.write_log("[Code] Avvio modalità Build...")

    lang = language or "python"

    try:
        code, path = _write(description, lang, output_path, player)
        print(f"[Code] ✅ Scritto: {path}")
    except Exception as e:
        msg = f"Impossibile scrivere il codice iniziale: {e}"
        if speak: speak(msg)
        return msg

    last_output = ""
    for attempt in range(1, MAX_BUILD_ATTEMPTS + 1):
        print(f"[Code] 🔄 Tentativo {attempt}/{MAX_BUILD_ATTEMPTS}")
        if player:
            player.write_log(f"[Code] Tentativo {attempt}...")

        last_output = _run_file(path, args, timeout)

        if not _has_error(last_output):
            msg = (
                f"Creazione completata. "
                f"Il codice funziona correttamente dopo {attempt} tentativ{'o' if attempt == 1 else 'i'}. "
                f"Salvato in {path}."
            )
            if speak: speak(msg)
            return f"{msg}\n\nOutput:\n{last_output}"

        print(f"[Code] ⚠️ Errore al tentativo {attempt}, correzione in corso...")
        if player:
            player.write_log(f"[Code] Correzione tentativo {attempt}...")

        try:
            code = _fix_code(code, last_output, description)
            _save_file(path, code)
        except Exception as e:
            msg = f"Impossibile correggere il codice al tentativo {attempt}: {e}"
            if speak: speak(msg)
            return msg

    msg = (
        f"Impossibile generare una versione funzionante dopo {MAX_BUILD_ATTEMPTS} tentativi. "
        f"L'ultimo errore riscontrato è stato: {last_output[:200]}"
    )
    if speak: speak(msg)
    return f"{msg}\n\nUltimo codice salvato in: {path}"

def _write_action(description, language, output_path, player) -> str:
    if not description:
        return "Descrivi cosa desideri scrivere."
    if player:
        player.write_log("[Code] Scrittura codice...")
    try:
        code, path = _write(description, language, output_path, player)
        print(f"[Code] ✅ Scritto: {path}")
        return f"Codice generato e salvato in: {path}\n\nAnteprima:\n{_preview(code)}"
    except Exception as e:
        return f"Impossibile generare il codice: {e}"


def _edit_action(file_path, instruction, player) -> str:
    if not file_path:
        return "Fornisci il percorso del file da modificare."
    if not instruction:
        return "Descrivi le modifiche da applicare."

    content, err = _read_file(file_path)
    if err:
        return err

    if player:
        player.write_log("[Code] Modifica file in corso...")

    model  = _get_gemini()
    prompt = f"""Sei uno sviluppatore esperto.
Applica la seguente modifica al codice fornito.
Restituisci SOLO il codice aggiornato completo — nessuna spiegazione, nessun markdown.

Modifica richiesta: {instruction}

Codice originale:
{content}

Codice aggiornato:"""

    try:
        response = model.generate_content(prompt)
        edited   = _clean_code(response.text)
    except Exception as e:
        return f"Impossibile modificare il codice: {e}"

    status = _save_file(Path(file_path), edited)
    print(f"[Code] ✅ Modificato: {file_path}")
    return f"File modificato. {status}\n\nAnteprima:\n{_preview(edited)}"


def _explain_action(file_path, code, player) -> str:
    if file_path and not code:
        code, err = _read_file(file_path)
        if err:
            return err
    if not code:
        return "Fornisci del codice o il percorso di un file da spiegare."

    if player:
        player.write_log("[Code] Analisi codice...")

    model  = _get_gemini()
    prompt = f"""Spiega cosa fa questo codice in modo chiaro e coinciso (massimo 3-5 frasi).

Codice:
{code[:4000]}

Spiegazione:"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Impossibile spiegare il codice: {e}"


def _run_action(file_path, args, timeout, player) -> str:
    if not file_path:
        return "Fornisci il percorso del file da eseguire."
    p = Path(file_path)
    if not p.exists():
        return f"File non trovato: {file_path}"
    if player:
        player.write_log(f"[Code] Esecuzione {p.name}...")
    return _run_file(p, args, timeout)


def _optimize_action(file_path, code, language, output_path, player) -> str:
    if file_path and not code:
        code, err = _read_file(file_path)
        if err:
            return err
    if not code:
        return "Fornisci del codice o il percorso di un file da ottimizzare."

    if player:
        player.write_log("[Code] Ottimizzazione codice...")

    lang  = language or "python"
    model = _get_gemini()

    prompt = f"""Sei uno sviluppatore esperto {lang}.
Ottimizza il seguente codice per prestazioni, leggibilità e buone pratiche.
Restituisci SOLO il codice ottimizzato — nessuna spiegazione, nessun markdown.

Codice originale:
{code[:6000]}

Codice ottimizzato:"""

    try:
        response  = model.generate_content(prompt)
        optimized = _clean_code(response.text)
    except Exception as e:
        return f"Impossibile ottimizzare il codice: {e}"

    if file_path:
        save_path = Path(file_path)
    else:
        save_path = _resolve_save_path(output_path, lang)

    status = _save_file(save_path, optimized)
    print(f"[Code] ✅ Ottimizzato: {save_path}")

    original_lines  = len(code.splitlines())
    optimized_lines = len(optimized.splitlines())
    diff = original_lines - optimized_lines

    return (
        f"Codice ottimizzato. {status}\n"
        f"Righe: {original_lines} → {optimized_lines} "
        f"({'−' if diff > 0 else '+'}{abs(diff)} righe)\n\n"
        f"Anteprima:\n{_preview(optimized)}"
    )


def _screen_debug_action(description, file_path, player, speak=None) -> str:
    if player:
        player.write_log("[Code] Acquisizione screenshot per debug...")

    print("[Code] 📸 Cattura dello schermo in corso...")

    screenshot_path = _take_screenshot()
    if not screenshot_path:
        return "Impossibile scattare lo screenshot. Verifica che PyAutoGUI sia installato."

    file_content = ""
    if file_path:
        file_content, err = _read_file(file_path)
        if err:
            print(f"[Code] ⚠️ Impossibile leggere il file: {err}")

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=_get_api_key())
        image_bytes = screenshot_path.read_bytes()

        user_question = description or "Quale errore o problema vedi sullo schermo? Come può essere risolto?"

        context = ""
        if file_content:
            context = f"\n\nContenuto del file correlato:\n```\n{file_content[:4000]}\n```"

        analysis_prompt = f"""Sei uno sviluppatore ed esperto di debugging.
Analizza lo screenshot per rispondere al problema dell'utente.

Domanda: {user_question}{context}

1. Identifica errori o problemi visibili sullo schermo.
2. Spiega la causa in modo semplice.
3. Fornisci la soluzione concreta.
4. Se c'è del codice visibile, mostra la versione corretta."""

        contents = [
            types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            analysis_prompt,
        ]

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
        )

        analysis = response.text.strip()
        print(f"[Code] ✅ Analisi dello schermo completata")

        if file_path and file_content:
            code_match = re.search(r"```[a-zA-Z]*\n(.*?)```", analysis, re.DOTALL)
            if code_match:
                fixed_code = code_match.group(1).strip()
                save_path  = Path(file_path)
                _save_file(save_path, fixed_code)
                analysis += f"\n\n✅ Il codice corretto è stato salvato in: {file_path}"
                print(f"[Code] ✅ Codice corretto salvato: {file_path}")

        return analysis

    except Exception as e:
        return f"Analisi dello schermo fallita: {e}"
    finally:
        if screenshot_path and screenshot_path.exists():
            try:
                screenshot_path.unlink()
            except Exception:
                pass


def code_helper(
    parameters: dict,
    response=None,
    player=None,
    session_memory=None,
    speak=None
) -> str:
    p           = parameters or {}
    action      = p.get("action", "auto").lower().strip()
    description = p.get("description", "").strip()
    language    = p.get("language", "python").strip()
    output_path = p.get("output_path", "").strip()
    file_path   = p.get("file_path", "").strip()
    code        = p.get("code", "").strip()
    args        = p.get("args", [])
    timeout     = int(p.get("timeout", 30))

    if action == "auto":
        action = _detect_intent(description, file_path, code)
        print(f"[Code] 🤖 Rilevato automaticamente: {action}")

    if action == "write":
        return _write_action(description, language, output_path, player)

    elif action == "edit":
        return _edit_action(
            file_path,
            description or p.get("instruction", ""),
            player
        )

    elif action == "explain":
        return _explain_action(file_path, code, player)

    elif action == "run":
        return _run_action(file_path, args, timeout, player)

    elif action == "build":
        return _build(description, language, output_path, args, timeout, speak, player)

    elif action == "optimize":
        return _optimize_action(file_path, code, language, output_path, player)

    elif action == "screen_debug":
        return _screen_debug_action(description, file_path, player, speak)

    else:
        return f"Azione non valida: '{action}'. Scegli tra write, edit, explain, run, build, optimize o screen_debug."