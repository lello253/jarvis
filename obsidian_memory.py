import glob
import json
import os
from datetime import datetime
from pathlib import Path


def get_active_vault_path() -> str:
    """Legge dinamicamente il percorso della memoria da config/settings.json."""
    config_path = Path("./config/settings.json")
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            if "memory_folder" in config and config["memory_folder"]:
                path = Path(config["memory_folder"])
                path.mkdir(parents=True, exist_ok=True)
                return str(path)
        except Exception:
            pass

    # Fallback sul valore d'ambiente o sulla cartella locale
    default_vault = Path("./app_memory").resolve()
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH", str(default_vault))
    os.makedirs(vault_path, exist_ok=True)
    return vault_path


def salva_nota(titolo: str, contenuto: str) -> str:
    """Salva una nuova nota in formato Markdown dentro la cartella di memoria."""
    vault_path = get_active_vault_path()

    titolo_pulito = "".join(
        c for c in titolo if c.isalnum() or c in (" ", "_", "-")
    ).strip()
    filename = f"{titolo_pulito}.md"
    filepath = os.path.join(vault_path, filename)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    testo_completo = (
        f"# {titolo}\n\n*Nota creata da Jarvis il {timestamp}*\n\n{contenuto}\n"
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(testo_completo)

    return f"Nota '{titolo}' salvata con successo nella memoria."


def leggi_tutta_la_memoria() -> str:
    """Legge tutti i file .md dando priorità alle note utente rispetto ai diari di chat."""
    vault_path = get_active_vault_path()

    files = glob.glob(
        os.path.join(vault_path, "**", "*.md"), recursive=True
    )

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

    with open(filepath, "a", encoding="utf-8") as f:
        f.write(blocco_testo)