import glob
import json
import os
import threading
from datetime import datetime
from pathlib import Path

_file_lock = threading.Lock()


def get_active_vault_path() -> str:
    """Legge dinamicamente il percorso della memoria da config/settings.json."""
    config_path = Path("./config/settings.json")
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            if config.get("memory_folder"):
                path = Path(config["memory_folder"])
                path.mkdir(parents=True, exist_ok=True)
                return str(path)
        except Exception:
            pass

    default_vault = Path("./app_memory").resolve()
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH", str(default_vault))
    os.makedirs(vault_path, exist_ok=True)
    return vault_path


def salva_nota(titolo: str, contenuto: str) -> str:
    """Salva una nuova nota in formato Markdown e invalida la cache."""
    vault_path = get_active_vault_path()

    titolo_pulito = "".join(
        c for c in titolo if c.isalnum() or c in (" ", "_", "-")
    ).strip()

    if not titolo_pulito:
        titolo_pulito = f"Nota_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    filename = f"{titolo_pulito}.md"
    filepath = os.path.join(vault_path, filename)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    testo_completo = (
        f"# {titolo}\n\n*Nota creata da Jarvis il {timestamp}*\n\n{contenuto}\n"
    )

    with _file_lock:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(testo_completo)

    try:
        from main import invalidate_obsidian_cache

        invalidate_obsidian_cache()
    except Exception as e:
        print(f"[JARVIS Cache Warning] Impossibile invalidare la cache: {e}")

    return f"Nota '{titolo}' salvata con successo nella memoria."


def leggi_tutta_la_memoria() -> str:
    """Legge tutti i file .md dando priorità alle note utente rispetto ai diari di chat."""
    vault_path = get_active_vault_path()

    files = glob.glob(os.path.join(vault_path, "**", "*.md"), recursive=True)

    note_importanti = []
    diari_chat = []

    for file_path in sorted(files):
        nome_file = os.path.basename(file_path)
        try:
            with open(
                file_path, "r", encoding="utf-8", errors="ignore"
            ) as f:
                contenuto = f.read().strip()
                if not contenuto:
                    continue

                blocco = f"--- NOTA: {nome_file} ---\n{contenuto}\n-------------------"

                if nome_file.startswith("Diario_"):
                    diari_chat.append(blocco)
                else:
                    note_importanti.append(blocco)
        except Exception:
            continue

    diari_recenti = diari_chat[-2:] if len(diari_chat) > 2 else diari_chat
    memoria_finale = note_importanti + diari_recenti
    return "\n\n".join(memoria_finale)


def appendi_conversazione(testo_utente: str, risposta_jarvis: str):
    """Appende l'interazione nella nota diario del giorno corrente."""
    vault_path = get_active_vault_path()

    oggi = datetime.now().strftime("%Y-%m-%d")
    ora = datetime.now().strftime("%H:%M:%S")

    filename = f"Diario_{oggi}.md"
    filepath = os.path.join(vault_path, filename)

    blocco_testo = (
        f"### [{ora}]\n**Utente:** {testo_utente}\n**Jarvis:** {risposta_jarvis}\n\n"
    )

    with _file_lock:
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(blocco_testo)

def cerca_nota_per_titolo(query: str) -> str | None:
    """
    Cerca un file .md nel Vault il cui nome contenga la query (case-insensitive).
    Restituisce il percorso completo del file o None se non trovato.
    """
    vault_path = get_active_vault_path()
    query_clean = query.lower().strip()

    for file_path in glob.glob(os.path.join(vault_path, "**", "*.md"), recursive=True):
        nome_file = os.path.basename(file_path).lower()
        if query_clean in nome_file:
            return file_path
    return None


def leggi_nota_singola(titolo: str) -> tuple[bool, str, str]:
    """
    Legge il contenuto di una specifica nota dato il titolo/nome file.
    Ritorna: (successo: bool, percorso_file: str, contenuto: str)
    """
    file_path = cerca_nota_per_titolo(titolo)
    if not file_path or not os.path.exists(file_path):
        return False, "", f"Nota '{titolo}' non trovata nel Vault."

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            contenuto = f.read()
        return True, file_path, contenuto
    except Exception as e:
        return False, file_path, f"Errore durante la lettura della nota: {e}"


def aggiorna_nota_esistente(titolo: str, nuovo_contenuto: str, modalita: str = "sovrascrivi") -> str:
    """
    Aggiorna una nota esistente nel Vault.
    - modalita='sovrascrivi': sostituisce l'intero contenuto della nota.
    - modalita='appendi': aggiunge il testo in coda mantenendo la nota esistente.
    """
    successo, file_path, contenuto_attuale = leggi_nota_singola(titolo)

    if not successo:
        # Se la nota non esiste, la crea da zero usando salva_nota
        return salva_nota(titolo, nuovo_contenuto)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    if modalita == "appendi":
        testo_finale = (
            f"{contenuto_attuale.strip()}\n\n"
            f"--- Aggiornamento del {timestamp} ---\n"
            f"{nuovo_contenuto}\n"
        )
    else:  # sovrascrivi
        # Mantiene il titolo H1 se presente o ne crea uno pulito
        testo_finale = (
            f"# {Path(file_path).stem}\n\n"
            f"*Ultima modifica di Jarvis il {timestamp}*\n\n"
            f"{nuovo_contenuto}\n"
        )

    with _file_lock:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(testo_finale)

    # Invalida la cache di memoria per rendere subito visibile la modifica al Grafo e a JARVIS
    try:
        from main import invalidate_obsidian_cache
        invalidate_obsidian_cache()
    except Exception as e:
        print(f"[JARVIS Cache Warning] Impossibile invalidare la cache: {e}")

    nome_nota = os.path.basename(file_path)
    return f"Nota '{nome_nota}' aggiornata con successo nella memoria."