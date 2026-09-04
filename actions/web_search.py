# web_search.py
import json
import sys
import re
from pathlib import Path
import urllib.request
import urllib.parse

def web_search_action():
    pass

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR        = _get_base_dir()
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"

def _get_api_key() -> str:
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]

def _fetch_page_content(url: str, timeout: int = 5) -> str:
    """Scrape del contenuto testuale di una pagina web rimuovendo HTML inutile."""
    if not url or not url.startswith("http"):
        return ""
    try:
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        # Pulisce script, CSS e tag HTML
        html = re.sub(r'<(script|style).*?>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<.*?>', ' ', html)
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limita a ~3000 caratteri di testo utile per non appesantire Gemini
        return clean_text[:3000]
    except Exception as e:
        print(f"[WebSearch] ⚠️ Impossibile estrarre {url}: {e}")
        return ""

def _gemini_search(query: str) -> str:
    from google import genai

    client = genai.Client(api_key=_get_api_key())
    
    # Prompt ottimizzato per risposte dettagliate e ricche di dati veri
    enriched_prompt = (
        f"Fornisci una risposta estremamente specifica, approfondita e ricca di dettagli concreti per: '{query}'. "
        "Includi dati, cifre, date e spiegazioni dettagliate trovate dalle fonti più aggiornate su internet."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=enriched_prompt,
        config={"tools": [{"google_search": {}}]},
    )

    text = ""
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if hasattr(part, "text") and part.text:
                text += part.text

    text = text.strip()
    if not text:
        raise ValueError("Gemini non ha restituito dati.")
    return text

def _ddg_search(query: str, max_results: int = 4) -> list[dict]:
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS

    results = []
    with DDGS() as ddgs:
        # Usiamo il parametro 'query' (o primo argomento posizionale)
        for r in ddgs.text(query, max_results=max_results):
            url = r.get("href", "") or r.get("url", "")
            snippet = r.get("body", "")
            
            # Web Scraping: estrae il testo effettivo della pagina
            page_text = _fetch_page_content(url) if url else ""
            
            results.append({
                "title":   r.get("title", ""),
                "snippet": snippet,
                "content": page_text if page_text else snippet,
                "url":     url,
            })
    return results

def _ddg_news(query: str, max_results: int = 5) -> list[dict]:
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS

    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.news(query, max_results=max_results):
                url = r.get("url", "")
                page_text = _fetch_page_content(url) if url else ""
                
                results.append({
                    "title":   r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "content": page_text if page_text else r.get("body", ""),
                    "url":     url,
                    "source":  r.get("source", ""),
                })
    except Exception as e:
        print(f"[WebSearch] ⚠️ DDG news() fallito ({e}) — uso ricerca standard")
        results = _ddg_search(query, max_results=max_results)
    return results

def _format_ddg(query: str, results: list[dict]) -> str:
    if not results:
        return f"Nessun risultato trovato per: {query}"

    lines = [f"Risultati dettagliati per: {query}\n"]
    for i, r in enumerate(results, 1):
        if r.get("title"): 
            lines.append(f"{i}. {r['title']}")
        if r.get("content"): 
            lines.append(f"   Dettagli estratti dal sito: {r['content'][:1200]}")
        if r.get("url"): 
            lines.append(f"   Fonte: {r['url']}")
        lines.append("")
    return "\n".join(lines).strip()

def _format_news(query: str, results: list[dict]) -> str:
    if not results:
        return f"Nessuna notizia trovata per: {query}"

    lines = [f"Ultime notizie su: {query}\n"]
    for i, r in enumerate(results, 1):
        title = r.get("title", "")
        if not title:
            continue
        src = f" [{r['source']}]" if r.get("source") else ""
        lines.append(f"{i}. {title}{src}")
        if r.get("content"):
            lines.append(f"   Contenuto articolo: {r['content'][:1200]}")
        if r.get("url"):
            lines.append(f"   {r['url']}")
        lines.append("")
    return "\n".join(lines).strip()

def _gemini_headlines(n: int = 5) -> tuple[list[str], str]:
    from google import genai

    client = genai.Client(api_key=_get_api_key())
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Top {n} notizie del giorno in Italia e nel mondo. Elenco numerato con soli titoli.",
        config={"tools": [{"google_search": {}}]},
    )

    raw = ""
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if hasattr(part, "text") and part.text:
                raw += part.text

    headlines = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if line and re.match(r'^[\d]+[.\)\-]', line):
            clean = re.sub(r'^[\d]+[.\)\-]\s*', '', line)
            clean = re.sub(r'^\*+\s*', '', clean).strip()
            if clean and len(clean) > 10:
                headlines.append(clean)

    return headlines[:n], raw.strip()

def _search(query: str) -> str:
    try:
        return _gemini_search(query)
    except Exception as e:
        print(f"[WebSearch] ⚠️ Gemini fallito ({e}) — provo web scraping via DDG...")
        results = _ddg_search(query)
        return _format_ddg(query, results)

def _news(query: str) -> str:
    import threading

    gemini_query = f"ultime notizie di oggi su: {query}" if query else "principali notizie di oggi"
    ddg_query    = query if query else "notizie oggi"

    result_box = [None]
    lock       = threading.Lock()
    done_evt   = threading.Event()
    failures   = [0]

    def _store(r: str) -> None:
        if r and len(r) > 60:
            with lock:
                if result_box[0] is None:
                    result_box[0] = r
            done_evt.set()
        else:
            with lock:
                failures[0] += 1
                if failures[0] >= 2:
                    done_evt.set()

    def _try_gemini():
        try:
            _store(_gemini_search(gemini_query))
        except Exception as e:
            print(f"[WebSearch] ⚠️ Gemini news fallito ({e})")
            _store("")

    def _try_ddg():
        try:
            results = _ddg_news(ddg_query, max_results=5)
            _store(_format_news(ddg_query, results))
        except Exception as e:
            print(f"[WebSearch] ⚠️ DDG news fallito ({e})")
            _store("")

    threading.Thread(target=_try_gemini, daemon=True).start()
    threading.Thread(target=_try_ddg,    daemon=True).start()

    done_evt.wait(timeout=10.0)
    return result_box[0] or f"Nessuna notizia trovata per: {query}"

def _research(query: str) -> str:
    research_query = (
        f"Ricerca approfondita ed esaustiva su: '{query}'. "
        "Fornisci dettagli storici, numeri, statistiche, fonti ed elementi chiave esatti trovati nel web."
    )
    try:
        return _gemini_search(research_query)
    except Exception as e:
        print(f"[WebSearch] ⚠️ Research Gemini fallito ({e}) — attivo scraping approfondito...")
        results = _ddg_search(query, max_results=6)
        return _format_ddg(query, results)

def _price(query: str) -> str:
    price_query = f"Prezzo attuale ed offerte in euro per: {query} — quanto costa oggi nei negozi e online"
    try:
        return _gemini_search(price_query)
    except Exception as e:
        print(f"[WebSearch] ⚠️ Price Gemini fallito ({e}) — provo DDG...")
        results = _ddg_search(f"{query} prezzo acquista euro", max_results=4)
        return _format_ddg(query, results)

def _compare(items: list[str], aspect: str) -> str:
    query = (
        f"Confronto dettagliato tra {', '.join(items)} relativamente a {aspect}. "
        "Fornisci dati tecnici specifici, pro e contro e cifre precise."
    )
    try:
        return _gemini_search(query)
    except Exception as e:
        print(f"[WebSearch] ⚠️ Gemini compare fallito: {e} — uso DDG fallback")

    all_results: dict[str, list] = {}
    for item in items:
        try:
            all_results[item] = _ddg_search(f"{item} {aspect}", max_results=3)
        except Exception:
            all_results[item] = []

    lines = [f"Confronto — {aspect.upper()}", "─" * 40]
    for item in items:
        lines.append(f"\n▸ {item}")
        for r in all_results.get(item, [])[:2]:
            if r.get("content"):
                lines.append(f"  • {r['content'][:600]}")
            if r.get("url"):
                lines.append(f"    {r['url']}")
    return "\n".join(lines)

def web_search(
    parameters:     dict,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    params = parameters or {}
    query  = params.get("query", "").strip()
    mode   = params.get("mode",  "search").lower().strip()
    items  = params.get("items", [])
    aspect = params.get("aspect", "general").strip() or "general"

    if not query and not items:
        return "Fornisci una query di ricerca."

    if items and mode not in ("compare",):
        mode = "compare"

    if player:
        player.write_log(f"[Search:{mode}] {query or ', '.join(items)}")

    print(f"[WebSearch] 🔍 mode={mode!r}  query={query!r}")

    try:
        if mode == "compare" and items:
            return _compare(items, aspect)
        if mode == "news":
            return _news(query)
        if mode == "research":
            return _research(query)
        if mode == "price":
            return _price(query)
        return _search(query)

    except Exception as e:
        print(f"[WebSearch] ❌ Tutti i sistemi di ricerca sono falliti: {e}")
        return f"Errore ricerca: {e}"