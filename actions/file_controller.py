import os
import shutil
import platform
from pathlib import Path
from datetime import datetime

try:
    import send2trash
    _SEND2TRASH = True
except ImportError:
    _SEND2TRASH = False

_OS = platform.system()  # "Windows" | "Darwin" | "Linux"

_SAFE_ROOTS: list[Path] = [
    Path.home(),
]

def _is_safe_path(target: Path) -> bool:
    """Verifica se il percorso è all'interno di _SAFE_ROOTS."""
    try:
        resolved = target.resolve()
        return any(
            resolved == root.resolve() or resolved.is_relative_to(root.resolve())
            for root in _SAFE_ROOTS
        )
    except Exception:
        return False

def _get_desktop() -> Path:
    if _OS == "Linux":
        xdg = os.environ.get("XDG_DESKTOP_DIR", "")
        if xdg and Path(xdg).exists():
            return Path(xdg)
    return Path.home() / "Desktop"

def _get_downloads() -> Path:
    if _OS == "Linux":
        xdg = os.environ.get("XDG_DOWNLOAD_DIR", "")
        if xdg and Path(xdg).exists():
            return Path(xdg)
    return Path.home() / "Downloads"

def _get_documents() -> Path:
    if _OS == "Linux":
        xdg = os.environ.get("XDG_DOCUMENTS_DIR", "")
        if xdg and Path(xdg).exists():
            return Path(xdg)
    return Path.home() / "Documents"

def _get_pictures() -> Path:
    if _OS == "Linux":
        xdg = os.environ.get("XDG_PICTURES_DIR", "")
        if xdg and Path(xdg).exists():
            return Path(xdg)
    return Path.home() / "Pictures"

def _get_music() -> Path:
    if _OS == "Linux":
        xdg = os.environ.get("XDG_MUSIC_DIR", "")
        if xdg and Path(xdg).exists():
            return Path(xdg)
    return Path.home() / "Music"

def _get_videos() -> Path:
    if _OS == "Linux":
        xdg = os.environ.get("XDG_VIDEOS_DIR", "")
        if xdg and Path(xdg).exists():
            return Path(xdg)
    return Path.home() / "Videos"

def _get_vault() -> Path:
    """Restituisce il percorso dinamico del Memory Vault di Jarvis."""
    vault = Path.home() / "JarvisMemory"
    vault.mkdir(parents=True, exist_ok=True)
    return vault

def _resolve_path(raw: str) -> Path:
    shortcuts: dict[str, Path] = {
        "desktop":   _get_desktop(),
        "downloads": _get_downloads(),
        "documents": _get_documents(),
        "pictures":  _get_pictures(),
        "music":     _get_music(),
        "videos":    _get_videos(),
        "home":      Path.home(),
        "vault":     _get_vault(),
        "memory":    _get_vault(),
    }
    lower = raw.strip().lower()
    if lower in shortcuts:
        return shortcuts[lower]
    return Path(raw).expanduser()

def _format_size(b: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"

def _safe_trash(target: Path) -> str:
    if not _SEND2TRASH:
        return (
            "send2trash non installato. "
            "Esegui: pip install send2trash — "
            "Cancellazione permanente disabilitata per sicurezza."
        )
    send2trash.send2trash(str(target))
    return f"Spostato nel cestino: {target.name}"


def list_files(path: str = "desktop", show_hidden: bool = False) -> str:
    try:
        target = _resolve_path(path)
        if not _is_safe_path(target):
            return f"Accesso negato: {target}"
        if not target.exists():
            return f"Percorso non trovato: {target}"
        if not target.is_dir():
            return f"Non è una cartella: {target}"

        items = []
        for item in sorted(target.iterdir()):
            if not show_hidden and item.name.startswith("."):
                continue
            if item.is_dir():
                items.append(f"📁 {item.name}/")
            else:
                size = _format_size(item.stat().st_size)
                items.append(f"📄 {item.name} ({size})")

        if not items:
            return f"La cartella è vuota: {target.name}/"

        return f"Contenuto di {target.name}/ ({len(items)} elementi):\n" + "\n".join(items)

    except PermissionError:
        return f"Permesso negato: {path}"
    except Exception as e:
        return f"Errore nell'elencare i file: {e}"


def create_file(path: str, name: str = "", content: str = "") -> str:
    try:
        base   = _resolve_path(path)
        target = (base / name) if name else base
        if not _is_safe_path(target):
            return f"Accesso negato: {target}"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"File creato: {target.name}"
    except Exception as e:
        return f"Impossibile creare il file: {e}"


def create_folder(path: str, name: str = "") -> str:
    try:
        base   = _resolve_path(path)
        target = (base / name) if name else base
        if not _is_safe_path(target):
            return f"Accesso negato: {target}"
        target.mkdir(parents=True, exist_ok=True)
        return f"Cartella creata: {target.name}"
    except Exception as e:
        return f"Impossibile creare la cartella: {e}"


def delete_file(path: str, name: str = "") -> str:
    try:
        base   = _resolve_path(path)
        target = (base / name) if name else base
        if not _is_safe_path(target):
            return f"Accesso negato: {target}"
        if not target.exists():
            return f"Non trovato: {target.name}"

        protected = {
            _get_desktop(), _get_downloads(), _get_documents(),
            _get_pictures(), _get_music(), _get_videos(), Path.home(), _get_vault()
        }
        if target.resolve() in {p.resolve() for p in protected}:
            return f"Cartella protetta, impossibile eliminare: {target.name}"

        return _safe_trash(target)

    except PermissionError:
        return f"Permesso negato: {path}"
    except Exception as e:
        return f"Impossibile eliminare: {e}"


def move_file(path: str, name: str = "", destination: str = "") -> str:
    try:
        base   = _resolve_path(path)
        src    = (base / name) if name else base
        dst    = _resolve_path(destination) if destination else None

        if not src.exists():
            return f"Origine non trovata: {src.name}"
        if dst is None:
            return "Nessuna destinazione specificata."
        if not _is_safe_path(src):
            return f"Accesso negato (origine): {src}"
        if not _is_safe_path(dst):
            return f"Accesso negato (destinazione): {dst}"

        if dst.is_dir():
            dst = dst / src.name

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return f"Spostato: {src.name} → {dst.parent.name}/"

    except Exception as e:
        return f"Impossibile spostare: {e}"


def copy_file(path: str, name: str = "", destination: str = "") -> str:
    try:
        base = _resolve_path(path)
        src  = (base / name) if name else base
        dst  = _resolve_path(destination) if destination else None

        if not src.exists():
            return f"Origine non trovata: {src.name}"
        if dst is None:
            return "Nessuna destinazione specificata."
        if not _is_safe_path(src):
            return f"Accesso negato (origine): {src}"
        if not _is_safe_path(dst):
            return f"Accesso negato (destinazione): {dst}"

        if dst.is_dir():
            dst = dst / src.name

        dst.parent.mkdir(parents=True, exist_ok=True)

        if src.is_dir():
            shutil.copytree(str(src), str(dst))
        else:
            shutil.copy2(str(src), str(dst))

        return f"Copiato: {src.name} → {dst.parent.name}/"

    except Exception as e:
        return f"Impossibile copiare: {e}"


def rename_file(path: str, name: str = "", new_name: str = "") -> str:
    try:
        base     = _resolve_path(path)
        target   = (base / name) if name else base
        if not _is_safe_path(target):
            return f"Accesso negato: {target}"
        if not target.exists():
            return f"Non trovato: {target.name}"
        if not new_name:
            return "Nessun nuovo nome fornito."

        new_path = target.parent / new_name
        if new_path.exists():
            return f"Un file chiamato '{new_name}' esiste già qui."

        target.rename(new_path)
        return f"Rinominato: {target.name} → {new_name}"

    except Exception as e:
        return f"Impossibile rinominare: {e}"


def read_file(path: str, name: str = "", max_chars: int = 4000) -> str:
    try:
        base   = _resolve_path(path)
        target = (base / name) if name else base
        if not _is_safe_path(target):
            return f"Accesso negato: {target}"
        if not target.exists():
            return f"File non trovato: {target.name}"
        if not target.is_file():
            return f"Non è un file: {target.name}"

        # Gestione multilivello delle codifiche per prevenire crash
        try:
            content = target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = target.read_text(encoding="cp1252")
            except Exception:
                content = target.read_text(encoding="utf-8", errors="ignore")

        if len(content) > max_chars:
            content = content[:max_chars] + f"\n\n[Troncato — {len(content)} caratteri totali]"
        return content

    except Exception as e:
        return f"Impossibile leggere il file: {e}"


def write_file(path: str, name: str = "", content: str = "",
               append: bool = False) -> str:
    try:
        base   = _resolve_path(path)
        target = (base / name) if name else base
        if not _is_safe_path(target):
            return f"Accesso negato: {target}"
        target.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with open(target, mode, encoding="utf-8", errors="ignore") as f:
            f.write(content)
        action = "Aggiunto a" if append else "Scritto in"
        return f"{action}: {target.name}"
    except Exception as e:
        return f"Impossibile scrivere il file: {e}"


def find_files(name: str = "", extension: str = "",
               path: str = "home", max_results: int = 20) -> str:
    try:
        search_path = _resolve_path(path)
        if not _is_safe_path(search_path):
            return f"Accesso negato: {search_path}"
        if not search_path.exists():
            return f"Percorso di ricerca non trovato: {path}"

        results    = []
        ignore_dirs = {".git", "node_modules", "__pycache__", "venv", ".venv", "AppData"}

        for root, dirs, files in os.walk(search_path):
            # Esclude cartelle pesanti dal walkthrough
            dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]

            for file in files:
                if file.startswith("."):
                    continue
                
                ext_match = not extension or file.lower().endswith(extension.lower() if extension.startswith(".") else f".{extension.lower()}")
                name_match = not name or name.lower() in file.lower()

                if ext_match and name_match:
                    full_p = Path(root) / file
                    try:
                        size = _format_size(full_p.stat().st_size)
                        results.append(f"📄 {file} ({size}) — {full_p.parent}")
                    except Exception:
                        results.append(f"📄 {file} — {full_p.parent}")

                    if len(results) >= max_results:
                        break
            if len(results) >= max_results:
                break

        if not results:
            query = name or extension or "file"
            return f"Nessun {query} trovato in {search_path.name}/"

        return f"Trovati {len(results)} file:\n" + "\n".join(results)

    except Exception as e:
        return f"Errore di ricerca: {e}"


def get_largest_files(path: str = "downloads", count: int = 10) -> str:
    count = min(count, 50)
    try:
        search_path = _resolve_path(path)
        if not _is_safe_path(search_path):
            return f"Accesso negato: {search_path}"
        if not search_path.exists():
            return f"Percorso non trovato: {path}"

        files = []
        ignore_dirs = {".git", "node_modules", "__pycache__", "venv", ".venv", "AppData"}

        for root, dirs, filenames in os.walk(search_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
            for f in filenames:
                full_p = Path(root) / f
                try:
                    files.append((full_p.stat().st_size, full_p))
                except Exception:
                    continue

        files.sort(reverse=True)
        top = files[:count]

        if not top:
            return "Nessun file trovato."

        lines = [f"I {len(top)} file più grandi in {search_path.name}/:"]
        for size, f in top:
            lines.append(f"  {_format_size(size):>10}  {f.name}  ({f.parent})")

        return "\n".join(lines)

    except Exception as e:
        return f"Errore: {e}"


def get_disk_usage(path: str = "home") -> str:
    try:
        target = _resolve_path(path)
        usage  = shutil.disk_usage(target)
        pct    = usage.used / usage.total * 100
        return (
            f"Spazio disco ({target}):\n"
            f"  Totale : {_format_size(usage.total)}\n"
            f"  Usato  : {_format_size(usage.used)} ({pct:.1f}%)\n"
            f"  Libero : {_format_size(usage.free)}"
        )
    except Exception as e:
        return f"Impossibile ottenere lo spazio disco: {e}"


def organize_desktop() -> str:
    type_map = {
        "Immagini":   {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico", ".heic"},
        "Documenti":  {".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx",
                       ".ppt", ".pptx", ".csv", ".odt", ".ods", ".odp"},
        "Video":      {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"},
        "Musica":     {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"},
        "Archivi":    {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
        "Codice":     {".py", ".js", ".ts", ".html", ".css", ".json", ".xml",
                       ".cpp", ".java", ".cs", ".go", ".rs", ".sh"},
    }

    desktop = _get_desktop()
    moved, skipped = [], []

    try:
        for item in desktop.iterdir():
            if item.is_dir() or item.name.startswith("."):
                continue
            if item.name in {k for k in type_map} or item.name == "Altro":
                continue

            ext        = item.suffix.lower()
            target_dir = desktop / "Altro"
            for folder, exts in type_map.items():
                if ext in exts:
                    target_dir = desktop / folder
                    break

            target_dir.mkdir(exist_ok=True)
            new_path = target_dir / item.name

            if new_path.exists():
                skipped.append(item.name)
                continue

            shutil.move(str(item), str(new_path))
            moved.append(f"{item.name} → {target_dir.name}/")

        result = f"Desktop organizzato: {len(moved)} file spostati."
        if moved:
            preview = moved[:8]
            result += "\n" + "\n".join(preview)
            if len(moved) > 8:
                result += f"\n... e altri {len(moved) - 8}."
        if skipped:
            result += f"\n{len(skipped)} file saltati (conflitto di nomi)."
        return result

    except Exception as e:
        return f"Impossibile organizzare il desktop: {e}"


def get_file_info(path: str, name: str = "") -> str:
    try:
        base   = _resolve_path(path)
        target = (base / name) if name else base
        if not _is_safe_path(target):
            return f"Accesso negato: {target}"
        if not target.exists():
            return f"Non trovato: {target.name}"

        stat = target.stat()
        info = {
            "Nome":          target.name,
            "Tipo":          "Cartella" if target.is_dir() else "File",
            "Dimensione":    _format_size(stat.st_size),
            "Posizione":     str(target.parent),
            "Creato":        datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M"),
            "Modificato":    datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
            "Estensione":    target.suffix or "—",
        }
        return "\n".join(f"  {k}: {v}" for k, v in info.items())

    except Exception as e:
        return f"Impossibile ottenere le informazioni sul file: {e}"

def file_controller(
    parameters: dict = None,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    params = parameters or {}
    action = params.get("action", "").lower().strip()
    path   = params.get("path", "desktop")
    name   = params.get("name", "")

    if player:
        player.write_log(f"[file] {action} {name or path}")

    try:
        if action == "list":
            return list_files(path)

        elif action == "create_file":
            return create_file(path, name=name, content=params.get("content", ""))

        elif action == "create_folder":
            return create_folder(path, name=name)

        elif action == "delete":
            return delete_file(path, name=name)

        elif action == "move":
            return move_file(path, name=name, destination=params.get("destination", ""))

        elif action == "copy":
            return copy_file(path, name=name, destination=params.get("destination", ""))

        elif action == "rename":
            return rename_file(path, name=name, new_name=params.get("new_name", ""))

        elif action == "read":
            return read_file(path, name=name)

        elif action == "write":
            return write_file(
                path, name=name,
                content=params.get("content", ""),
                append=params.get("append", False)
            )

        elif action == "find":
            return find_files(
                name=name or params.get("name", ""),
                extension=params.get("extension", ""),
                path=path,
                max_results=min(int(params.get("max_results", 20)), 50),
            )

        elif action == "largest":
            return get_largest_files(
                path=path,
                count=int(params.get("count", 10)),
            )

        elif action == "disk_usage":
            return get_disk_usage(path)

        elif action == "organize_desktop":
            return organize_desktop()

        elif action == "info":
            return get_file_info(path, name=name)

        else:
            return f"Azione sconosciuta: '{action}'"

    except Exception as e:
        return f"Errore file controller ({action}): {e}"