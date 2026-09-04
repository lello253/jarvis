import subprocess
import time
import sys
import os
import threading

def start_main_engine():
    """Avvia il motore logico principale in background."""
    subprocess.Popen([sys.executable, "main.py"], creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

def start_streamlit_ui():
    """Avvia l'interfaccia grafica in background."""
    subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app_ui.py", "--server.headless=true", "--server.port=8501"], creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

if __name__ == "__main__":
    print("Avvio di Jarvis Enterprise in corso...")
    
    # 1. Avvia il motore nativo e l'UI in thread separati e nascosti
    threading.Thread(target=start_main_engine, daemon=True).start()
    threading.Thread(target=start_streamlit_ui, daemon=True).start()
    
    # 2. Attende che i servizi siano pronti
    time.sleep(3)
    
    # 3. Apre l'interfaccia direttamente dentro una finestra Nativa Windows (PyWebView)
    try:
        import webview
        webview.create_window('Jarvis Enterprise Assistant', 'http://localhost:8501', width=1280, height=800)
        webview.start()
    except ImportError:
        # Fallback se pywebview non è installato
        import webbrowser
        webbrowser.open('http://localhost:8501')