from __future__ import annotations

import json
import math
import os
import platform
import random
import subprocess
import sys
import threading
import time
from pathlib import Path
from ui_graph import ObsidianGraphView
import psutil

if platform.system() == "Windows":
    _WIN_HIDE: dict = {"creationflags": subprocess.CREATE_NO_WINDOW}
else:
    _WIN_HIDE: dict = {}

from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import QTreeView

from PyQt6.QtCore import (
    QEasingCurve, QMimeData, QObject, QPointF, QRectF, QSize, Qt,
    QTimer, QUrl, pyqtSignal, QDir,
)
from PyQt6.QtGui import (
    QBrush, QColor, QConicalGradient, QDragEnterEvent, QDropEvent, QFont,
    QFontDatabase, QKeySequence, QLinearGradient, QPainter, QPainterPath,
    QPen, QPixmap, QRadialGradient, QShortcut, QTextCursor, QTextBlockFormat, QTextCharFormat,
)
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QPushButton, QScrollArea, QSizePolicy, QSplitter,
    QStackedWidget, QTextEdit, QVBoxLayout, QWidget, QProgressBar, QTabWidget,
)

import importlib.util

import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QComboBox, QCheckBox, QLineEdit, QPushButton, QGroupBox
)

import json
import importlib.util
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel,
    QLineEdit, QComboBox, QCheckBox, QPushButton, QGroupBox, QSlider
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


import json
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from glitter_overlay import GlitterOverlay

class SettingsDialog(QDialog):
    """Dialog delle Impostazioni Avanzate di JARVIS (Temi, Note, Profilo, Audio e AI Engine)."""

    def __init__(self, parent=None, config_path="config.json"):
        super().__init__(parent)
        self.setWindowTitle("⚙ Impostazioni JARVIS")
        self.resize(520, 500)
        self.config_path = config_path
        self.config = self.load_config()

        # Stile Sci-Fi Cyberpunk ottimizzato per l'HUD
        self.setStyleSheet("""
            QDialog {
                background-color: #0b0e14;
                color: #00f0ff;
                font-family: 'Segoe UI', sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #1f293d;
                background: #111622;
                border-radius: 6px;
            }
            QTabBar::tab {
                background: #131722;
                color: #8a99ad;
                padding: 8px 14px;
                border: 1px solid #1f293d;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #1f293d;
                color: #00f0ff;
                font-weight: bold;
            }
            QGroupBox {
                border: 1px solid #1f293d;
                margin-top: 10px;
                padding: 12px;
                color: #00f0ff;
                font-weight: bold;
                border-radius: 6px;
            }
            QLabel {
                color: #8a99ad;
                font-size: 12px;
            }
            QComboBox, QLineEdit {
                background-color: #131722;
                border: 1px solid #1f293d;
                color: #ffffff;
                padding: 6px;
                border-radius: 4px;
                selection-background-color: #00f0ff;
                selection-color: #0b0e14;
            }
            QComboBox:focus, QLineEdit:focus {
                border: 1px solid #00f0ff;
            }
            QCheckBox {
                color: #e2e8f0;
                padding: 4px;
            }
            QPushButton {
                background-color: #131722;
                border: 1px solid #00f0ff;
                color: #00f0ff;
                padding: 8px 18px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00f0ff;
                color: #0b0e14;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: #1f293d;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #00f0ff;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
        """)

        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        # Inizializzazione schede
        self.tabs.addTab(self._create_theme_tab(), "🎨 Temi")
        self.tabs.addTab(self._create_notes_tab(), "📝 Note")
        self.tabs.addTab(self._create_profile_tab(), "👤 Profilo")
        self.tabs.addTab(self._create_voice_tab(), "🎙️️ Audio")
        self.tabs.addTab(self._create_ai_tab(), "🔑 AI Engine")

        main_layout.addWidget(self.tabs)

        # Pulsanti d'azione
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("ANNULLA")
        save_btn = QPushButton("SALVA")

        save_btn.clicked.connect(self.save_and_close)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        main_layout.addLayout(btn_layout)

    def _create_theme_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group = QGroupBox("Schema Colori Interfaccia")
        g_layout = QVBoxLayout(group)

        g_layout.addWidget(QLabel("Seleziona Tema:"))
        self.combo_theme = QComboBox()
        self.combo_theme.addItems([
            "Cyan Cyberpunk (Default)",
            "OLED Obsidian",
            "Dark Enterprise",
            "Neon Fluo",
            "Cloud Sky",
            "Purple Cyberpunk",
            "Ironman Arc Reactor",
            "Sparkle Glitter",
            "Arctic",
            "Matrix",
            "Deep Space",
            "Executive",
            "Ocean",
            "Glass"
        ])

        current_theme = self.config.get("theme", "Cyan Cyberpunk (Default)")
        self.combo_theme.setCurrentText(current_theme)

        g_layout.addWidget(self.combo_theme)
        layout.addWidget(group)
        layout.addStretch()
        return widget

    def _create_notes_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group = QGroupBox("Integrazione Note & HUD")
        g_layout = QVBoxLayout(group)

        self.check_bottom_panel = QCheckBox(
            "Mostra note nel riquadro in basso"
        )
        self.check_bottom_panel.setChecked(
            self.config.get("notes_in_bottom_panel", True)
        )
        g_layout.addWidget(self.check_bottom_panel)

        layout.addWidget(group)
        layout.addStretch()
        return widget

    def _create_profile_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group = QGroupBox("Identità Utente & Assistente")
        g_layout = QVBoxLayout(group)

        g_layout.addWidget(QLabel("Nome Assistente:"))
        self.input_asst_name = QLineEdit(
            self.config.get("assistant_name", "JARVIS")
        )
        g_layout.addWidget(self.input_asst_name)

        g_layout.addWidget(QLabel("Nome Utente:"))
        self.input_user_name = QLineEdit(self.config.get("user_name", "Sir"))
        g_layout.addWidget(self.input_user_name)

        self.check_face_auth = QCheckBox("Riconoscimento facciale all'avvio")
        self.check_face_auth.setChecked(self.config.get("face_auth", True))
        g_layout.addWidget(self.check_face_auth)

        layout.addWidget(group)
        layout.addStretch()
        return widget

    def _create_voice_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group = QGroupBox("Sintesi Vocale & Audio")
        g_layout = QVBoxLayout(group)

        g_layout.addWidget(QLabel("Motore Sintesi Vocale (TTS):"))
        self.combo_tts = QComboBox()
        self.combo_tts.addItems([
            "Edge-TTS (Online High Quality)",
            "Pyttsx3 (Offline Fast)",
            "ElevenLabs API",
        ])
        self.combo_tts.setCurrentText(
            self.config.get("tts_engine", "Edge-TTS (Online High Quality)")
        )
        g_layout.addWidget(self.combo_tts)

        # Contenitore orizzontale per Label + Valore percentuale dello Slider
        speed_header_layout = QHBoxLayout()
        speed_label = QLabel("Velocità Parlato:")
        self.lbl_speed_val = QLabel(f"{self.config.get('voice_speed', 110)}%")
        self.lbl_speed_val.setStyleSheet("color: #00f0ff; font-weight: bold;")

        speed_header_layout.addWidget(speed_label)
        speed_header_layout.addStretch()
        speed_header_layout.addWidget(self.lbl_speed_val)
        g_layout.addLayout(speed_header_layout)

        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setRange(80, 160)
        self.slider_speed.setValue(self.config.get("voice_speed", 110))
        # Update in tempo reale del valore testo %
        self.slider_speed.valueChanged.connect(
            lambda val: self.lbl_speed_val.setText(f"{val}%")
        )

        g_layout.addWidget(self.slider_speed)

        layout.addWidget(group)
        layout.addStretch()
        return widget

    def _create_ai_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group = QGroupBox("Configurazione Modello LLM")
        g_layout = QVBoxLayout(group)

        g_layout.addWidget(QLabel("Provider Modello:"))
        self.combo_model = QComboBox()
        self.combo_model.addItems([
            "Ollama Locale (Qwen / Llama)",
            "Groq Cloud API",
            "OpenAI GPT-4o",
        ])
        self.combo_model.setCurrentText(
            self.config.get("llm_provider", "Ollama Locale (Qwen / Llama)")
        )
        g_layout.addWidget(self.combo_model)

        g_layout.addWidget(QLabel("API Key (se richiesta dal provider):"))
        self.input_api_key = QLineEdit(self.config.get("api_key", ""))
        self.input_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_api_key.setPlaceholderText("Inserisci chiave API...")
        g_layout.addWidget(self.input_api_key)

        layout.addWidget(group)
        layout.addStretch()
        return widget

    def load_config(self) -> dict:
        defaults = {
            "theme": "Cyan Cyberpunk (Default)",
            "notes_in_bottom_panel": True,
            "assistant_name": "JARVIS",
            "user_name": "Sir",
            "face_auth": True,
            "tts_engine": "Edge-TTS (Online High Quality)",
            "voice_speed": 110,
            "llm_provider": "Ollama Locale (Qwen / Llama)",
            "api_key": "",
        }

        if not os.path.exists(self.config_path):
            return defaults

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                defaults.update(data)
                return defaults
        except Exception as e:
            print(f"[Settings Error] Errore durante il caricamento: {e}")
            return defaults

    def save_and_close(self):
        self.config = {
            "theme": self.combo_theme.currentText(),
            "notes_in_bottom_panel": self.check_bottom_panel.isChecked(),
            "assistant_name": self.input_asst_name.text().strip(),
            "user_name": self.input_user_name.text().strip(),
            "face_auth": self.check_face_auth.isChecked(),
            "tts_engine": self.combo_tts.currentText(),
            "voice_speed": self.slider_speed.value(),
            "llm_provider": self.combo_model.currentText(),
            "api_key": self.input_api_key.text().strip(),
        }
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Settings Error] Salvataggio fallito: {e}")

        self.accept()


# Caricamento dinamico del gestore Smart Drop
_spec = importlib.util.find_spec("actions.smart_drop_handler")
if _spec is not None:
    from actions.smart_drop_handler import process_dropped_file
else:
    process_dropped_file = None

def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent

BASE_DIR   = _base_dir()
CONFIG_DIR = BASE_DIR / "config"
API_FILE   = CONFIG_DIR / "api_keys.json"


def _read_full_config() -> dict:
    """Read api_keys.json config dict. Returns {} on any error."""
    try:
        return json.loads(API_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


_DEFAULT_W, _DEFAULT_H = 980, 700
_MIN_W,     _MIN_H     = 820, 580
_LEFT_W  = 148
_RIGHT_W = 340

_OS = platform.system()  # "Windows" | "Darwin" | "Linux"


class C:
    BG        = "#00060a"
    PANEL     = "#010d14"
    PANEL2    = "#010f18"
    BORDER    = "#0d3347"
    BORDER_B  = "#1a5c7a"
    BORDER_A  = "#0f4060"
    PRI       = "#00d4ff"
    PRI_DIM   = "#007a99"
    PRI_GHO   = "#001f2e"
    ACC       = "#ff6b00"
    ACC2      = "#ffcc00"
    GREEN     = "#00ff88"
    GREEN_D   = "#00aa55"
    RED       = "#ff3355"
    MUTED_C   = "#ff3366"
    TEXT      = "#8ffcff"
    TEXT_DIM  = "#3a8a9a"
    TEXT_MED  = "#5ab8cc"
    WHITE     = "#d8f8ff"
    DARK      = "#000d14"
    BAR_BG    = "#011520"


# Ana renge (accent) bağlı anahtarlar — durum renkleri (ACC, GREEN, RED…) sabit kalır
_HUE_LINKED = (
    "BG", "PANEL", "PANEL2", "BORDER", "BORDER_B", "BORDER_A",
    "PRI", "PRI_DIM", "PRI_GHO", "TEXT", "TEXT_DIM", "TEXT_MED",
    "WHITE", "DARK", "BAR_BG",
)
_PALETTE_DEFAULTS: dict[str, str] = {k: getattr(C, k) for k in _HUE_LINKED}

DEFAULT_UI_COLOR = _PALETTE_DEFAULTS["PRI"]


def apply_ui_accent(accent_hex: str) -> bool:
    """
    Seçilen accent rengine göre tüm turkuaz-ailesi paleti yeniden türetir
    (hue kaydırma — parlaklık/doygunluk oranları korunur, tasarım bozulmaz).
    Boyanan öğeler (HUD, dalga formu, metrikler) bir sonraki karede yeni
    rengi alır; stylesheet tabanlı paneller yeniden kurulduklarında alır.
    """
    import colorsys

    accent_hex = (accent_hex or "").strip().lower()
    if not (accent_hex.startswith("#") and len(accent_hex) == 7):
        return False
    try:
        int(accent_hex[1:], 16)
    except ValueError:
        return False

    def _hsv(h: str) -> tuple[float, float, float]:
        r = int(h[1:3], 16) / 255
        g = int(h[3:5], 16) / 255
        b = int(h[5:7], 16) / 255
        return colorsys.rgb_to_hsv(r, g, b)

    base_h            = _hsv(_PALETTE_DEFAULTS["PRI"])[0]
    acc_h, acc_s, _av = _hsv(accent_hex)
    dh   = acc_h - base_h
    grey = acc_s < 0.08   # griye yakın accent → tüm tema desaturize edilir

    for key, hex0 in _PALETTE_DEFAULTS.items():
        h, s, v = _hsv(hex0)
        if grey:
            s *= 0.15
        r, g, b = colorsys.hsv_to_rgb((h + dh) % 1.0, s, v)
        setattr(C, key, "#{:02x}{:02x}{:02x}".format(
            int(r * 255 + 0.5), int(g * 255 + 0.5), int(b * 255 + 0.5)))
    return True


def current_palette() -> dict[str, str]:
    """C sınıfındaki accent'e bağlı renklerin anlık kopyası."""
    return {k: getattr(C, k) for k in _HUE_LINKED}


def retheme_all_widgets(old: dict[str, str], new: dict[str, str]) -> None:
    """
    CANLI tam tema değişimi. Uygulamadaki HER widget'ın stylesheet'inde eski
    palet renklerini yenileriyle değiştirir ve yeniden çizdirir. Böylece renk
    değişimi yalnızca boyanan öğelerde değil, panel/buton/kenarlık dahil tüm
    arayüzde ANINDA uygulanır — yeniden başlatma gerekmez.
    """
    mapping = {old[k].lower(): new[k].lower()
               for k in old if old[k].lower() != new.get(k, old[k]).lower()}
    if not mapping:
        return
    app = QApplication.instance()
    if app is None:
        return
    for w in app.allWidgets():
        try:
            ss = w.styleSheet()
            if ss:
                s2 = ss
                for o, n in mapping.items():
                    if o in s2:
                        s2 = s2.replace(o, n)
                if s2 != ss:
                    w.setStyleSheet(s2)
            w.update()
        except Exception:
            pass


def qcol(h: str, a: int = 255) -> QColor:
    c = QColor(h); c.setAlpha(a); return c


# ── Windows GPU via NVML DLL (no subprocess, no console window) ──────────────
_nvml_lib: object = None   # cached ctypes DLL
_nvml_ok:  object = None   # None=untested, True=works, False=unavailable


def _nvml_gpu_windows() -> float:
    """Return NVIDIA GPU utilisation % using nvml.dll directly — zero subprocess."""
    global _nvml_lib, _nvml_ok
    if _nvml_ok is False:
        return -1.0
    try:
        import ctypes

        class _Util(ctypes.Structure):
            _fields_ = [("gpu", ctypes.c_uint), ("memory", ctypes.c_uint)]

        if _nvml_lib is None:
            for dll_name in ("nvml", r"C:\Windows\System32\nvml.dll"):
                try:
                    lib = ctypes.WinDLL(dll_name)
                    lib.nvmlInit_v2()
                    _nvml_lib = lib
                    break
                except Exception:
                    continue

        if _nvml_lib is None:
            import pynvml  # type: ignore
            pynvml.nvmlInit()
            h = pynvml.nvmlDeviceGetHandleByIndex(0)
            _nvml_ok = True
            return float(pynvml.nvmlDeviceGetUtilizationRates(h).gpu)

        dev = ctypes.c_void_p()
        _nvml_lib.nvmlDeviceGetHandleByIndex_v2(0, ctypes.byref(dev))
        util = _Util()
        _nvml_lib.nvmlDeviceGetUtilizationRates(dev, ctypes.byref(util))
        _nvml_ok = True
        return float(util.gpu)
    except Exception:
        _nvml_ok = False
        return -1.0


class _SysMetrics:
    def __init__(self):
        self.cpu  = 0.0
        self.mem  = 0.0
        self.net  = 0.0   
        self.gpu  = -1.0  
        self.tmp  = -1.0  
        self._lock = threading.Lock()
        self._last_net = psutil.net_io_counters()
        self._last_net_t = time.time()
        self._running = True
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()

    def _loop(self):
        while self._running:
            try:
                self._update()
            except Exception:
                pass
            time.sleep(1.5)

    def _update(self):
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent

        nc  = psutil.net_io_counters()
        now = time.time()
        dt  = now - self._last_net_t
        if dt > 0:
            sent = (nc.bytes_sent - self._last_net.bytes_sent) / dt
            recv = (nc.bytes_recv - self._last_net.bytes_recv) / dt
            net  = (sent + recv) / (1024 * 1024)
        else:
            net = 0.0
        self._last_net   = nc
        self._last_net_t = now

        gpu = self._get_gpu()

        tmp = self._get_temp()

        with self._lock:
            self.cpu = cpu
            self.mem = mem
            self.net = net
            self.gpu = gpu
            self.tmp = tmp

    def _get_gpu(self) -> float:
        # pynvml — subprocess-free, works on all platforms if installed
        try:
            import pynvml  # type: ignore
            pynvml.nvmlInit()
            h = pynvml.nvmlDeviceGetHandleByIndex(0)
            return float(pynvml.nvmlDeviceGetUtilizationRates(h).gpu)
        except Exception:
            pass

        # Windows: nvml.dll via ctypes (already cached in _nvml_gpu_windows)
        if _OS == "Windows":
            return _nvml_gpu_windows()

        # Linux / macOS: libnvidia-ml shared lib via ctypes
        try:
            import ctypes
            _lib = "libnvidia-ml.so.1" if _OS == "Linux" else "libnvidia-ml.dylib"

            class _Util(ctypes.Structure):
                _fields_ = [("gpu", ctypes.c_uint), ("memory", ctypes.c_uint)]

            nv = ctypes.CDLL(_lib)
            nv.nvmlInit_v2()
            dev = ctypes.c_void_p()
            nv.nvmlDeviceGetHandleByIndex_v2(0, ctypes.byref(dev))
            u = _Util()
            nv.nvmlDeviceGetUtilizationRates(dev, ctypes.byref(u))
            return float(u.gpu)
        except Exception:
            pass

        return -1.0   # N/A — zero subprocess on all platforms

    def _get_temp(self) -> float:
        # psutil — works on Linux; occasionally Windows with driver support
        try:
            temps = psutil.sensors_temperatures()
            for name in ["coretemp", "k10temp", "cpu_thermal", "acpitz",
                         "cpu-thermal", "zenpower", "it8688"]:
                if name in temps and temps[name]:
                    return temps[name][0].current
            for entries in temps.values():
                if entries:
                    return entries[0].current
        except Exception:
            pass

        # Windows: wmi module (pure Python COM, zero subprocess)
        if _OS == "Windows":
            try:
                import wmi  # type: ignore
                w = wmi.WMI(namespace="root/wmi")
                tz = w.MSAcpi_ThermalZoneTemperature()
                if tz:
                    return (tz[0].CurrentTemperature / 10.0) - 273.15
            except Exception:
                pass

        return -1.0   # N/A — zero subprocess on all platforms

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "cpu": self.cpu,
                "mem": self.mem,
                "net": self.net,
                "gpu": self.gpu,
                "tmp": self.tmp,
            }


_metrics = _SysMetrics()

import math
import random
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QFont
from PyQt6.QtWidgets import QWidget, QSizePolicy

import math
import random
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QFont
from PyQt6.QtWidgets import QWidget, QSizePolicy

class HudCanvas(QWidget):
    """Core d'Energia Volumetric - Sfera Reattiva & Reattore Arc Sincronizzato alla Voce."""
    def __init__(self, face_path: str = "", assistant_name: str = "J.A.R.V.I.S", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.setMinimumSize(320, 320)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.muted    = False
        self.speaking = False
        self.state    = "INITIALISING"
        self._assistant_name = assistant_name

        self._tick = 0.0
        self._scale = 1.0
        self._tgt_scale = 1.0
        
        # Tema e Colori
        self._theme_name = "Cyan Cyberpunk (Default)"
        self._theme_bg   = QColor("#080a0f")
        self._theme_main = QColor("#00f0ff")
        self._theme_sec  = QColor("#0055ff")

        self._curr_main = QColor("#00f0ff")
        self._curr_sec  = QColor("#0055ff")
        self._last_voice_tick = 0.0

        self._tmr = QTimer(self)
        self._tmr.timeout.connect(self._step)
        self._tmr.start(16)  # 60 FPS

    def apply_theme_colors(self, bg_hex: str, main_hex: str, sec_hex: str, theme_name: str = "Cyan Cyberpunk (Default)"):
        self._theme_name = theme_name
        self._theme_bg   = QColor(bg_hex)
        self._theme_main = QColor(main_hex)
        self._theme_sec  = QColor(sec_hex)
        
        # FORZA L'AGGIORNAMENTO ISTANTANEO (senza aspettare il lerp lento)
        self._curr_main  = QColor(main_hex)
        self._curr_sec   = QColor(sec_hex)
        
        self.update()

    def _step(self):
        self._tick += 0.05
        
        if self.speaking:
            if self._tick - self._last_voice_tick > random.uniform(0.06, 0.12):
                self._tgt_scale = random.uniform(1.15, 1.45)
                self._last_voice_tick = self._tick
            sp = 0.35
        elif self.state in ("THINKING", "PROCESSING"):
            self._tgt_scale = 0.95 + math.sin(self._tick * 3.0) * 0.05
            sp = 0.12
        else:
            self._tgt_scale = 1.0 + math.sin(self._tick * 1.2) * 0.03
            sp = 0.08

        self._scale += (self._tgt_scale - self._scale) * sp
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Sfondo Scuro Deep Space dinamico
        p.fillRect(self.rect(), self._theme_bg)

        W, H = self.width(), self.height()
        cx, cy = W / 2, H / 2
        fw = min(W, H)

        # 1. GESTIONE CROMATICA VINCOLATA AL TEMA ATTIVO
        if self.muted:
            target_main, target_sec = QColor("#ff3355"), QColor("#ff6b00")
        else:
            # USA SEMPRE I COLORI DEL TEMA SELEZIONATO (SENZA SOVRASCRIVERLI CON L'AZZURRO FISSO)
            target_main, target_sec = self._theme_main, self._theme_sec

        # Forza l'assegnazione immediata dei colori del tema
        self._curr_main = target_main
        self._curr_sec  = target_sec

        # 2. CORNER BRACKETS DINAMICI
        bracket_pen = QPen(QColor(self._curr_main.red(), self._curr_main.green(), self._curr_main.blue(), 140))
        bracket_pen.setWidth(2)
        p.setPen(bracket_pen)
        b_len, margin = 18, 12

        p.drawLine(margin, margin, margin + b_len, margin)
        p.drawLine(margin, margin, margin, margin + b_len)
        p.drawLine(W - margin, margin, W - margin - b_len, margin)
        p.drawLine(W - margin, margin, W - margin, margin + b_len)

        p.drawLine(margin, H - margin, margin + b_len, H - margin)
        p.drawLine(margin, H - margin, margin, H - margin - b_len)
        p.drawLine(W - margin, H - margin, W - margin - b_len, H - margin)
        p.drawLine(W - margin, H - margin, W - margin, H - margin - b_len)

        # 3. DISAGNO CORE (REATTORE ARC O ORB TEMA)
        theme_lower = str(self._theme_name).lower()
        if "ironman" in theme_lower or "iron" in theme_lower or "arc" in theme_lower:
            self._draw_arc_reactor(p, cx, cy, fw)
        else:
            self._draw_standard_orb(p, cx, cy, fw)

        # 4. BADGE STATO
        sy = cy + fw * 0.40
        if self.muted:
            txt, col = "⊘  SYSTEM MUTED", QColor("#ff3355")
        elif self.speaking:
            txt, col = "●  SPEAKING", self._curr_main
        elif self.state in ("THINKING", "PROCESSING"):
            txt, col = "◈  PROCESSING...", self._curr_main
        else:
            txt, col = f"●  {self.state}", self._curr_main

        p.setPen(QPen(col, 1))
        p.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        p.drawText(QRectF(0, sy, W, 20), Qt.AlignmentFlag.AlignCenter, txt)
        
    def _draw_arc_reactor(self, p: QPainter, cx: float, cy: float, fw: float):
        """Disegna il Reattore Arc di Tony Stark."""
        max_r = fw * 0.30 * self._scale

        # A. Glow esterno
        glow_r = max_r * (1.8 if not self.speaking else 2.2)
        glow_grad = QRadialGradient(QPointF(cx, cy), glow_r)
        
        c_glow = QColor(self._curr_main)
        c_glow.setAlpha(int(160 + (self._scale - 1.0) * 200) if self.speaking else 120)
        glow_grad.setColorAt(0.0, c_glow)
        glow_grad.setColorAt(0.5, QColor(self._curr_main.red(), self._curr_main.green(), self._curr_main.blue(), 40))
        glow_grad.setColorAt(1.0, QColor(0, 0, 0, 0))

        p.setBrush(QBrush(glow_grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), glow_r, glow_r)

        # B. Anello Esterno Oro Stark
        r_outer = max_r * 0.85
        p.setPen(QPen(self._curr_sec, 3.0))  # Oro Stark
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QPointF(cx, cy), r_outer, r_outer)

        # C. Anello Interno Ciano/Main
        r_inner = max_r * 0.60
        p.setPen(QPen(self._curr_main, 4.0))
        p.drawEllipse(QPointF(cx, cy), r_inner, r_inner)

        # D. Spicchi Radiali Rotanti (10 Bobine)
        p.save()
        p.translate(cx, cy)
        p.rotate(self._tick * 30.0)
        
        p.setPen(QPen(QColor("#ffffff"), 2.5))
        for i in range(10):
            angle = i * (2 * math.pi / 10)
            x1 = r_inner * math.cos(angle)
            y1 = r_inner * math.sin(angle)
            x2 = r_outer * math.cos(angle)
            y2 = r_outer * math.sin(angle)
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            
        p.restore()

        # E. Anello Intermedio Tratteggiato Rotante in Senso Opposto
        p.save()
        p.translate(cx, cy)
        p.rotate(-self._tick * 40.0)
        p.setPen(QPen(self._curr_sec, 1.5, Qt.PenStyle.DashLine))
        p.drawEllipse(QPointF(0, 0), max_r * 0.42, max_r * 0.42)
        p.restore()

        # F. Core Centrale
        core_r = max_r * 0.28
        core_grad = QRadialGradient(QPointF(cx, cy), core_r)
        core_grad.setColorAt(0.0, QColor("#ffffff"))
        core_grad.setColorAt(0.7, self._curr_main)
        core_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(core_grad))
        p.setPen(QPen(QColor("#ffffff"), 1.5))
        p.drawEllipse(QPointF(cx, cy), core_r, core_r)

    def _draw_standard_orb(self, p: QPainter, cx: float, cy: float, fw: float):
        """Disegna l'Orb Volumetrico dinamico adattato ai colori del tema attivo."""
        core_r = fw * 0.16 * self._scale

        # Glow d'Ambiente
        glow_r = core_r * (3.0 if not self.speaking else 3.6)
        glow_grad = QRadialGradient(QPointF(cx, cy), glow_r)
        
        c_amb = QColor(self._curr_main)
        c_amb.setAlpha(int(60 + (self._scale - 1.0) * 350) if self.speaking else 60)
        glow_grad.setColorAt(0.0, c_amb)
        
        c_sec_amb = QColor(self._curr_sec)
        c_sec_amb.setAlpha(30)
        glow_grad.setColorAt(0.55, c_sec_amb)
        glow_grad.setColorAt(1.0, QColor(0, 0, 0, 0))

        p.setBrush(QBrush(glow_grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), glow_r, glow_r)

        # Sfera Centrale (Usa i colori dinamici del tema)
        body_grad = QRadialGradient(QPointF(cx, cy), core_r)
        body_grad.setColorAt(0.0, QColor("#ffffff"))
        c_mid = QColor(self._curr_main)
        c_mid.setAlpha(240)
        body_grad.setColorAt(0.35, c_mid)
        c_edge = QColor(self._curr_sec)
        c_edge.setAlpha(180)
        body_grad.setColorAt(0.75, c_edge)
        body_grad.setColorAt(1.0, QColor(0, 0, 0, 0))

        p.setBrush(QBrush(body_grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), core_r, core_r)

        # Hotspot Centrale
        center_r = core_r * 0.35
        center_grad = QRadialGradient(QPointF(cx, cy), center_r)
        center_grad.setColorAt(0.0, QColor("#ffffff"))
        c_c_edge = QColor(self._curr_main)
        c_c_edge.setAlpha(255)
        center_grad.setColorAt(0.8, c_c_edge)
        center_grad.setColorAt(1.0, QColor(0, 0, 0, 0))

        p.setBrush(QBrush(center_grad))
        p.drawEllipse(QPointF(cx, cy), center_r, center_r)
        
class MetricBar(QWidget):

    def __init__(self, label: str, color: str = C.PRI, parent=None):
        super().__init__(parent)
        self._label = label
        self._color = color
        self._value = 0.0       # 0–100
        self._text  = "--"
        self.setFixedHeight(38)
        self.setMinimumWidth(80)

    def set_value(self, pct: float, text: str):
        self._value = max(0.0, min(100.0, pct))
        self._text  = text
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H = self.width(), self.height()

        # Sfondo Slate minimalista
        p.setBrush(QBrush(QColor("#131722")))
        p.setPen(QPen(QColor("#1f293d"), 1))
        p.drawRoundedRect(QRectF(1, 1, W - 2, H - 2), 4, 4)

        bar_h   = 4
        bar_y   = H - bar_h - 5
        bar_w   = W - 12
        bar_x   = 6
        fill_w  = int(bar_w * self._value / 100)

        p.setBrush(QBrush(QColor("#0b0e14")))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(bar_x, bar_y, bar_w, bar_h), 2, 2)

        if self._value > 85:
            bar_col = QColor("#ff3355")
        elif self._value > 65:
            bar_col = QColor("#ffcc00")
        else:
            bar_col = qcol(self._color)

        if fill_w > 0:
            p.setBrush(QBrush(bar_col))
            p.drawRoundedRect(QRectF(bar_x, bar_y, fill_w, bar_h), 2, 2)

        # Label della metrica in Segoe UI (es. CPU)
        p.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        p.setPen(QPen(QColor("#8a99b5"), 1))
        p.drawText(QRectF(8, 4, 50, 14), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self._label)

        # Valore percentuale in Consolas (es. 17%)
        p.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        p.setPen(QPen(bar_col if self._text != "--" else QColor("#5a657b"), 1))
        p.drawText(QRectF(0, 4, W - 6, 16), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, self._text)

class LogWidget(QTextEdit):
    _sig = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 9))
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: #0b0e14;
                color: #e2e8f0;
                border: 1px solid #1f293d;
                border-radius: 6px;
                padding: 10px;
                selection-background-color: #1c2333;
                selection-color: #00f0ff;
            }}
            QScrollBar:vertical {{
                background: #0b0e14;
                width: 6px;
                border: none;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: #1f293d;
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #00f0ff;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """)
        self._queue: list[str] = []
        self._typing  = False
        self._text    = ""
        self._pos     = 0
        self._tag     = "sys"
        self._ai_name_lc = "jarvis"   # updated when assistant name changes
        self._tmr = QTimer(self)
        self._tmr.timeout.connect(self._step)
        self._sig.connect(self._enqueue)

    def append_log(self, text: str):
        self._sig.emit(text)

    def _enqueue(self, text: str):
        self._queue.append(text)
        if not self._typing:
            self._next()

    def _next(self):
        if not self._queue:
            self._typing = False
            return
        self._typing = True
        self._text   = self._queue.pop(0)
        self._pos    = 0
        tl = self._text.lower()
        _ai_pfx = f"{self._ai_name_lc}:"
        if   tl.startswith("you:"):                               self._tag = "you"
        elif tl.startswith(_ai_pfx) or tl.startswith("jarvis:"): self._tag = "ai"
        elif tl.startswith("file:"):                             self._tag = "file"
        elif "err" in tl:                                        self._tag = "err"
        else:                                                    self._tag = "sys"
        self._tmr.start(4)  # Leggermente più veloce per una digitazione istantanea

    def _step(self):
        if self._pos < len(self._text):
            ch  = self._text[self._pos]
            cur = self.textCursor()
            fmt = cur.charFormat()
            
            # Mappatura dei colori della nuova palette Cyberpunk
            col_map = {
                "you":  QColor("#e2e8f0"), # Bianco pulito
                "ai":   QColor("#00f0ff"), # Cyan Neon
                "err":  QColor("#ff3355"), # Rosso
                "file": QColor("#00ff88"), # Verde Neon
                "sys":  QColor("#a142ff"), # Viola Elettrico
            }
            col = col_map.get(self._tag, QColor("#8a99b5"))
            
            fmt.setForeground(QBrush(col))
            cur.movePosition(cur.MoveOperation.End)
            cur.insertText(ch, fmt)
            self.setTextCursor(cur)
            self.ensureCursorVisible()
            self._pos += 1
        else:
            self._tmr.stop()
            cur = self.textCursor()
            cur.movePosition(cur.MoveOperation.End)
            cur.insertText("\n")
            self.setTextCursor(cur)
            self.ensureCursorVisible()
            QTimer.singleShot(15, self._next)

_FILE_ICONS = {
    "image":   ("🖼", "#00d4ff"), "video":   ("🎬", "#ff6b00"),
    "audio":   ("🎵", "#cc44ff"), "pdf":     ("📄", "#ff4444"),
    "word":    ("📝", "#4488ff"), "excel":   ("📊", "#44bb44"),
    "code":    ("💻", "#ffcc00"), "archive": ("📦", "#ff8844"),
    "pptx":    ("📊", "#ff6622"), "text":    ("📃", "#aaaaaa"),
    "data":    ("🔧", "#88ddff"), "unknown": ("📎", "#888888"),
}
_EXT_TO_CAT = {
    **dict.fromkeys(["jpg","jpeg","png","gif","webp","bmp","tiff","svg","ico"], "image"),
    **dict.fromkeys(["mp4","avi","mov","mkv","wmv","flv","webm","m4v"],         "video"),
    **dict.fromkeys(["mp3","wav","ogg","m4a","aac","flac","wma","opus"],        "audio"),
    **dict.fromkeys(["pdf"],                                                     "pdf"),
    **dict.fromkeys(["doc","docx"],                                              "word"),
    **dict.fromkeys(["xls","xlsx","ods"],                                        "excel"),
    **dict.fromkeys(["ppt","pptx"],                                              "pptx"),
    **dict.fromkeys(["py","js","ts","jsx","tsx","html","css","java","c","cpp",
                     "cs","go","rs","rb","php","swift","kt","sh","sql","lua"],   "code"),
    **dict.fromkeys(["zip","rar","tar","gz","7z","bz2","xz"],                   "archive"),
    **dict.fromkeys(["txt","md","rst","log"],                                    "text"),
    **dict.fromkeys(["csv","tsv","json","xml"],                                  "data"),
}

def _file_category(path: Path) -> str:
    return _EXT_TO_CAT.get(path.suffix.lower().lstrip("."), "unknown")

def _fmt_size(size: int) -> str:
    if   size < 1024:    return f"{size} B"
    elif size < 1024**2: return f"{size/1024:.1f} KB"
    elif size < 1024**3: return f"{size/1024**2:.1f} MB"
    else:                return f"{size/1024**3:.1f} GB"


class FileDropZone(QWidget):
    file_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(100)
        self._current_file: str | None = None
        self._hovering  = False
        self._drag_over = False
        self._dash_offset = 0.0
        self._anim_tmr = QTimer(self)
        self._anim_tmr.timeout.connect(self._animate)
        self._anim_tmr.start(40)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._canvas = _DropCanvas(self)
        layout.addWidget(self._canvas)

    def _animate(self):
        self._dash_offset = (self._dash_offset + 0.8) % 20
        self._canvas.update()

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self._drag_over = True; self._canvas.update()

    def dragLeaveEvent(self, e):
        self._drag_over = False; self._canvas.update()

    def dropEvent(self, e: QDropEvent):
        self._drag_over = False
        urls = e.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if Path(path).is_file():
                self._set_file(path)
        self._canvas.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._browse()

    def enterEvent(self, e):
        self._hovering = True; self._canvas.update()

    def leaveEvent(self, e):
        self._hovering = False; self._canvas.update()

    def current_file(self) -> str | None:
        return self._current_file

    def clear_file(self):
        self._current_file = None; self._canvas.update()

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select a file for JARVIS", str(Path.home()),
            "All Files (*.*);;"
            "Images (*.jpg *.jpeg *.png *.gif *.webp *.bmp *.svg);;"
            "Documents (*.pdf *.docx *.txt *.md *.pptx);;"
            "Data (*.csv *.xlsx *.json *.xml);;"
            "Code (*.py *.js *.ts *.html *.css *.java *.cpp *.go);;"
            "Audio (*.mp3 *.wav *.ogg *.m4a *.aac *.flac);;"
            "Video (*.mp4 *.avi *.mov *.mkv *.wmv *.webm);;"
            "Archives (*.zip *.rar *.tar *.gz *.7z)",
        )
        if path:
            self._set_file(path)

    def _set_file(self, path: str):
        self._current_file = path
        self._canvas.update()
        self.file_selected.emit(path)

        # Invocazione automatica del menu Smart Drop sulle finestre reali
        try:
            from actions.smart_drop_handler import process_dropped_file
            process_dropped_file(path, parent_window=self.window())
        except Exception as e:
            print(f"[SmartDrop Error] Impossibile aprire il menu d'azione: {e}")

class _DropCanvas(QWidget):
    def __init__(self, zone: FileDropZone):
        super().__init__(zone)
        self._z = zone

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        z    = self._z
        W, H = self.width(), self.height()
        pad  = 4
        rect = QRectF(pad, pad, W - pad * 2, H - pad * 2)

        # Sfondo Slate Scuro dinamico
        bg_col = QColor("#002433" if z._drag_over else ("#131722" if z._hovering else "#0b0e14"))
        p.setBrush(QBrush(bg_col))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(rect, 4, 4)

        # Colore bordo in base allo stato
        if z._current_file:   border_col = QColor("#00ff88")
        elif z._drag_over:    border_col = QColor("#00f0ff")
        elif z._hovering:     border_col = QColor("#7000ff")
        else:                 border_col = QColor("#1f293d")

        pen = QPen(border_col, 1.2, Qt.PenStyle.DashLine if not z._current_file else Qt.PenStyle.SolidLine)
        pen.setDashOffset(z._dash_offset)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(rect, 4, 4)

        if z._current_file:   self._paint_file(p, W, H)
        elif z._drag_over:    self._paint_drag_over(p, W, H)
        else:                 self._paint_idle(p, W, H, z._hovering)

    def _paint_idle(self, p, W, H, hover):
        cx, cy = W / 2, H / 2 - 6
        col = QColor("#00f0ff" if hover else "#5a657b")
        
        # Icona Upload Vettoriale
        p.setPen(QPen(col, 1.8))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawLine(QPointF(cx, cy - 10), QPointF(cx, cy + 6))
        p.drawLine(QPointF(cx - 6, cy - 4), QPointF(cx, cy - 10))
        p.drawLine(QPointF(cx + 6, cy - 4), QPointF(cx, cy - 10))
        p.drawLine(QPointF(cx - 10, cy + 6), QPointF(cx + 10, cy + 6))
        
        # Testo minimal
        p.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        p.setPen(QPen(QColor("#e2e8f0" if hover else "#8a99b5"), 1))
        p.drawText(QRectF(0, cy + 12, W, 16), Qt.AlignmentFlag.AlignCenter, "DROP FILE  OR  CLICK TO BROWSE")
        
        p.setFont(QFont("Consolas", 7))
        p.setPen(QPen(QColor("#5a657b"), 1))
        p.drawText(QRectF(0, cy + 28, W, 14), Qt.AlignmentFlag.AlignCenter, "Images · Video · Audio · PDF · Docs · Code · Data")

    def _paint_drag_over(self, p, W, H):
        cx, cy = W / 2, H / 2
        p.setFont(QFont("Consolas", 16, QFont.Weight.Bold))
        p.setPen(QPen(QColor("#00f0ff"), 1))
        p.drawText(QRectF(0, cy - 16, W, 24), Qt.AlignmentFlag.AlignCenter, "[ RELEASE TO LOAD ]")

    def _paint_file(self, p, W, H):
        path = Path(self._z._current_file)
        cat  = _file_category(path)
        icon, icon_col = _FILE_ICONS.get(cat, _FILE_ICONS["unknown"])
        size_str = _fmt_size(path.stat().st_size)
        ext_str  = path.suffix.upper().lstrip(".") or "FILE"

        block_x, block_w = 10, 45
        p.setFont(QFont("Segoe UI Emoji", 18) if _OS == "Windows" else QFont("Arial", 18))
        p.setPen(QPen(qcol(icon_col), 1))
        p.drawText(QRectF(block_x, 0, block_w, H), Qt.AlignmentFlag.AlignCenter, icon)

        tx = block_x + block_w + 4
        tw = W - tx - 36

        p.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        p.setPen(QPen(QColor("#00ff88"), 1))
        name = path.name if len(path.name) <= 32 else path.name[:29] + "..."
        p.drawText(QRectF(tx, H * 0.18, tw, 16), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, name)

        p.setFont(QFont("Consolas", 7))
        p.setPen(QPen(QColor("#8a99b5"), 1))
        p.drawText(QRectF(tx, H * 0.18 + 16, tw, 14), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"{ext_str}  ·  {size_str}")

        # Bottone d'eliminazione ✕
        p.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        p.setPen(QPen(QColor("#ff3355"), 1))
        p.drawText(QRectF(W - 30, 0, 24, H), Qt.AlignmentFlag.AlignCenter, "✕")

    def mousePressEvent(self, e):
        z = self._z
        if z._current_file and e.pos().x() > self.width() - 34:
            z.clear_file()
        else:
            z.mousePressEvent(e)


class _CameraPreview(QWidget):
    """Floating overlay that briefly shows what the camera captured."""

    _W, _H = 244, 188

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            _CameraPreview {{
                background: rgba(0, 6, 10, 242);
                border: 1px solid {C.PRI};
                border-radius: 6px;
            }}
        """)
        self.setFixedWidth(self._W)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 5, 6, 6)
        lay.setSpacing(4)

        hdr = QHBoxLayout()
        title = QLabel("◈  VISUAL INPUT")
        title.setFont(QFont("Courier New", 7, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C.PRI}; background: transparent;")
        hdr.addWidget(title)
        hdr.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(16, 16)
        close_btn.setFont(QFont("Courier New", 8))
        close_btn.setStyleSheet(
            f"color: {C.TEXT_DIM}; background: transparent; border: none;"
        )
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.hide)
        hdr.addWidget(close_btn)
        lay.addLayout(hdr)

        self._img_lbl = QLabel()
        self._img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._img_lbl.setStyleSheet("background: transparent;")
        lay.addWidget(self._img_lbl)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

        self.hide()

    def show_frame(self, img_bytes: bytes) -> None:
        px = QPixmap()
        px.loadFromData(img_bytes)
        if not px.isNull():
            max_w = self._W - 12
            scaled = px.scaled(
                max_w, 160,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._img_lbl.setPixmap(scaled)
            self._img_lbl.setFixedSize(scaled.width(), scaled.height())
            self.adjustSize()
        self.show()
        self.raise_()
        self._timer.start(6_000)   # auto-dismiss after 6 s


class SetupOverlay(QWidget):
    done = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            SetupOverlay {{
                background: rgba(0, 6, 10, 245);
                border: 1px solid {C.BORDER_B};
                border-radius: 6px;
            }}
        """)

        detected = {"darwin": "mac", "windows": "windows"}.get(
            _OS.lower(), "linux"
        )
        self._sel_os = detected

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 22, 30, 22)
        layout.setSpacing(8)

        def _lbl(txt, font_size=9, bold=False, color=C.PRI,
                 align=Qt.AlignmentFlag.AlignCenter):
            w = QLabel(txt)
            w.setAlignment(align)
            w.setFont(QFont("Courier New", font_size,
                            QFont.Weight.Bold if bold else QFont.Weight.Normal))
            w.setStyleSheet(f"color: {color}; background: transparent;")
            return w

        layout.addWidget(_lbl("◈  INITIALISATION REQUIRED", 13, True))
        layout.addWidget(_lbl("Configure J.A.R.V.I.S. before first boot.", 9, color=C.PRI_DIM))
        layout.addSpacing(6)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {C.BORDER};"); layout.addWidget(sep)
        layout.addSpacing(4)

        layout.addWidget(_lbl("GEMINI API KEY", 8, color=C.TEXT_DIM,
                               align=Qt.AlignmentFlag.AlignLeft))
        self._key_input = QLineEdit()
        self._key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._key_input.setPlaceholderText("AIza…")
        self._key_input.setFont(QFont("Courier New", 10))
        self._key_input.setFixedHeight(32)
        self._key_input.setStyleSheet(f"""
            QLineEdit {{
                background: #000d12; color: {C.TEXT};
                border: 1px solid {C.BORDER}; border-radius: 3px; padding: 4px 8px;
            }}
            QLineEdit:focus {{ border: 1px solid {C.PRI}; }}
        """)
        layout.addWidget(self._key_input)
        layout.addSpacing(12)

        sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"color: {C.BORDER};"); layout.addWidget(sep2)
        layout.addSpacing(4)

        layout.addWidget(_lbl("OPERATING SYSTEM", 8, color=C.TEXT_DIM,
                               align=Qt.AlignmentFlag.AlignLeft))
        det_name = {"windows": "Windows", "mac": "macOS", "linux": "Linux"}[detected]
        layout.addWidget(_lbl(f"Auto-detected: {det_name}", 8, color=C.ACC2,
                               align=Qt.AlignmentFlag.AlignLeft))

        os_row = QHBoxLayout(); os_row.setSpacing(6)
        self._os_btns: dict[str, QPushButton] = {}
        for key, label in [("windows","⊞  Windows"),("mac","  macOS"),("linux","🐧  Linux")]:
            btn = QPushButton(label)
            btn.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
            btn.setFixedHeight(32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self._sel(k))
            os_row.addWidget(btn)
            self._os_btns[key] = btn
        layout.addLayout(os_row)
        self._sel(detected)
        layout.addSpacing(12)

        init_btn = QPushButton("▸  INITIALISE SYSTEMS")
        init_btn.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
        init_btn.setFixedHeight(36)
        init_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        init_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C.PRI};
                border: 1px solid {C.PRI_DIM}; border-radius: 3px;
            }}
            QPushButton:hover {{
                background: {C.PRI_GHO}; border: 1px solid {C.PRI};
            }}
        """)
        init_btn.clicked.connect(self._submit)
        layout.addWidget(init_btn)

    def _sel(self, key: str):
        self._sel_os = key
        pal = {"windows":(C.PRI,"#001a22"),"mac":(C.ACC2,"#1a1400"),"linux":(C.GREEN,"#001a0d")}
        for k, btn in self._os_btns.items():
            if k == key:
                fg, bg = pal[k]
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {fg}; color: {bg};
                        border: none; border-radius: 3px; font-weight: bold;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: #000d12; color: {C.TEXT_DIM};
                        border: 1px solid {C.BORDER}; border-radius: 3px;
                    }}
                    QPushButton:hover {{ color: {C.TEXT}; border: 1px solid {C.BORDER_B}; }}
                """)

    def _submit(self):
        key = self._key_input.text().strip()
        if not key:
            self._key_input.setStyleSheet(
                self._key_input.styleSheet() +
                f" QLineEdit {{ border: 1px solid {C.RED}; }}"
            )
            return
        self.done.emit(key, self._sel_os)


class HueWheel(QWidget):
    """
    Dairesel renk seçici. Kullanıcı tutamacı (küçük beyaz daire) çarkın
    çevresinde sürükleyerek TÜM renk tonları arasından seçim yapar.
    Merkezdeki dolu daire seçilen rengin canlı önizlemesidir.
    """

    hue_picked    = pyqtSignal(str)   # sürükleme sırasında (canlı)
    hue_committed = pyqtSignal(str)   # tutamaç bırakıldığında

    _RING = 16   # halka kalınlığı (px)

    def __init__(self, initial_hex: str = DEFAULT_UI_COLOR, parent=None):
        super().__init__(parent)
        self.setFixedSize(148, 148)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hue  = 0.53
        self._drag = False
        self.set_color(initial_hex)

    # ── API ──────────────────────────────────────────────────────────────────
    def color(self) -> str:
        return QColor.fromHsvF(self._hue, 1.0, 1.0).name()

    def set_color(self, hex_str: str):
        c = QColor((hex_str or "").strip())
        if c.isValid() and c.hsvHueF() >= 0:
            self._hue = c.hsvHueF()
            self.update()

    # ── geometri yardımcıları ────────────────────────────────────────────────
    def _ring_rect(self) -> QRectF:
        m = self._RING / 2 + 3
        return QRectF(self.rect()).adjusted(m, m, -m, -m)

    def _hue_from_pos(self, pos: QPointF) -> float:
        c  = QRectF(self.rect()).center()
        dx = pos.x() - c.x()
        dy = c.y() - pos.y()          # ekran y'si aşağı — matematiksel eksene çevir
        ang = math.atan2(dy, dx)      # [-π, π], saat yönünün tersi
        return (ang / (2 * math.pi)) % 1.0

    # ── çizim ────────────────────────────────────────────────────────────────
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect   = self._ring_rect()
        center = rect.center()

        grad = QConicalGradient(center, 0)
        for i in range(0, 361, 20):
            grad.setColorAt(i / 360.0, QColor.fromHsvF((i % 360) / 360.0, 1.0, 1.0))
        p.setPen(QPen(QBrush(grad), self._RING))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(rect)

        # merkez önizleme dairesi
        preview = QColor.fromHsvF(self._hue, 1.0, 1.0)
        inner   = rect.adjusted(30, 30, -30, -30)
        p.setPen(QPen(qcol(C.BORDER_B), 1))
        p.setBrush(QBrush(preview))
        p.drawEllipse(inner)

        # sürüklenen tutamaç
        r   = rect.width() / 2
        ang = self._hue * 2 * math.pi
        hx  = center.x() + r * math.cos(ang)
        hy  = center.y() - r * math.sin(ang)
        p.setPen(QPen(QColor("#00060a"), 2))
        p.setBrush(QBrush(QColor("#ffffff")))
        p.drawEllipse(QPointF(hx, hy), 7.5, 7.5)

    # ── fare ─────────────────────────────────────────────────────────────────
    def mousePressEvent(self, e):
        self._drag = True
        self._hue  = self._hue_from_pos(e.position())
        self.update()
        self.hue_picked.emit(self.color())

    def mouseMoveEvent(self, e):
        if self._drag:
            self._hue = self._hue_from_pos(e.position())
            self.update()
            self.hue_picked.emit(self.color())

    def mouseReleaseEvent(self, e):
        if self._drag:
            self._drag = False
            self.hue_committed.emit(self.color())


class CustomizeOverlay(QWidget):
    """Floating overlay — change assistant name, user name and UI colour."""

    saved = pyqtSignal(str, str, str)   # assistant_name, user_name, ui_color
    _OW, _OH = 400, 500

    def __init__(self, assistant_name="JARVIS", user_name="",
                 ui_color=DEFAULT_UI_COLOR, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            CustomizeOverlay {{
                background: rgba(0, 6, 10, 245);
                border: 1px solid {C.BORDER_B};
                border-radius: 6px;
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 18, 24, 18)
        lay.setSpacing(8)

        def _lbl(txt, fs=9, bold=False, color=C.PRI, align=Qt.AlignmentFlag.AlignCenter):
            w = QLabel(txt); w.setAlignment(align)
            w.setFont(QFont("Courier New", fs,
                            QFont.Weight.Bold if bold else QFont.Weight.Normal))
            w.setStyleSheet(f"color: {color}; background: transparent;")
            return w

        _fs = (f"QLineEdit {{ background: #000d12; color: {C.TEXT}; "
               f"border: 1px solid {C.BORDER}; border-radius: 3px; padding: 4px 8px; }}"
               f"QLineEdit:focus {{ border: 1px solid {C.PRI}; }}")

        lay.addWidget(_lbl("⚙  CUSTOMISE ASSISTANT", 12, True))
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {C.BORDER}; margin: 2px 0;")
        lay.addWidget(sep)

        lay.addWidget(_lbl("ASSISTANT NAME", 8, color=C.TEXT_DIM,
                            align=Qt.AlignmentFlag.AlignLeft))
        self._name_input = QLineEdit(assistant_name)
        self._name_input.setFont(QFont("Courier New", 10))
        self._name_input.setFixedHeight(32)
        self._name_input.setStyleSheet(_fs)
        lay.addWidget(self._name_input)

        lay.addSpacing(4)
        lay.addWidget(_lbl("YOUR NAME  (leave blank for default sir / efendim)", 8,
                            color=C.TEXT_DIM, align=Qt.AlignmentFlag.AlignLeft))
        self._user_input = QLineEdit(user_name)
        self._user_input.setPlaceholderText("e.g.  Tony   (leave blank for auto)")
        self._user_input.setFont(QFont("Courier New", 10))
        self._user_input.setFixedHeight(32)
        self._user_input.setStyleSheet(_fs)
        lay.addWidget(self._user_input)

        # ── UI colour — renk çarkı ───────────────────────────────────────────
        lay.addSpacing(4)
        clr_hdr = QHBoxLayout()
        clr_hdr.addWidget(_lbl("UI COLOUR  —  drag the handle", 8,
                               color=C.TEXT_DIM, align=Qt.AlignmentFlag.AlignLeft))
        clr_hdr.addStretch()
        df_btn = QPushButton("DEFAULT")
        df_btn.setFixedSize(64, 20)
        df_btn.setFont(QFont("Courier New", 7, QFont.Weight.Bold))
        df_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        df_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C.TEXT_MED};
                border: 1px solid {C.BORDER}; border-radius: 3px;
            }}
            QPushButton:hover {{ color: {C.TEXT}; border-color: {C.BORDER_B}; }}
        """)
        df_btn.clicked.connect(lambda: self._set_color(DEFAULT_UI_COLOR))
        clr_hdr.addWidget(df_btn)
        lay.addLayout(clr_hdr)

        self._initial_color = (ui_color or DEFAULT_UI_COLOR).strip().lower()
        self._sel_color     = self._initial_color
        self.on_preview     = None   # callable(hex) — canlı önizleme; MainWindow bağlar

        self._wheel = HueWheel(self._sel_color)
        wheel_row = QHBoxLayout()
        wheel_row.addStretch(); wheel_row.addWidget(self._wheel); wheel_row.addStretch()
        lay.addLayout(wheel_row)
        self._wheel.hue_picked.connect(self._on_wheel_pick)
        self._wheel.hue_committed.connect(self._on_wheel_commit)

        self._hex_input = QLineEdit(self._sel_color)
        self._hex_input.setPlaceholderText("#00d4ff   (custom hex colour)")
        self._hex_input.setFont(QFont("Courier New", 10))
        self._hex_input.setFixedHeight(28)
        self._hex_input.setStyleSheet(_fs)
        self._hex_input.textEdited.connect(self._on_hex_edited)
        lay.addWidget(self._hex_input)

        lay.addSpacing(6)
        btn_row = QHBoxLayout(); btn_row.setSpacing(8)

        save_btn = QPushButton("▸  APPLY CHANGES")
        save_btn.setFixedHeight(34)
        save_btn.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C.PRI};
                border: 1px solid {C.PRI_DIM}; border-radius: 3px;
            }}
            QPushButton:hover {{ background: {C.PRI_GHO}; border: 1px solid {C.PRI}; }}
        """)
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        cancel_btn = QPushButton("CANCEL")
        cancel_btn.setFixedHeight(34)
        cancel_btn.setFont(QFont("Courier New", 9))
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C.TEXT_MED};
                border: 1px solid {C.BORDER}; border-radius: 3px;
            }}
            QPushButton:hover {{ color: {C.TEXT}; border-color: {C.BORDER_B}; }}
        """)
        cancel_btn.clicked.connect(self._cancel)
        btn_row.addWidget(cancel_btn)
        lay.addLayout(btn_row)

    # ── renk akışı ───────────────────────────────────────────────────────────
    def _set_color(self, hx: str, update_wheel: bool = True, preview: bool = True):
        """Seçili rengi günceller; hex kutusu + çark senkron kalır, tema canlı önizlenir."""
        self._sel_color = hx.strip().lower()
        self._hex_input.blockSignals(True)
        self._hex_input.setText(self._sel_color)
        self._hex_input.blockSignals(False)
        if update_wheel:
            self._wheel.set_color(self._sel_color)
        if preview and self.on_preview:
            self.on_preview(self._sel_color)

    def _on_wheel_pick(self, hx: str):
        # Sürükleme sırasında: hex kutusunu güncelle, temayı henüz uygulama
        self._sel_color = hx
        self._hex_input.blockSignals(True)
        self._hex_input.setText(hx)
        self._hex_input.blockSignals(False)

    def _on_wheel_commit(self, hx: str):
        # Tutamaç bırakıldı → tüm arayüzü canlı önizle
        self._set_color(hx, update_wheel=False)

    def _on_hex_edited(self, text: str):
        t = text.strip().lower()
        if t.startswith("#") and len(t) == 7:
            try:
                int(t[1:], 16)
            except ValueError:
                return
            self._set_color(t, update_wheel=True, preview=True)

    def _cancel(self):
        # Önizleme uygulandıysa açılıştaki renge geri dön
        if self.on_preview and self._sel_color != self._initial_color:
            self.on_preview(self._initial_color)
        self.hide()

    def _save(self):
        name = self._name_input.text().strip() or "JARVIS"
        user = self._user_input.text().strip()
        self.saved.emit(name, user, self._sel_color or DEFAULT_UI_COLOR)
        self.hide()


class ClipboardPanel(QWidget):
    """Floating panel shown when text is copied — offers quick Jarvis actions."""

    action_requested = pyqtSignal(str)
    _W, _H = 326, 112

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            ClipboardPanel {{
                background: rgba(0, 8, 14, 248);
                border: 1px solid {C.BORDER_B};
                border-radius: 6px;
            }}
        """)
        self.setFixedWidth(self._W)
        self._clip_text = ""

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 6, 8, 7)
        lay.setSpacing(4)

        hdr = QHBoxLayout(); hdr.setSpacing(4)
        icon_lbl = QLabel("◈  CLIPBOARD DETECTED")
        icon_lbl.setFont(QFont("Courier New", 7, QFont.Weight.Bold))
        icon_lbl.setStyleSheet(f"color: {C.ACC2}; background: transparent;")
        hdr.addWidget(icon_lbl); hdr.addStretch()
        x_btn = QPushButton("✕")
        x_btn.setFixedSize(16, 16)
        x_btn.setFont(QFont("Courier New", 8))
        x_btn.setStyleSheet(f"color: {C.TEXT_DIM}; background: transparent; border: none;")
        x_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        x_btn.clicked.connect(self.hide)
        hdr.addWidget(x_btn)
        lay.addLayout(hdr)

        self._preview = QLabel()
        self._preview.setFont(QFont("Courier New", 8))
        self._preview.setStyleSheet(f"""
            color: {C.TEXT}; background: {C.PANEL2};
            border: 1px solid {C.BORDER}; border-radius: 3px; padding: 4px 6px;
        """)
        self._preview.setWordWrap(False)
        self._preview.setFixedHeight(28)
        lay.addWidget(self._preview)

        btn_row = QHBoxLayout(); btn_row.setSpacing(4)
        _bs = (f"QPushButton {{ background: {C.PANEL2}; color: {C.TEXT_MED}; "
               f"border: 1px solid {C.BORDER}; border-radius: 2px; }}"
               f"QPushButton:hover {{ color: {C.PRI}; border-color: {C.BORDER_B}; }}")
        for label, cmd_fmt in [
            ("TRANSLATE", "Translate this text to English: {text}"),
            ("SUMMARISE", "Summarise this: {text}"),
            ("EXPLAIN",   "Explain this: {text}"),
            ("FIX",       "Fix grammar and spelling: {text}"),
        ]:
            b = QPushButton(label)
            b.setFixedHeight(22)
            b.setFont(QFont("Courier New", 7, QFont.Weight.Bold))
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(_bs)
            b.clicked.connect(lambda _, c=cmd_fmt: self._trigger(c))
            btn_row.addWidget(b)
        lay.addLayout(btn_row)

        self._dismiss_timer = QTimer(self)
        self._dismiss_timer.setSingleShot(True)
        self._dismiss_timer.timeout.connect(self.hide)
        self.hide()

    def _trigger(self, cmd_fmt: str):
        if self._clip_text:
            self.action_requested.emit(cmd_fmt.format(text=self._clip_text[:800]))
        self.hide()

    def show_clipboard(self, text: str):
        self._clip_text = text
        preview = text[:58].replace('\n', ' ')
        if len(text) > 58:
            preview += "…"
        self._preview.setText(f'"{preview}"')
        self.show(); self.raise_()
        self._dismiss_timer.start(8000)


class RemoteKeyOverlay(QWidget):
    """Floating overlay — QR code for instant phone pairing + manual key fallback."""

    closed = pyqtSignal()

    _OW, _OH = 400, 465

    def __init__(self, url: str, key: str, auto_login_url: str = "",
                 manual_url: str = "", expiry_secs: int = 600, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            RemoteKeyOverlay {{
                background: rgba(0, 4, 12, 0.95);
                border: 1px solid {C.BORDER_B};
                border-radius: 14px;
            }}
        """)
        self._expiry          = time.time() + expiry_secs
        self._on_new_key      = None
        self._auto_login_url  = auto_login_url
        self._manual_url      = manual_url or url

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 16, 24, 16)
        lay.setSpacing(5)

        def _lbl(txt, fs=9, bold=False, color=C.PRI,
                 align=Qt.AlignmentFlag.AlignCenter):
            w = QLabel(txt)
            w.setAlignment(align)
            w.setFont(QFont("Courier New", fs,
                            QFont.Weight.Bold if bold else QFont.Weight.Normal))
            w.setStyleSheet(f"color: {color}; background: transparent;")
            w.setWordWrap(True)
            return w

        lay.addWidget(_lbl("◈  REMOTE ACCESS", 12, True))
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {C.BORDER}; margin: 1px 0;")
        lay.addWidget(sep)

        # ── QR code ───────────────────────────────────────────────────────────
        self._qr_label = QLabel()
        self._qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qr_label.setFixedSize(176, 176)
        self._qr_label.setStyleSheet(
            "background: white; border-radius: 10px; padding: 4px;"
        )
        qr_row = QHBoxLayout()
        qr_row.addStretch()
        qr_row.addWidget(self._qr_label)
        qr_row.addStretch()
        lay.addLayout(qr_row)

        self._update_qr(auto_login_url)

        lay.addWidget(_lbl("Scan with phone camera to connect instantly", 8, color=C.TEXT_DIM))

        sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"color: {C.BORDER}; margin: 1px 0;")
        lay.addWidget(sep2)

        lay.addWidget(_lbl("Or enter manually:", 7, color=C.TEXT_DIM,
                           align=Qt.AlignmentFlag.AlignLeft))

        self._url_lbl = QLabel(self._manual_url)
        self._url_lbl.setFont(QFont("Courier New", 8))
        self._url_lbl.setStyleSheet(f"color: {C.PRI_DIM}; background: transparent;")
        self._url_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._url_lbl.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        lay.addWidget(self._url_lbl)

        self._key_lbl = QLabel(key)
        self._key_lbl.setFont(QFont("Courier New", 28, QFont.Weight.Bold))
        self._key_lbl.setStyleSheet(f"""
            color: {C.ACC};
            background: {C.PANEL2};
            border: 1px solid {C.BORDER_B};
            border-radius: 8px;
            padding: 6px 4px;
            letter-spacing: 10px;
        """)
        self._key_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self._key_lbl)

        self._timer_lbl = QLabel()
        self._timer_lbl.setFont(QFont("Courier New", 8))
        self._timer_lbl.setStyleSheet(f"color: {C.TEXT_MED}; background: transparent;")
        self._timer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self._timer_lbl)

        btn_row = QHBoxLayout(); btn_row.setSpacing(8)
        new_btn = QPushButton("NEW KEY")
        new_btn.setFixedHeight(32)
        new_btn.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C.PANEL}; color: {C.PRI};
                border: 1px solid {C.PRI_DIM}; border-radius: 5px;
            }}
            QPushButton:hover {{ background: {C.PRI_GHO}; border: 1px solid {C.PRI}; }}
        """)
        new_btn.clicked.connect(self._refresh_key)
        btn_row.addWidget(new_btn)

        close_btn = QPushButton("DISMISS")
        close_btn.setFixedHeight(32)
        close_btn.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C.TEXT_MED};
                border: 1px solid {C.BORDER}; border-radius: 5px;
            }}
            QPushButton:hover {{ color: {C.TEXT}; border: 1px solid {C.BORDER_B}; }}
        """)
        close_btn.clicked.connect(self._do_close)
        btn_row.addWidget(close_btn)
        lay.addLayout(btn_row)

        self._ctimer = QTimer(self)
        self._ctimer.timeout.connect(self._tick)
        self._ctimer.start(1000)
        self._tick()

    def set_new_key_callback(self, fn) -> None:
        self._on_new_key = fn

    def _update_qr(self, url: str) -> None:
        if not url:
            self._qr_label.setText("—")
            return
        try:
            import qrcode as _qrmod
            from io import BytesIO
            qr = _qrmod.QRCode(
                box_size=5, border=2,
                error_correction=_qrmod.constants.ERROR_CORRECT_M,
            )
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = BytesIO()
            img.save(buf, format="PNG")
            px = QPixmap()
            px.loadFromData(buf.getvalue())
            self._qr_label.setPixmap(
                px.scaled(170, 170,
                          Qt.AspectRatioMode.KeepAspectRatio,
                          Qt.TransformationMode.SmoothTransformation)
            )
        except ImportError:
            self._qr_label.setText("pip install\nqrcode[pil]")
            self._qr_label.setFont(QFont("Courier New", 8))
            self._qr_label.setStyleSheet(
                "color: #888; background: white; border-radius: 10px; padding: 4px;"
            )
        except Exception:
            self._qr_label.setText(url[:28])
            self._qr_label.setFont(QFont("Courier New", 7))
            self._qr_label.setStyleSheet(
                f"color: {C.PRI}; background: white; border-radius: 10px; padding: 4px;"
            )

    def _tick(self):
        remaining = max(0, int(self._expiry - time.time()))
        m, s = divmod(remaining, 60)
        self._timer_lbl.setText(f"Key expires in  {m:02d}:{s:02d}")
        if remaining == 0:
            self._do_close()

    def mark_connected(self) -> None:
        """Call from any thread when a phone successfully connects."""
        self._ctimer.stop()
        self._key_lbl.setText("CONNECTED")
        self._key_lbl.setStyleSheet(f"""
            color: {C.GREEN};
            background: rgba(34,197,94,0.08);
            border: 2px solid rgba(34,197,94,0.4);
            border-radius: 8px;
            padding: 6px 4px;
            letter-spacing: 4px;
        """)
        self._qr_label.setText("✓")
        self._qr_label.setFont(QFont("Courier New", 54, QFont.Weight.Bold))
        self._qr_label.setStyleSheet(
            "color: #00ff88; background: #001a0d; border-radius: 10px;"
        )
        self._timer_lbl.setText("Phone connected — JARVIS ready")
        self._timer_lbl.setStyleSheet(f"color: {C.GREEN}; background: transparent;")

    def _refresh_key(self):
        if self._on_new_key:
            result = self._on_new_key()
            if result:
                url    = result[0]
                key    = result[1]
                auto   = result[2] if len(result) >= 3 else ""
                manual = result[3] if len(result) >= 4 else url
                self._manual_url     = manual or url
                self._url_lbl.setText(self._manual_url)
                self._key_lbl.setText(key)
                self._auto_login_url = auto
                self._update_qr(auto or url)
                self._expiry = time.time() + 600
                self._key_lbl.setStyleSheet(f"""
                    color: {C.ACC};
                    background: {C.PANEL2};
                    border: 1px solid {C.BORDER_B};
                    border-radius: 8px;
                    padding: 6px 4px;
                    letter-spacing: 10px;
                """)
                self._timer_lbl.setStyleSheet(
                    f"color: {C.TEXT_MED}; background: transparent;"
                )
                self._ctimer.start(1000)
                self._tick()

    def _do_close(self):
        self._ctimer.stop()
        self.hide()
        self.closed.emit()


class MainWindow(QMainWindow):
    _log_sig        = pyqtSignal(str)
    _state_sig      = pyqtSignal(str)
    _content_sig    = pyqtSignal(str, str)   # (title, text) — thread-safe content display
    _reconfig_sig   = pyqtSignal()           # trigger setup overlay from any thread
    _camera_sig     = pyqtSignal(bytes)      # show camera frame preview (small overlay)
    _cam_stream_sig = pyqtSignal(bool)       # True=start live stream, False=stop
    _cam_frame_sig  = pyqtSignal(bytes)      # live camera frame → HUD area
    _clipboard_sig  = pyqtSignal(str)        # clipboard text changed (thread-safe)

    def __init__(self, face_path: str):
        super().__init__()
        self._face_path = face_path

        # Load customization from config
        _cfg = _read_full_config()
        self._assistant_name: str = (_cfg.get("assistant_name") or "JARVIS").strip()
        _display = self._assistant_name.upper()

        # Kayıtlı UI rengini panel/stylesheet'ler kurulmadan ÖNCE uygula
        _ui_color = (_cfg.get("ui_color") or "").strip()
        if _ui_color and _ui_color.lower() != DEFAULT_UI_COLOR:
            apply_ui_accent(_ui_color)

        self.setWindowTitle(f"{_display} — MARK XLIX")
        self.setMinimumSize(_MIN_W, _MIN_H)
        self.resize(_DEFAULT_W, _DEFAULT_H)

        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width()  - _DEFAULT_W) // 2,
            (screen.height() - _DEFAULT_H) // 2,
        )

        self.on_text_command   = None
        self.on_remote_clicked = None   # callable: () -> (url, key) | None
        self.on_interrupt      = None   # callable: () -> None — stop JARVIS mid-speech
        self._muted            = False
        self._current_file: str | None = None
        self._remote_overlay: RemoteKeyOverlay | None = None
        self._customize_overlay: CustomizeOverlay | None = None

        central = QWidget()
        central.setStyleSheet(f"background: {C.BG};")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_header())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self._left_panel = self._build_left_panel()
        body.addWidget(self._left_panel, stretch=0)

        # Center column: HUD + resizable content panel via QSplitter
        self.hud = HudCanvas(face_path, _display)
        self.hud.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._content_panel = self._build_content_panel()

        # Live camera container — replaces HUD when camera stream is active
        _cam_cont = QWidget()
        _cam_cont.setStyleSheet("background: #000308;")
        _cam_v = QVBoxLayout(_cam_cont)
        _cam_v.setContentsMargins(0, 0, 0, 0)
        _cam_v.setSpacing(0)
        _cam_hdr = QHBoxLayout()
        _cam_hdr.setContentsMargins(8, 5, 8, 5)
        _cam_title = QLabel("◈  CAMERA FEED")
        _cam_title.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        _cam_title.setStyleSheet(f"color: {C.PRI}; background: transparent;")
        _cam_hdr.addWidget(_cam_title)
        _cam_hdr.addStretch()
        _cam_x = QPushButton("✕  CLOSE")
        _cam_x.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        _cam_x.setCursor(Qt.CursorShape.PointingHandCursor)
        _cam_x.setStyleSheet(f"""
            QPushButton {{
                color: {C.TEXT_DIM}; background: transparent;
                border: none; padding: 2px 6px;
            }}
            QPushButton:hover {{ color: {C.PRI}; }}
        """)
        _cam_x.clicked.connect(self.stop_camera_stream)
        _cam_hdr.addWidget(_cam_x)
        _cam_v.addLayout(_cam_hdr)
        self._cam_live_lbl = QLabel()
        self._cam_live_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cam_live_lbl.setStyleSheet("background: transparent;")
        self._cam_live_lbl.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        _cam_v.addWidget(self._cam_live_lbl, stretch=1)

        # Stack: 0 = animated HUD, 1 = live camera
        self._hud_cam_stack = QStackedWidget()
        self._hud_cam_stack.addWidget(self.hud)
        self._hud_cam_stack.addWidget(_cam_cont)

        self._center_split = QSplitter(Qt.Orientation.Vertical)
        self._center_split.setStyleSheet(f"""
            QSplitter::handle {{
                background: {C.BORDER};
                height: 4px;
            }}
            QSplitter::handle:hover {{
                background: {C.PRI_DIM};
            }}
        """)
        self._center_split.addWidget(self._hud_cam_stack)
        self._center_split.addWidget(self._content_panel)
        self._center_split.setStretchFactor(0, 3)
        self._center_split.setStretchFactor(1, 1)
        self._center_split.setCollapsible(0, False)
        body.addWidget(self._center_split, stretch=5)

        self._right_panel = self._build_right_panel()
        body.addWidget(self._right_panel, stretch=0)

        root.addLayout(body, stretch=1)
        

        # Quick-access drawer (floating overlay, built after central widget layout is done)
        self._quick_drawer = self._build_quick_drawer()
        self._update_autostart_btn(self._check_autostart())
        from memory.config_manager import get_brief_enabled as _gbe
        self._update_brief_btn(_gbe())

        self._clock_tmr = QTimer(self)
        self._clock_tmr.timeout.connect(self._tick_clock)
        self._clock_tmr.start(1000)
        self._tick_clock()

        # Metrik güncelleme timer'ı
        self._metric_tmr = QTimer(self)
        self._metric_tmr.timeout.connect(self._update_metrics)
        self._metric_tmr.start(2000)
        self._update_metrics()

        self._log_sig.connect(self._log.append_log)
        self._state_sig.connect(self._apply_state)
        self._content_sig.connect(self._show_content)
        self._reconfig_sig.connect(self._show_setup)
        self._camera_sig.connect(self._show_camera_frame)
        self._cam_stream_sig.connect(self._on_cam_stream)
        self._cam_frame_sig.connect(self._on_cam_frame)
        self._clipboard_sig.connect(self._show_clipboard_panel)
        self._cam_stop = threading.Event()

        # Camera preview overlay (child of central widget, positioned in resizeEvent)
        self._cam_preview = _CameraPreview(self.centralWidget())

        # Clipboard panel (child of central widget, bottom-center)
        self._clipboard_panel = ClipboardPanel(self.centralWidget())
        self._clipboard_panel.action_requested.connect(self._on_clipboard_action)
        QApplication.clipboard().dataChanged.connect(self._on_clipboard_changed)

        self._overlay: SetupOverlay | None = None
        self._ready = self._check_config()
        if not self._ready:
            self._show_setup()

        sc_mute = QShortcut(QKeySequence("F4"), self)
        sc_mute.activated.connect(self._toggle_mute)

        sc_mem = QShortcut(QKeySequence("F5"), self)
        sc_mem.activated.connect(self._load_memory_vault_view)

        sc_full = QShortcut(QKeySequence("F11"), self)
        sc_full.activated.connect(self._toggle_fullscreen)

        sc_intr = QShortcut(QKeySequence("Escape"), self)
        sc_intr.activated.connect(self._do_interrupt)

        self._glitter = GlitterOverlay(self, count=80)
        self._glitter.setGeometry(0, 0, self.width(), self.height())

    def _show_camera_frame(self, img_bytes: bytes):
        """Slot — display camera preview overlay (main thread)."""
        self._cam_preview.show_frame(img_bytes)
        cw = self.centralWidget()
        pw = _CameraPreview._W
        ph = self._cam_preview.height()
        self._cam_preview.setGeometry(
            cw.width() - _RIGHT_W - pw - 12,
            cw.height() - ph - 28,
            pw, ph,
        )

    def _get_or_setup_memory_dir(self) -> Path:
        """Legge la cartella memoria dal config. Se non esiste, la fa scegliere all'utente e migra i vecchi file."""
        from pathlib import Path
        import json
        import shutil
        from PyQt6.QtWidgets import QFileDialog

        config_path = Path("./config/settings.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config = {}
        if config_path.exists():
            try:
                config = json.loads(config_path.read_text(encoding="utf-8"))
            except Exception:
                config = {}

        # Determina la cartella scelta
        if "memory_folder" in config and config["memory_folder"]:
            final_path = Path(config["memory_folder"])
        else:
            chosen_dir = QFileDialog.getExistingDirectory(
                self, 
                "INSTALLAZIONE JARVIS — Seleziona la cartella per la Memoria (.md)",
                str(Path.home())
            )

            if not chosen_dir:
                chosen_dir = "./app_memory"

            final_path = Path(chosen_dir)
            config["memory_folder"] = str(final_path.resolve())
            config_path.write_text(json.dumps(config, indent=4), encoding="utf-8")

        final_path.mkdir(parents=True, exist_ok=True)

        # Migrazione automatica da ./app_memory verso il nuovo percorso (se diverso)
        default_old_path = Path("./app_memory").resolve()
        if default_old_path.exists() and default_old_path != final_path.resolve():
            for item in default_old_path.glob("*.md"):
                dest_file = final_path / item.name
                if not dest_file.exists():
                    try:
                        shutil.copy2(item, dest_file)
                        if hasattr(self, "_log"):
                            self._log.append_log(f"SYS: Migrata nota '{item.name}' nella nuova cartella.")
                    except Exception as e:
                        if hasattr(self, "_log"):
                            self._log.append_log(f"ERR: Impossibile migrare {item.name}: {e}")

        if hasattr(self, "_log"):
            self._log.append_log(f"SYS: Memoria attiva su: {final_path.resolve()}")
        return final_path

    def _open_obsidian_vault_window(self):
        """Apre la vista Vault avanzata stile Obsidian mantenendo il riferimento attivo."""
        try:
            vault_path = self._get_or_setup_memory_dir()
            
            if not hasattr(self, "_obsidian_win") or self._obsidian_win is None:
                self._obsidian_win = ObsidianVaultWindow(vault_path, parent=None)
            
            self._obsidian_win.show()
            self._obsidian_win.raise_()
            self._obsidian_win.activateWindow()
        except Exception as e:
            if hasattr(self, "_log"):
                self._log.append_log(f"ERR: Impossibile aprire Obsidian Vault: {e}")

    # --- Live camera stream in HUD area ------------------------------------
    def _on_cam_stream(self, start: bool) -> None:
        if start:
            self._hud_cam_stack.setCurrentIndex(1)
        else:
            self._hud_cam_stack.setCurrentIndex(0)
            self._cam_live_lbl.clear()

    def _on_cam_frame(self, data: bytes) -> None:
        px = QPixmap()
        px.loadFromData(data)
        if not px.isNull():
            w, h = self._cam_live_lbl.width(), self._cam_live_lbl.height()
            if w > 1 and h > 1:
                self._cam_live_lbl.setPixmap(
                    px.scaled(w, h,
                              Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
                )

    def start_camera_stream(self) -> None:
        self._cam_stop.clear()
        self._cam_stream_sig.emit(True)
        t = threading.Thread(target=self._cam_loop, daemon=True, name="cam-stream")
        t.start()

    def _cam_loop(self) -> None:
        try:
            import cv2
            # Reuse camera index detected by screen_processor (cached in api_keys.json)
            cam_idx = 0
            try:
                import json as _j
                cfg = _j.loads((CONFIG_DIR / "api_keys.json").read_text())
                cam_idx = int(cfg.get("camera_index", 0))
            except Exception:
                pass
            try:
                backend = cv2.CAP_DSHOW if _OS == "Windows" else cv2.CAP_ANY
            except AttributeError:
                backend = 0
            cap = cv2.VideoCapture(cam_idx, backend)
            if not cap.isOpened():
                cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return
            # warm-up frames
            for _ in range(5):
                cap.read()
            while not self._cam_stop.wait(0.033) and cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 65])
                    self._cam_frame_sig.emit(buf.tobytes())
            cap.release()
        except Exception as e:
            print(f"[Camera] Stream error: {e}")
        finally:
            self._cam_stream_sig.emit(False)

    def stop_camera_stream(self) -> None:
        self._cam_stop.set()

    # ------------------------------------------------------------------
    # Icon generation — arc-reactor style, rendered with Pillow
    # ------------------------------------------------------------------
    @staticmethod
    def _build_jarvis_icon(out_path: Path) -> bool:
        """
        Render a JARVIS arc-reactor icon at 4× resolution and downsample
        for crisp results at all sizes. Saves a multi-res .ico to out_path.
        Returns True on success.
        """
        try:
            import math
            import PIL.Image
            import PIL.ImageDraw
            import PIL.ImageFilter
        except ImportError:
            return False

        CYAN   = (0, 212, 255)
        DIM    = (0, 100, 140)
        DARK   = (0, 6, 10)
        GLOW   = (0, 160, 200)
        WHITE  = (220, 240, 255)

        def _render(sz: int) -> PIL.Image.Image:
            S  = sz * 4                     # draw at 4× then downscale
            img = PIL.Image.new("RGBA", (S, S), (0, 0, 0, 0))
            d   = PIL.ImageDraw.Draw(img)
            cx = cy = S // 2

            # ── filled background circle ──────────────────────────────────
            R = S // 2 - 2
            d.ellipse([cx-R, cy-R, cx+R, cy+R], fill=(*DARK, 255))

            # ── outer border ring ─────────────────────────────────────────
            lw = max(2, S // 40)
            d.ellipse([cx-R, cy-R, cx+R, cy+R],
                      outline=(*CYAN, 220), width=lw)

            # ── mid decorative ring ───────────────────────────────────────
            R2 = int(R * 0.72)
            d.ellipse([cx-R2, cy-R2, cx+R2, cy+R2],
                      outline=(*DIM, 180), width=max(1, lw // 2))

            # ── 6 radial spokes (hex bolt) ────────────────────────────────
            R_inner = int(R * 0.30)
            R_outer = int(R * 0.62)
            spoke_w = max(1, S // 80)
            for i in range(6):
                angle = math.radians(i * 60 - 30)
                x1 = cx + int(R_inner * math.cos(angle))
                y1 = cy + int(R_inner * math.sin(angle))
                x2 = cx + int(R_outer * math.cos(angle))
                y2 = cy + int(R_outer * math.sin(angle))
                d.line([x1, y1, x2, y2], fill=(*GLOW, 200), width=spoke_w)

            # ── 6 tick marks on outer ring ────────────────────────────────
            for i in range(6):
                angle = math.radians(i * 60)
                for dr in range(lw * 2):
                    rx = (R - lw - dr)
                    d.point(
                        [cx + int(rx * math.cos(angle)),
                         cy + int(rx * math.sin(angle))],
                        fill=(*WHITE, 220),
                    )

            # ── inner glowing ring ────────────────────────────────────────
            Ri = int(R * 0.26)
            d.ellipse([cx-Ri, cy-Ri, cx+Ri, cy+Ri],
                      outline=(*CYAN, 255), width=max(2, lw))

            # ── bright glow soft blur applied before core ─────────────────
            # (draw a slightly larger cyan circle on a separate layer)
            glow_layer = PIL.Image.new("RGBA", (S, S), (0, 0, 0, 0))
            gd = PIL.ImageDraw.Draw(glow_layer)
            Rc = int(R * 0.13)
            gd.ellipse([cx-Rc*2, cy-Rc*2, cx+Rc*2, cy+Rc*2],
                       fill=(*CYAN, 110))
            glow_layer = glow_layer.filter(PIL.ImageFilter.GaussianBlur(S // 14))
            img = PIL.Image.alpha_composite(img, glow_layer)
            d   = PIL.ImageDraw.Draw(img)

            # ── core dot ──────────────────────────────────────────────────
            d.ellipse([cx-Rc, cy-Rc, cx+Rc, cy+Rc], fill=(*WHITE, 255))

            # ── downscale to target size ──────────────────────────────────
            return img.resize((sz, sz), PIL.Image.LANCZOS)

        try:
            sizes  = [256, 128, 64, 48, 32, 16]
            frames = [_render(s) for s in sizes]
            frames[0].save(
                out_path,
                format="ICO",
                append_images=frames[1:],
                sizes=[(s, s) for s in sizes],
            )
            return True
        except Exception as e:
            print(f"[Shortcut] ⚠️  Icon generation failed: {e}")
            return False

    @staticmethod
    def _create_lnk_windows(lnk: str, target: str, args: str,
                             work_dir: str, icon_loc: str) -> None:
        """
        Create a Windows .lnk shortcut WITHOUT launching PowerShell or cmd.
        Tries win32com (pywin32) first; falls back to wscript.exe + VBScript.
        wscript.exe is a GUI-mode host — it never opens a console window.
        """
        # ── Option 1: pywin32 (pure Python COM, zero subprocess) ──────────
        try:
            from win32com.client import Dispatch   # type: ignore
            sh = Dispatch("WScript.Shell")
            sc = sh.CreateShortCut(lnk)
            sc.TargetPath       = target
            sc.Arguments        = f'"{args}"'
            sc.WorkingDirectory = work_dir
            sc.Description      = "J.A.R.V.I.S AI Assistant"
            sc.IconLocation     = icon_loc
            sc.save()
            return
        except ImportError:
            pass

        # ── Option 2: wscript.exe + VBScript (always available on Windows,
        #    GUI-mode executable — never opens a console window) ────────────
        vbs = "\n".join([
            'Set ws = CreateObject("WScript.Shell")',
            f'Set sc = ws.CreateShortcut("{lnk}")',
            f'sc.TargetPath = "{target}"',
            f'sc.Arguments = Chr(34) & "{args}" & Chr(34)',
            f'sc.WorkingDirectory = "{work_dir}"',
            'sc.Description = "J.A.R.V.I.S AI Assistant"',
            f'sc.IconLocation = "{icon_loc}"',
            'sc.Save',
        ])
        import tempfile
        fd, tmp = tempfile.mkstemp(suffix=".vbs")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(vbs)
            proc = subprocess.Popen(
                ["wscript.exe", "/nologo", tmp],
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
            )
            proc.wait(timeout=10)
        finally:
            try:
                os.unlink(tmp)
            except Exception:
                pass

    @staticmethod
    def _get_desktop_dir() -> Path:
        """
        Resolve the user's REAL desktop directory instead of assuming
        ~/Desktop, which breaks when:
          • OneDrive "Known Folder Move" relocates the desktop
            (C:/Users/x/OneDrive/Desktop) — very common on Win 10/11;
          • the XDG desktop is localized on Linux (~/Masaüstü,
            ~/Schreibtisch, ~/Bureau, …).
        Falls back to ~/Desktop only as a last resort.
        """
        home = Path.home()
        _os = platform.system()

        if _os == "Windows":
            # ── 1) SHGetKnownFolderPath(FOLDERID_Desktop) — the canonical
            #       answer; follows OneDrive redirection. No dependencies. ──
            try:
                import ctypes
                from ctypes import wintypes

                class _GUID(ctypes.Structure):
                    _fields_ = [("Data1", wintypes.DWORD),
                                ("Data2", wintypes.WORD),
                                ("Data3", wintypes.WORD),
                                ("Data4", ctypes.c_ubyte * 8)]

                # FOLDERID_Desktop {B4BFCC3A-DB2C-424C-B029-7FE99A87C641}
                fid = _GUID(0xB4BFCC3A, 0xDB2C, 0x424C,
                            (ctypes.c_ubyte * 8)(0xB0, 0x29, 0x7F, 0xE9,
                                                 0x9A, 0x87, 0xC6, 0x41))
                buf = ctypes.c_wchar_p()
                if ctypes.windll.shell32.SHGetKnownFolderPath(
                        ctypes.byref(fid), 0, None, ctypes.byref(buf)) == 0:
                    p = Path(buf.value)
                    ctypes.windll.ole32.CoTaskMemFree(buf)
                    if p.is_dir():
                        return p
            except Exception:
                pass

            # ── 2) Registry: User Shell Folders (may contain %VARS%) ──────
            try:
                import winreg
                with winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        r"Software\Microsoft\Windows\CurrentVersion"
                        r"\Explorer\User Shell Folders") as key:
                    val, _t = winreg.QueryValueEx(key, "Desktop")
                p = Path(os.path.expandvars(val))
                if p.is_dir():
                    return p
            except Exception:
                pass

        elif _os == "Linux":
            # ── xdg-user-dir honours localized names (~/Masaüstü, …) ──────
            try:
                out = subprocess.run(["xdg-user-dir", "DESKTOP"],
                                     capture_output=True, text=True, timeout=5)
                p = Path(out.stdout.strip())
                if out.stdout.strip() and p != home and p.is_dir():
                    return p
            except Exception:
                pass
            try:
                cfg = home / ".config" / "user-dirs.dirs"
                for line in cfg.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line.startswith("XDG_DESKTOP_DIR"):
                        val = line.split("=", 1)[1].strip().strip('"')
                        p = Path(val.replace("$HOME", str(home)))
                        if p != home and p.is_dir():
                            return p
            except Exception:
                pass

        # macOS: ~/Desktop is always the real path (localization is
        # display-only). Everything else lands here as a last resort.
        return home / "Desktop"

    def _create_desktop_shortcut(self):
        """
        Create a desktop shortcut on Windows / macOS / Linux.
        Never opens a terminal, console, or PowerShell window on any platform.
        """
        import stat as _stat
        script  = Path(__file__).resolve().parent / "main.py"
        python  = Path(sys.executable)
        desktop = self._get_desktop_dir()

        # Arc-reactor icon (.ico — also exported as .png for Linux/macOS)
        ico_path = Path(__file__).resolve().parent / "config" / "jarvis.ico"
        if not ico_path.exists():
            self._build_jarvis_icon(ico_path)

        try:
            _os = platform.system()

            # ── Windows ───────────────────────────────────────────────────────
            if _os == "Windows":
                pythonw  = python.parent / "pythonw.exe"
                target   = str(pythonw if pythonw.exists() else python)
                lnk      = str(desktop / "J.A.R.V.I.S.lnk")
                icon_loc = str(ico_path) if ico_path.exists() else f"{target},0"
                self._create_lnk_windows(lnk, target, str(script),
                                         str(script.parent), icon_loc)

            # ── macOS — proper .app bundle (no Terminal window) ───────────────
            elif _os == "Darwin":
                app     = desktop / "J.A.R.V.I.S.app"
                mac_dir = app / "Contents" / "MacOS"
                res_dir = app / "Contents" / "Resources"
                mac_dir.mkdir(parents=True, exist_ok=True)
                res_dir.mkdir(exist_ok=True)

                # Launcher executable (bash — runs as background process,
                # macOS does NOT open Terminal for executables inside .app bundles)
                launcher = mac_dir / "JARVIS"
                launcher.write_text(
                    "#!/usr/bin/env bash\n"
                    f'cd "{script.parent}"\n'
                    f'exec "{python}" "{script}"\n'
                )
                launcher.chmod(launcher.stat().st_mode
                               | _stat.S_IEXEC | _stat.S_IXGRP | _stat.S_IXOTH)

                # Minimal Info.plist (required for .app recognition)
                (app / "Contents" / "Info.plist").write_text(
                    '<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
                    '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
                    '<plist version="1.0"><dict>\n'
                    '  <key>CFBundleExecutable</key><string>JARVIS</string>\n'
                    '  <key>CFBundleIdentifier</key>'
                    '<string>com.jarvis.assistant</string>\n'
                    '  <key>CFBundleName</key><string>J.A.R.V.I.S</string>\n'
                    '  <key>CFBundlePackageType</key><string>APPL</string>\n'
                    '  <key>CFBundleVersion</key><string>1.0</string>\n'
                    '</dict></plist>\n'
                )

                # Optional: copy icon as .icns (skip silently if Pillow is missing)
                try:
                    import PIL.Image
                    icns = res_dir / "AppIcon.icns"
                    PIL.Image.open(ico_path).save(icns, format="ICNS")
                    # Inject icon reference into plist
                    plist = app / "Contents" / "Info.plist"
                    txt = plist.read_text()
                    plist.write_text(
                        txt.replace(
                            '</dict></plist>',
                            '  <key>CFBundleIconFile</key>'
                            '<string>AppIcon</string>\n</dict></plist>\n',
                        )
                    )
                except Exception:
                    pass  # icon is optional

            # ── Linux — .desktop file (Terminal=false, no console) ────────────
            else:
                # Export .ico → .png for better desktop integration
                png_path = ico_path.with_suffix(".png")
                if not png_path.exists() and ico_path.exists():
                    try:
                        import PIL.Image
                        PIL.Image.open(ico_path).resize(
                            (256, 256), PIL.Image.LANCZOS
                        ).save(png_path, format="PNG")
                    except Exception:
                        png_path = ico_path  # fallback to .ico

                icon_line = f"Icon={png_path}\n" if png_path.exists() else ""
                desk = desktop / "J.A.R.V.I.S.desktop"
                desk.write_text(
                    "[Desktop Entry]\n"
                    "Name=J.A.R.V.I.S\n"
                    f"Exec={python} {script}\n"
                    f"Path={script.parent}\n"
                    "Type=Application\n"
                    "Terminal=false\n"
                    "Categories=Utility;\n"
                    + icon_line
                )
                desk.chmod(desk.stat().st_mode | 0o755)

            self._log.append_log("SYS: Desktop shortcut created.")
        except Exception as e:
            self._log.append_log(f"ERR: Shortcut failed — {e}")

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _open_obsidian_vault_window(self):
        """Apre la vista Vault avanzata stile Obsidian mantenendo il riferimento attivo."""
        try:
            vault_path = self._get_or_setup_memory_dir()
            
            # Mantiene un riferimento permanente per evitare che il Garbage Collector chiuda la finestra
            if not hasattr(self, "_obsidian_win") or self._obsidian_win is None:
                self._obsidian_win = ObsidianVaultWindow(vault_path, parent=None)
            
            self._obsidian_win.show()
            self._obsidian_win.raise_()
            self._obsidian_win.activateWindow()
        except Exception as e:
            if hasattr(self, "_log"):
                self._log.append_log(f"ERR: Impossibile aprire Obsidian Vault: {e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cw = self.centralWidget()

        # 1. Overlay Glitter — Copre l'intera finestra (in primo piano)
        if hasattr(self, "_glitter") and self._glitter:
            self._glitter.setGeometry(0, 0, self.width(), self.height())
            self._glitter.raise_()

        # 2. Overlay standard centrati
        if self._overlay and self._overlay.isVisible():
            ow, oh = 460, 390
            self._overlay.setGeometry(
                (cw.width()  - ow) // 2,
                (cw.height() - oh) // 2,
                ow, oh,
        )
        if self._remote_overlay and self._remote_overlay.isVisible():
            ow, oh = RemoteKeyOverlay._OW, RemoteKeyOverlay._OH
            self._remote_overlay.setGeometry(
                (cw.width()  - ow) // 2,
                (cw.height() - oh) // 2,
                ow, oh,
        )
        if self._customize_overlay and self._customize_overlay.isVisible():
            ow, oh = CustomizeOverlay._OW, CustomizeOverlay._OH
            self._customize_overlay.setGeometry(
                (cw.width()  - ow) // 2,
                (cw.height() - oh) // 2,
                ow, oh,
            )

        # Camera preview — bottom-right corner of the center/HUD area
        pw = _CameraPreview._W
        ph = self._cam_preview.height() or _CameraPreview._H
        self._cam_preview.setGeometry(
            cw.width() - _RIGHT_W - pw - 12,
            cw.height() - ph - 28,
            pw, ph,
        )

        # Clipboard panel — bottom-center
        if hasattr(self, '_clipboard_panel') and self._clipboard_panel.isVisible():
            self._position_clipboard_panel()

        # Quick drawer — reposition if open
        if hasattr(self, '_quick_drawer') and self._quick_drawer.isVisible():
            self._position_quick_drawer()

    def _update_metrics(self):
        snap = _metrics.snapshot()

        # CPU
        cpu = snap["cpu"]
        self._bar_cpu.set_value(cpu, f"{cpu:.0f}%")

        # MEM
        mem = snap["mem"]
        self._bar_mem.set_value(mem, f"{mem:.0f}%")

        # NET
        net = snap["net"]
        if net < 1.0:
            net_str = f"{net*1024:.0f}KB/s"
        else:
            net_str = f"{net:.1f}MB/s"
        net_pct = min(100, net * 10)  # 10 MB/s = %100
        self._bar_net.set_value(net_pct, net_str)

        # GPU
        gpu = snap["gpu"]
        if gpu >= 0:
            self._bar_gpu.set_value(gpu, f"{gpu:.0f}%")
        else:
            self._bar_gpu.set_value(0, "N/A")

        # TMP
        tmp = snap["tmp"]
        if tmp >= 0:
            tmp_pct = min(100, (tmp / 100) * 100)
            self._bar_tmp.set_value(tmp_pct, f"{tmp:.0f}°C")
        else:
            self._bar_tmp.set_value(0, "N/A")

        try:
            boot_t  = psutil.boot_time()
            elapsed = time.time() - boot_t
            h = int(elapsed // 3600)
            m = int((elapsed % 3600) // 60)
            self._uptime_lbl.setText(f"UP  {h:02d}:{m:02d}")
        except Exception:
            self._uptime_lbl.setText("UP  --:--")

        try:
            proc_count = len(psutil.pids())
            self._proc_lbl.setText(f"PROC  {proc_count}")
        except Exception:
            self._proc_lbl.setText("PROC  --")


    def _build_header(self) -> QWidget:
        w = QWidget()
        w.setFixedHeight(50)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(12, 4, 12, 4)

        # Gestione sicura di _drawer_btn
        if not hasattr(self, "_drawer_btn") or self._drawer_btn is None:
            self._drawer_btn = QPushButton("⚙")
            self._drawer_btn.setFixedSize(32, 32)
            self._drawer_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._drawer_btn.setCheckable(True)
            if hasattr(self, "_toggle_drawer"):
                self._drawer_btn.clicked.connect(self._toggle_drawer)

        self._drawer_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lay.addWidget(self._drawer_btn)
        lay.addStretch()

        # Titolo centrale Cyberpunk
        mid = QVBoxLayout()
        mid.setSpacing(1)
        _disp = self._assistant_name.upper()

        self._title_lbl = QLabel(_disp)
        self._title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_lbl.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        mid.addWidget(self._title_lbl)

        _sub_text = ("Just A Rather Very Intelligent System"
                     if _disp in ("JARVIS", "J.A.R.V.I.S")
                     else "Personal AI Assistant")
        self._sub_lbl = QLabel(_sub_text)
        self._sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sub_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Normal))
        mid.addWidget(self._sub_lbl)

        lay.addLayout(mid)
        lay.addStretch()

        # Orologio e data in alto a destra
        right_col = QVBoxLayout()
        right_col.setSpacing(1)

        self._clock_lbl = QLabel("00:00:00")
        self._clock_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self._clock_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_col.addWidget(self._clock_lbl)

        self._date_lbl = QLabel("")
        self._date_lbl.setFont(QFont("Segoe UI", 8))
        self._date_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_col.addWidget(self._date_lbl)

        lay.addLayout(right_col)

        # Applica immediatamente la palette di colori iniziale agli elementi dell'header
        self._update_header_styles()
        return w

    def _update_header_styles(self):
        """Aggiorna lo stile grafico degli elementi dell'header in base alle variabili di tema attive."""
        # Se non sono ancora definite le variabili di tema, imposta i valori di default (Cyan Cyberpunk)
        accent   = getattr(self, "c_accent", "#00f0ff")
        bg_btn   = getattr(self, "c_bg_btn", "#131722")
        bg_hover = getattr(self, "c_bg_hover", "#1c2333")
        border   = getattr(self, "c_border", "#1f293d")
        subtext  = getattr(self, "c_subtext", "#5a657b")

        if hasattr(self, "_drawer_btn") and self._drawer_btn:
            self._drawer_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {bg_btn}; color: {accent};
                    border: 1px solid {border}; border-radius: 4px;
                }}
                QPushButton:hover {{
                    background: {bg_hover}; border: 1px solid {accent};
                }}
                QPushButton:checked {{
                    color: {accent}; border-color: {accent}; background: {bg_hover};
                }}
            """)

        if hasattr(self, "_title_lbl"):
            self._title_lbl.setStyleSheet(f"color: {accent}; background: transparent; letter-spacing: 3px;")
        if hasattr(self, "_sub_lbl"):
            self._sub_lbl.setStyleSheet(f"color: {subtext}; background: transparent; letter-spacing: 1px;")
        if hasattr(self, "_clock_lbl"):
            self._clock_lbl.setStyleSheet(f"color: {accent}; background: transparent; letter-spacing: 1px;")
        if hasattr(self, "_date_lbl"):
            self._date_lbl.setStyleSheet(f"color: {subtext}; background: transparent;")
    
    def _tick_clock(self):
        self._clock_lbl.setText(time.strftime("%H:%M:%S"))
        self._date_lbl.setText(time.strftime("%a %d %b %Y"))

    def _build_left_panel(self) -> QWidget:
        self._left_panel_w = QWidget()
        self._left_panel_w.setFixedWidth(_LEFT_W)

        lay = QVBoxLayout(self._left_panel_w)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(6)

        # Header Tattico
        self._sys_hdr_lbl = QLabel("▶ SYS MONITOR")
        self._sys_hdr_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lay.addWidget(self._sys_hdr_lbl)
        lay.addSpacing(2)

        # Metric Bars (CPU, MEM, NET, GPU, TMP)
        # Se la classe MetricBar accetta aggiornamenti dinamici, la inizializziamo normalmente
        self._bar_cpu = MetricBar("CPU", getattr(C, "PRI", "#00f0ff"))
        self._bar_mem = MetricBar("MEM", getattr(C, "ACC2", "#00ff88"))
        self._bar_net = MetricBar("NET", getattr(C, "GREEN", "#00ff88"))
        self._bar_gpu = MetricBar("GPU", getattr(C, "ACC", "#7000ff"))
        self._bar_tmp = MetricBar("TMP", "#ff3355")

        for bar in [self._bar_cpu, self._bar_mem, self._bar_net, self._bar_gpu, self._bar_tmp]:
            lay.addWidget(bar)

        lay.addSpacing(4)

        # Box Uptime & Processi
        self._info_panel = QWidget()
        ip_lay = QVBoxLayout(self._info_panel)
        ip_lay.setContentsMargins(8, 6, 8, 6)
        ip_lay.setSpacing(3)

        self._uptime_lbl = QLabel("UP  --:--")
        self._uptime_lbl.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        ip_lay.addWidget(self._uptime_lbl)

        self._proc_lbl = QLabel("PROC  --")
        self._proc_lbl.setFont(QFont("Consolas", 8))
        ip_lay.addWidget(self._proc_lbl)

        os_name = {"Windows": "WIN", "Darwin": "macOS", "Linux": "LINUX"}.get(_OS, _OS.upper())
        self._os_lbl = QLabel(f"OS  {os_name}")
        self._os_lbl.setFont(QFont("Consolas", 8))
        ip_lay.addWidget(self._os_lbl)

        lay.addWidget(self._info_panel)
        lay.addStretch()

        # Status Badges In basso (Pill)
        self._badge_labels = []
        badges_data = [
            ("● AI CORE ACTIVE", "#00ff88", "#0a1c18", "#124a3e"),
            ("◈ SEC CLEARED",    "#00f0ff", "#091b24", "#0f3c52"),
            ("◇ PROTOCOL XLIX",  "#7000ff", "#150a24", "#321252")
        ]
        for txt, fg, bg, bd in badges_data:
            lbl = QLabel(txt)
            lbl.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setProperty("default_style", (fg, bg, bd)) # Salva i colori base
            lay.addWidget(lbl)
            self._badge_labels.append(lbl)

        # Applica subito lo stile corrente
        self._update_left_panel_styles()
        return self._left_panel_w

    def _update_left_panel_styles(self):
        """Aggiorna lo stile del pannello laterale sinistro in base al tema attivo."""
        bg_main  = getattr(self, "c_bg_main", "#0b0e14")
        bg_card  = getattr(self, "c_bg_card", "#131722")
        border   = getattr(self, "c_border", "#1f293d")
        accent   = getattr(self, "c_accent", "#00f0ff")
        subtext  = getattr(self, "c_subtext", "#8a99b5")

        if hasattr(self, "_left_panel_w"):
            self._left_panel_w.setStyleSheet(f"background: {bg_main}; border-right: 1px solid {border};")

        if hasattr(self, "_sys_hdr_lbl"):
            self._sys_hdr_lbl.setStyleSheet(f"color: {accent}; background: transparent; letter-spacing: 1px;")

        if hasattr(self, "_info_panel"):
            self._info_panel.setStyleSheet(f"""
                background: {bg_card};
                border: 1px solid {border};
                border-radius: 6px;
            """)

        if hasattr(self, "_uptime_lbl"):
            self._uptime_lbl.setStyleSheet(f"color: {accent}; background: transparent; border: none;")

        if hasattr(self, "_proc_lbl"):
            self._proc_lbl.setStyleSheet(f"color: {subtext}; background: transparent; border: none;")

        if hasattr(self, "_os_lbl"):
            self._os_lbl.setStyleSheet(f"color: {accent}; background: transparent; border: none;")

        # Badges in basso
        if hasattr(self, "_badge_labels"):
            for lbl in self._badge_labels:
                fg, bg, bd = lbl.property("default_style")
                # Se siamo su un tema diverso da Cyberpunk, addolciamo i colori di sfondo delle pillole
                if accent != "#00f0ff":
                    lbl.setStyleSheet(f"""
                        color: {accent}; background: {bg_card};
                        border: 1px solid {border}; border-radius: 4px; padding: 5px 2px;
                    """)
                else:
                    lbl.setStyleSheet(f"""
                        color: {fg}; background: {bg};
                        border: 1px solid {bd}; border-radius: 4px; padding: 5px 2px;
                    """)
    
    def _build_right_panel(self) -> QWidget:
        self._right_panel_w = QWidget()
        self._right_panel_w.setFixedWidth(_RIGHT_W)

        lay = QVBoxLayout(self._right_panel_w)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(8)

        # Tracciamo tutte le etichette di sezione per aggiornarne il colore a runtime
        self._right_sec_labels = []
        def _sec(txt):
            l = QLabel(f"▶ {txt}")
            l.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
            self._right_sec_labels.append(l)
            return l

        # 1. Activity Log
        lay.addWidget(_sec("ACTIVITY LOG"))
        self._log = LogWidget()
        lay.addWidget(self._log, stretch=1)

        # 2. File Upload Zone
        lay.addWidget(_sec("FILE UPLOAD"))
        self._drop_zone = FileDropZone()
        self._drop_zone.setFixedHeight(65)
        self._drop_zone.file_selected.connect(self._on_file_selected)
        lay.addWidget(self._drop_zone)

        self._file_hint = QLabel("No file loaded — drop or click above to upload")
        self._file_hint.setFont(QFont("Consolas", 7))
        self._file_hint.setWordWrap(True)
        lay.addWidget(self._file_hint)

        # 3. Command Input
        lay.addWidget(_sec("COMMAND INPUT"))
        lay.addLayout(self._build_input_row())

        # 4. Pulsanti di Stato Affiancati (Inline Pills)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        self._interrupt_btn = QPushButton("🛑 INTERRUPT [ESC]")
        self._interrupt_btn.setFixedHeight(30)
        self._interrupt_btn.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        self._interrupt_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._interrupt_btn.clicked.connect(self._do_interrupt)
        btn_row.addWidget(self._interrupt_btn)

        self._mute_btn = QPushButton("🎙 MIC ACTIVE")
        self._mute_btn.setFixedHeight(30)
        self._mute_btn.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        self._mute_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._mute_btn.clicked.connect(self._toggle_mute)
        self._style_mute_btn()
        btn_row.addWidget(self._mute_btn)

        lay.addLayout(btn_row)

        # Applica immediatamente i colori dello stile corrente
        self._update_right_panel_styles()
        return self._right_panel_w

    def _update_right_panel_styles(self):
        """Aggiorna i colori del pannello destro in base al tema selezionato."""
        bg_main  = getattr(self, "c_bg_main", "#0b0e14")
        bg_card  = getattr(self, "c_bg_card", "#131722")
        border   = getattr(self, "c_border", "#1f293d")
        accent   = getattr(self, "c_accent", "#00f0ff")
        subtext  = getattr(self, "c_subtext", "#5a657b")

        if hasattr(self, "_right_panel_w"):
            self._right_panel_w.setStyleSheet(f"background: {bg_main}; border-left: 1px solid {border};")

        if hasattr(self, "_right_sec_labels"):
            for l in self._right_sec_labels:
                l.setStyleSheet(f"color: {accent}; background: transparent; letter-spacing: 1px;")

        if hasattr(self, "_file_hint"):
            self._file_hint.setStyleSheet(f"color: {subtext}; background: transparent;")

        if hasattr(self, "_interrupt_btn"):
            self._interrupt_btn.setStyleSheet("""
                QPushButton {
                    background: #1a0a10;
                    color: #ff3355;
                    border: 1px solid #4a121e;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background: #ff3355;
                    color: #ffffff;
                    border: 1px solid #ff3355;
                }
                QPushButton:pressed {
                    background: #990022;
                }
            """)

        if hasattr(self, "_log") and hasattr(self._log, "setStyleSheet"):
            self._log.setStyleSheet(f"background: {bg_card}; border: 1px solid {border}; color: {accent};")

        if hasattr(self, "_drop_zone") and hasattr(self._drop_zone, "setStyleSheet"):
            self._drop_zone.setStyleSheet(f"background: {bg_card}; border: 1px dashed {border}; color: {subtext};")

    def _build_quick_drawer(self) -> QWidget:
        """Floating overlay panel shown when the ⚙ header button is toggled."""
        self._drawer_w = QWidget(self.centralWidget())
        self._drawer_w.setObjectName("QuickDrawer")
        self._drawer_w.hide()

        lay = QVBoxLayout(self._drawer_w)
        lay.setContentsMargins(10, 8, 10, 10)
        lay.setSpacing(5)

        self._drawer_hdr = QLabel("◈ CONTROLS")
        self._drawer_hdr.setFont(QFont("Courier New", 7, QFont.Weight.Bold))
        lay.addWidget(self._drawer_hdr)

        self._remote_btn = QPushButton("◉   REMOTE CONTROL")
        self._remote_btn.setFixedHeight(30)
        self._remote_btn.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        self._remote_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._remote_btn.clicked.connect(self._open_remote)
        lay.addWidget(self._remote_btn)

        self._fs_btn = QPushButton("⛶   FULLSCREEN  [F11]")
        self._fs_btn.setFixedHeight(26)
        self._fs_btn.setFont(QFont("Courier New", 7))
        self._fs_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._fs_btn.clicked.connect(self._toggle_fullscreen)
        lay.addWidget(self._fs_btn)

        self._sc_btn = QPushButton("⊞   CREATE DESKTOP SHORTCUT")
        self._sc_btn.setFixedHeight(26)
        self._sc_btn.setFont(QFont("Courier New", 7))
        self._sc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._sc_btn.clicked.connect(self._create_desktop_shortcut)
        lay.addWidget(self._sc_btn)

        self._autostart_btn = QPushButton("◉   AUTO-START: OFF")
        self._autostart_btn.setFixedHeight(26)
        self._autostart_btn.setFont(QFont("Courier New", 7))
        self._autostart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._autostart_btn.clicked.connect(self._toggle_autostart)
        lay.addWidget(self._autostart_btn)

        self._cust_btn = QPushButton("⚙   CUSTOMISE ASSISTANT")
        self._cust_btn.setFixedHeight(26)
        self._cust_btn.setFont(QFont("Courier New", 7))
        self._cust_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cust_btn.clicked.connect(self._open_customize)
        lay.addWidget(self._cust_btn)

        self._brief_btn = QPushButton()
        self._brief_btn.setFixedHeight(26)
        self._brief_btn.setFont(QFont("Courier New", 7))
        self._brief_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._brief_btn.clicked.connect(self._toggle_brief)
        lay.addWidget(self._brief_btn)

        # Applica immediatamente lo stile grafico iniziale
        self._update_quick_drawer_styles()

        self._drawer_w.adjustSize()
        return self._drawer_w

    def _update_quick_drawer_styles(self):
        """Aggiorna dinamicamente i colori del Quick Drawer in base al tema selezionato."""
        bg_main = getattr(self, "c_bg_main", "#0b0e14")
        bg_card = getattr(self, "c_bg_card", "#131722")
        border  = getattr(self, "c_border", "#1f293d")
        accent  = getattr(self, "c_accent", "#00f0ff")
        subtext = getattr(self, "c_subtext", "#8a99ad")

        # Stile Pulsante Primario (Remote Control)
        btn_style_pri = f"""
            QPushButton {{
                background: {bg_main}; color: {accent};
                border: 1px solid {accent}; border-radius: 3px;
                text-align: left; padding: 0 8px;
            }}
            QPushButton:hover {{ background: {bg_card}; border-color: {accent}; }}
        """

        # Stile Pulsanti Secondari
        btn_style_dim = f"""
            QPushButton {{
                background: transparent; color: {subtext};
                border: 1px solid {border}; border-radius: 3px;
                text-align: left; padding: 0 8px;
            }}
            QPushButton:hover {{ color: {accent}; border-color: {accent}; }}
        """

        if hasattr(self, "_drawer_w"):
            self._drawer_w.setStyleSheet(f"""
                QWidget#QuickDrawer {{
                    background: {bg_main};
                    border: 1px solid {border};
                    border-top: none;
                    border-radius: 0 0 6px 6px;
                }}
            """)

        if hasattr(self, "_drawer_hdr"):
            self._drawer_hdr.setStyleSheet(f"color: {accent}; background: transparent; "
                                           f"border-bottom: 1px solid {border}; padding-bottom: 4px;")

        if hasattr(self, "_remote_btn"):
            self._remote_btn.setStyleSheet(btn_style_pri)

        for btn_name in ["_fs_btn", "_sc_btn", "_autostart_btn", "_cust_btn", "_brief_btn"]:
            if hasattr(self, btn_name):
                getattr(self, btn_name).setStyleSheet(btn_style_dim)

    def _toggle_drawer(self, checked: bool):
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction, QFont

        menu = QMenu(self)
        menu.setFont(QFont("Segoe UI", 9))
        menu.setStyleSheet("""
            QMenu {
                background-color: #0b0e14;
                color: #e2e8f0;
                border: 1px solid #1f293d;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #131722;
                color: #00f0ff;
            }
            QMenu::separator {
                height: 1px;
                background: #1f293d;
                margin: 4px 0px;
            }
        """)

        # 1. Opzioni preesistenti
        act_hud = QAction("🧠 Memory Vault (HUD View)", self)
        act_hud.triggered.connect(self._load_memory_vault_view)
        menu.addAction(act_hud)

        act_obsidian = QAction("📂 Apri Obsidian Vault View", self)
        act_obsidian.triggered.connect(self._open_obsidian_vault_window)
        menu.addAction(act_obsidian)

        # -------------------------------------------------------------
        # 2. Nuova voce: Impostazioni & Temi
        # -------------------------------------------------------------
        menu.addSeparator()

        act_settings = QAction("⚙️ Impostazioni e Temi...", self)
        act_settings.triggered.connect(self._open_settings_dialog)
        menu.addAction(act_settings)

        # Mostra il menu esattamente sotto l'icona ingranaggio
        btn_widget = self.sender()
        if btn_widget:
            menu.exec(btn_widget.mapToGlobal(btn_widget.rect().bottomLeft()))

    def apply_theme(self, theme_name: str):
        """Metodo globale di cambio tema che aggiorna tutti i moduli visivi dell'HUD senza chiudere i pannelli."""
        print(f"[JARVIS UI] Applicazione tema: {theme_name}")

        # 1. Preserva lo stato di visibilità del pannello notizie/vault
        panel_was_visible = False
        if hasattr(self, "_content_panel_w") and self._content_panel_w:
            panel_was_visible = self._content_panel_w.isVisible()

        # 2. Definizione Palette Colori per i Temi Scuri & Nuovi Temi (Incluso il Core centrale)
        if "OLED" in theme_name:
            self.c_bg_main   = "#000000"
            self.c_bg_card   = "#080808"
            self.c_bg_btn    = "#0e0e0e"
            self.c_bg_hover  = "#181818"
            self.c_border    = "#222222"
            self.c_accent    = "#bb86fc"
            self.c_subtext   = "#777777"
            self.c_core_main = "#bb86fc"   # Viola chiaro
            self.c_core_sec  = "#7000ff"   # Viola scuro
        elif "Enterprise" in theme_name:
            self.c_bg_main   = "#0d1117"
            self.c_bg_card   = "#161b22"
            self.c_bg_btn    = "#1c2128"
            self.c_bg_hover  = "#2d333b"
            self.c_border    = "#30363d"
            self.c_accent    = "#58a6ff"
            self.c_subtext   = "#8b949e"
            self.c_core_main = "#58a6ff"   # Blu elettrico
            self.c_core_sec  = "#1f6beb"   # Blu scuro
        elif "Neon" in theme_name:
            self.c_bg_main   = "#050505"
            self.c_bg_card   = "#0d140d"
            self.c_bg_btn    = "#121f12"
            self.c_bg_hover  = "#1a2e1a"
            self.c_border    = "#1e3a1e"
            self.c_accent    = "#00ff66"   # Verde Fluo
            self.c_subtext   = "#ccff00"   # Giallo Fluo
            self.c_core_main = "#00ff66"   # Verde Fluo
            self.c_core_sec  = "#ccff00"   # Giallo Fluo
        elif "Cloud" in theme_name:
            self.c_bg_main   = "#0f172a"
            self.c_bg_card   = "#1e293b"
            self.c_bg_btn    = "#334155"
            self.c_bg_hover  = "#475569"
            self.c_border    = "#475569"
            self.c_accent    = "#f8fafc"   # Bianco Cloud
            self.c_subtext   = "#38bdf8"   # Sky Blue
            self.c_core_main = "#ffffff"   # Bianco Puro
            self.c_core_sec  = "#38bdf8"   # Azzurro Cielo
        elif "Purple" in theme_name:
            self.c_bg_main   = "#0a0512"
            self.c_bg_card   = "#140b24"
            self.c_bg_btn    = "#1f1038"
            self.c_bg_hover  = "#2e1065"
            self.c_border    = "#3b0764"
            self.c_accent    = "#ec4899"   # Rosa Neon
            self.c_subtext   = "#a855f7"   # Viola Deep
            self.c_core_main = "#ec4899"   # Rosa Neon
            self.c_core_sec  = "#a855f7"   # Viola Deep
        elif "Ironman" in theme_name:
            self.c_bg_main   = "#030a16"
            self.c_bg_card   = "#08152c"
            self.c_bg_btn    = "#0e2242"
            self.c_bg_hover  = "#15325b"
            self.c_border    = "#1e3a5f"
            self.c_accent    = "#00d8ff"   # Ciano Olografico Arc
            self.c_subtext   = "#ffd700"   # Oro Stark
            self.c_core_main = "#00d8ff"   # Ciano Reattore Arc
            self.c_core_sec  = "#ffd700"   # Oro Stark
        elif "Glitter" in theme_name:
            self.c_bg_main   = "#160526"
            self.c_bg_card   = "#240a3c"
            self.c_bg_btn    = "#3b0e5d"
            self.c_bg_hover  = "#5c138f"
            self.c_border    = "#ff77bc"
            self.c_accent    = "#ff66cc"
            self.c_subtext   = "#ffd700"
            self.c_core_main = "#ff66cc"
            self.c_core_sec  = "#ffd700"
        elif "Arctic" in theme_name:
            # Tema Chiaro / Minimal Ice Lab
            self.c_bg_main   = "#eef4f8"   # Sfondo principale grigio/azzurro ghiaccio
            self.c_bg_card   = "#ffffff"   # Card bianche
            self.c_bg_btn    = "#dbe3ed"   # Bottoni grigio-azzurri chiari
            self.c_bg_hover  = "#c7d5e5"   # Hover azzurrato
            self.c_border    = "#b0c4de"   # Bordi azzurro ghiaccio
            self.c_accent    = "#0284c7"   # Blu acceso per evidenziazioni
            self.c_subtext   = "#334155"   # Testo scuro/scuro antracite (LEGGIBILE!)
            self.c_core_main = "#0284c7"   # Reattore centrale azzurro
            self.c_core_sec  = "#38bdf8"

        elif "Matrix" in theme_name:
            self.c_bg_main   = "#020a02"   # Nero quasi totale
            self.c_bg_card   = "#051405"
            self.c_bg_btn    = "#0a220a"
            self.c_bg_hover  = "#0f330f"
            self.c_border    = "#155515"
            self.c_accent    = "#00ff33"   # Verde fosforescente
            self.c_subtext   = "#009922"
            self.c_core_main = "#00ff33"
            self.c_core_sec  = "#008811"

        elif "Deep Space" in theme_name:
            # Sfondo cosmico indaco/blu notte profondo
            self.c_bg_main   = "#040614"   # Nero spaziale/blu profondo
            self.c_bg_card   = "#0a0f26"   # Blu indaco scuro
            self.c_bg_btn    = "#111838"   # Blu notte
            self.c_bg_hover  = "#1a2452"   # Blu cosmico brillante
            self.c_border    = "#273570"   # Bordi indaco
            self.c_accent    = "#38bdf8"   # Ciano stellare / azzurro brillante
            self.c_subtext   = "#818cf8"   # Viola indaco tenue
            self.c_core_main = "#38bdf8"   # Reattore Ciano Stellare
            self.c_core_sec  = "#818cf8"   # Reattore Viola cosmico

        elif "Executive" in theme_name:
            self.c_bg_main   = "#0e0e11"   # Carbone scuro elegante
            self.c_bg_card   = "#16161a"   # Pannello nero premium
            self.c_bg_btn    = "#222228"
            self.c_bg_hover  = "#2e2e36"
            self.c_border    = "#3a3a46"
            self.c_accent    = "#d4af37"   # Oro discreto/Porsche 911 vibe 😉
            self.c_subtext   = "#e2e2e8"   # Bianco caldo
            self.c_core_main = "#d4af37"   # Oro lucido discreto
            self.c_core_sec  = "#8a7322"

        elif "Ocean" in theme_name:
            # Tema Ocean: Navy Scuro Abissale
            self.c_bg_main   = "#030a16"   # Blu Navy scurissimo (quasi nero)
            self.c_bg_card   = "#081326"   # Card Navy molto scura
            self.c_bg_btn    = "#0e1e38"   # Bottoni Navy scuro
            self.c_bg_hover  = "#172d52"   # Hover Blu leggermente più luminoso
            self.c_border    = "#1a2e4c"   # Bordi Navy discreti
            self.c_accent    = "#00d8ff"   # Ciano elettrico per scritte/dettagli
            self.c_subtext   = "#4a6b94"   # Testo secondario grigio-blu
            self.c_core_main = "#00d8ff"   # Reattore Ciano
            self.c_core_sec  = "#0055aa"   # Reattore Blu scuro

        elif "Glass" in theme_name:
            # Colori semitrasparenti per effetto Glassmorphism
            self.c_bg_main   = "#0f172a"
            self.c_bg_card   = "#1e293b"
            self.c_bg_btn    = "#334155"
            self.c_bg_hover  = "#475569"
            self.c_border    = "#38bdf8"
            self.c_accent    = "#a5f3fc"   # Ciano morbido lucido
            self.c_subtext   = "#94a3b8"
            self.c_core_main = "#38bdf8"
            self.c_core_sec  = "#a5f3fc"
        else:
            # Cyan Cyberpunk (Default)
            self.c_bg_main   = "#0b0e14"
            self.c_bg_card   = "#131722"
            self.c_bg_btn    = "#131722"
            self.c_bg_hover  = "#1c2333"
            self.c_border    = "#1f293d"
            self.c_accent    = "#00f0ff"
            self.c_subtext   = "#5a657b"
            self.c_core_main = "#00f0ff"
            self.c_core_sec  = "#0055ff"

     # Riconoscimento se il tema è di tipo CHIARO (es. Arctic)
            is_light_theme = "Arctic" in theme_name
    
            # QSS per Input, Log e componenti di testo
            text_color = "#0f172a" if is_light_theme else "#ffffff"
            log_text_color = "#0369a1" if is_light_theme else "#00f0ff"
            border_color = self.c_border
    
            # 1. Stile Finestra Principale e Top Bar Header
            main_qss = f"""
                QMainWindow, QDialog {{
                    background-color: {self.c_bg_main};
                    color: {text_color};
                }}
                QWidget#header_widget {{
                    background-color: {self.c_bg_card};
                    border-bottom: 1px solid {border_color};
                }}
                QLabel {{
                    color: {text_color};
                }}
                QLineEdit {{
                    background-color: {self.c_bg_card};
                    color: {text_color};
                    border: 1px solid {border_color};
                    padding: 6px;
                    border-radius: 4px;
                }}
                QTextEdit, QPlainTextEdit {{
                    background-color: {self.c_bg_card};
                    color: {log_text_color};
                    border: 1px solid {border_color};
                }}
            """
            self.setStyleSheet(main_qss)

        # 3. Gestione Overlay Particelle (Attivo SOLO per Glitter e Deep Space)
        if hasattr(self, "_glitter") and self._glitter:
            if any(k in theme_name for k in ["Glitter", "Sparkle", "Deep Space"]):
                if "Deep Space" in theme_name:
                    self._glitter.set_mode("stars")
                else:
                    self._glitter.set_mode("glitter")

                self._glitter.setGeometry(0, 0, self.width(), self.height())
                self._glitter.raise_()
                self._glitter.start()
            else:
                self._glitter.stop()  # Spegne le particelle per Ocean e tutti gli altri temi

        # Aggiornamento colore testo Activity Log nel pannello destro
        if hasattr(self, "log_widget") and self.log_widget:
            self.log_widget.setStyleSheet(f"""
                QTextEdit, QPlainTextEdit {{
                    background-color: {self.c_bg_card};
                    color: {self.c_accent}; /* Il testo prende il colore accento del tema! */
                    border: 1px solid {self.c_border};
                    font-family: 'Consolas', 'Segoe UI', monospace;
                }}
            """)
        elif hasattr(self, "_update_right_panel_styles"):
            self._update_right_panel_styles()

        # Aggiornamento colori dati Sys Monitor (CPU, RAM, GPU, NET)
        if hasattr(self, "_update_left_panel_styles"):
            self._update_left_panel_styles()
        elif hasattr(self, "sys_monitor_widget"):
            self.sys_monitor_widget.setStyleSheet(f"""
                QLabel {{
                    color: {self.c_accent}; /* Le percentuali e i valori prendono il colore del tema! */
                }}
                QLabel#subtext {{
                    color: {self.c_subtext};
                }}
                QProgressBar::chunk {{
                    background-color: {self.c_accent};
                }}
            """)

        # 4. Sfondo della finestra radice
        if "Glitter" in theme_name:
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background: qradialgradient(
                        cx: 0.5, cy: 0.5, radius: 0.8,
                        fx: 0.5, fy: 0.5,
                        stop: 0 #2a0845, 
                        stop: 0.6 #160526, 
                        stop: 1 #0d0218
                    );
                }
            """)
        if "Glass" in theme_name:
            self.setStyleSheet("""
                QFrame, QGroupBox {
                    background-color: rgba(30, 41, 59, 0.55);
                    border: 1px solid rgba(255, 255, 255, 0.18);
                    border-radius: 12px;
                }
                QPushButton {
                    background-color: rgba(51, 65, 85, 0.6);
                    border: 1px solid rgba(165, 243, 252, 0.3);
                    border-radius: 8px;
                    color: #f8fafc;
                }
                QPushButton:hover {
                    background-color: rgba(71, 85, 105, 0.8);
                    border: 1px solid #38bdf8;
                }
            """)
        if "Ocean" in theme_name:
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background: qradialgradient(
                        cx: 0.5, cy: 0.2, radius: 0.9,
                        fx: 0.5, fy: 0.1,
                        stop: 0 #082846, 
                        stop: 0.5 #03111e, 
                        stop: 1 #010810
                    );
                }
            """)
        else:
            self.setStyleSheet(f"background-color: {self.c_bg_main};")

        # 5. Propagazione dinamica a tutti i moduli dell'HUD
        if hasattr(self, "_update_header_styles"):
            self._update_header_styles()

        if hasattr(self, "_update_left_panel_styles"):
            self._update_left_panel_styles()

        if hasattr(self, "_update_center_panel_styles"):
            self._update_center_panel_styles()

        if hasattr(self, "_update_right_panel_styles"):
            self._update_right_panel_styles()

        if hasattr(self, "_update_quick_drawer_styles"):
            self._update_quick_drawer_styles()

        if hasattr(self, "_update_content_panel_styles"):
            self._update_content_panel_styles()

        if hasattr(self, "_update_input_row_styles"):
            self._update_input_row_styles()

        # Aggiornamento stili pannello destro (Activity Log, Dropzone, Command Input)
        if hasattr(self, "_update_right_panel_styles"):
            self._update_right_panel_styles()

        # Aggiornamento stili Sys Monitor (Pannello Sinistro)
        if hasattr(self, "_update_left_panel_styles"):
            self._update_left_panel_styles()

        # Aggiornamento stili News / Vault (Pannello Basso)
        if hasattr(self, "_update_content_panel_styles"):
            self._update_content_panel_styles()

        # 6. Passiamo i colori SPECIFICI del Core (c_core_main e c_core_sec)
        target_orb = getattr(self, "_face_widget", None) or getattr(self, "hud_canvas", None) or getattr(self, "orb_widget", None)
        
        if target_orb and hasattr(target_orb, "apply_theme_colors"):
            target_orb.apply_theme_colors(
                bg_hex=self.c_bg_main,
                main_hex=self.c_core_main,
                sec_hex=self.c_core_sec,
                theme_name=theme_name
            )
            target_orb.update()
        else:
            for child in self.findChildren(QWidget):
                if type(child).__name__ == "HudCanvas" and hasattr(child, "apply_theme_colors"):
                    child.apply_theme_colors(
                        bg_hex=self.c_bg_main,
                        main_hex=self.c_core_main,
                        sec_hex=self.c_core_sec,
                        theme_name=theme_name
                    )
                    child.update()

        # Aggiorna il colore del testo e dello sfondo nell'Activity Log
        if hasattr(self, "_log") and self._log:
            self._log.setStyleSheet(f"""
                QTextEdit, QPlainTextEdit, QLabel {{
                    color: {self.c_accent};
                    background-color: transparent;
                }}
            """)

        # Aggiorna le etichette del System Monitor
        if hasattr(self, "_sys_monitor") and self._sys_monitor:
            self._sys_monitor.setStyleSheet(f"""
                QLabel {{
                    color: {self.c_accent};
                }}
            """)

        # 7. Mantiene aperto il pannello notizie/vault se era già visibile prima del cambio tema
        if hasattr(self, "_content_panel_w") and self._content_panel_w and panel_was_visible:
            self._content_panel_w.show()

        if hasattr(self, "_update_notes_tabs_styles"):
            self._update_notes_tabs_styles()

        # Forza il ridisegno grafico immediato
        self.update()
        # ── SISTEMA RE-THEME DINAMICO GLOBALE ──────────────────────
        # Aggiorna la tavolozza globale e ricolora automaticamente Log, Sys Monitor e Testi
        old_pal = current_palette()
        if apply_ui_accent(self.c_accent):
            retheme_all_widgets(old_pal, current_palette())
        # ── RE-THEME HARDCORE DI TUTTI I WIDGET (LOG + SYS MONITOR) ──
        try:
            # 1. Salva la palette corrente prima della modifica
            old_pal = current_palette()

            # 2. Aggiorna le costanti primarie e secondarie del modulo colori (C)
            if hasattr(C, "PRI"):
                C.PRI = self.c_accent
            if hasattr(C, "ACCENT"):
                C.ACCENT = self.c_accent
            if hasattr(C, "SEC"):
                C.SEC = self.c_core_sec

            # 3. Forziamo apply_ui_accent ad applicare il colore primario
            apply_ui_accent(self.c_accent)

            # 4. Invochiamo il retheme di tutti i sotto-widget dell'HUD
            new_pal = current_palette()
            retheme_all_widgets(old_pal, new_pal)

            # 5. Se il log ha un proprio QTextEdit o stylesheet dedicato
            if hasattr(self, "_log") and hasattr(self._log, "setStyleSheet"):
                self._log.setStyleSheet(
                    f"color: {self.c_accent}; background: transparent;"
                )

            # 6. Se il Sys Monitor ha etichette specifiche da ricolorare
            if hasattr(self, "_sys_monitor") and hasattr(
                self._sys_monitor, "setStyleSheet"
            ):
                self._sys_monitor.setStyleSheet(
                    f"color: {self.c_accent}; background: transparent;"
                )

        except Exception as err:
            print(f"[JARVIS UI] Errore durante il retheme dinamico: {err}")

        # ── 1. RICALCOLO PALETTE GLOBALE HSV ─────────────────────
        # Ricalcola tutte le costanti di C (C.PRI, C.SEC, C.ACCENT, ecc.)
        if apply_ui_accent(self.c_accent):
            # C.PRI deve essere esattamente il colore di accento selezionato
            C.PRI = self.c_accent.lower()

        # ── 2. AGGIORNAMENTO FORZATO PANNELLO DESTRO (ACTIVITY LOG) ──
        if hasattr(self, "_log") and self._log:
            # Ricolora il contenitore del log
            self._log.setStyleSheet(f"""
                QTextEdit, QPlainTextEdit, QLabel {{
                    color: {self.c_accent} !important;
                    background-color: transparent;
                }}
            """)
            # Se la classe _log ha una proprietà per il colore di testo dei messaggi
            if hasattr(self._log, "c_accent"):
                self._log.c_accent = self.c_accent
            if hasattr(self._log, "_text_color"):
                self._log._text_color = self.c_accent

        # ── 3. AGGIORNAMENTO FORZATO PANNELLO SINISTRO (SYS MONITOR) ──
        if hasattr(self, "_update_left_panel_styles"):
            self._update_left_panel_styles()

        # Richiama retheme_all_widgets se disponibile per notificare gli altri moduli
        if "retheme_all_widgets" in globals():
            try:
                retheme_all_widgets(old_pal, current_palette())
            except Exception:
                pass

        # Forza il ridisegno immediato dell'interfaccia
        self.update()

    def _open_settings_dialog(self):
        """Apre la finestra delle impostazioni e applica il tema senza alterare lo stato dei pannelli."""
        dialog = SettingsDialog(self)
        if dialog.exec():  # Ritorna True quando l'utente clicca su "SALVA"
            config = dialog.config

            # Applica il tema selezionato (che preserva lo stato di visibilità del pannello)
            if hasattr(self, "apply_theme"):
                self.apply_theme(config.get("theme", "Cyan Cyberpunk (Default)"))

    def _position_quick_drawer(self):
        if not hasattr(self, '_quick_drawer'):
            return
        _W = 220
        self._quick_drawer.setFixedWidth(_W)
        self._quick_drawer.adjustSize()
        self._quick_drawer.setGeometry(12, 54, _W, self._quick_drawer.sizeHint().height())

    def _build_input_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(6)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Type a command or question...")
        self._input.setFont(QFont("Consolas", 9))
        self._input.setFixedHeight(34)
        self._input.returnPressed.connect(self._send)
        row.addWidget(self._input)

        self._send_btn = QPushButton("▸")
        self._send_btn.setFixedSize(34, 34)
        self._send_btn.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        self._send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._send_btn.clicked.connect(self._send)
        row.addWidget(self._send_btn)

        # Applica gli stili iniziali
        self._update_input_row_styles()
        return row

    def _update_input_row_styles(self):
        """Aggiorna lo stile del campo di testo e del pulsante invio."""
        bg_main = getattr(self, "c_bg_main", "#0b0e14")
        bg_card = getattr(self, "c_bg_card", "#131722")
        border  = getattr(self, "c_border", "#1f293d")
        accent  = getattr(self, "c_accent", "#00f0ff")
        subtext = getattr(self, "c_subtext", "#e2e8f0")

        if hasattr(self, "_input"):
            self._input.setStyleSheet(f"""
                QLineEdit {{
                    background: {bg_main};
                    color: {subtext};
                    border: 1px solid {border};
                    border-radius: 6px;
                    padding: 4px 10px;
                }}
                QLineEdit:focus {{
                    border: 1px solid {accent};
                    background: {bg_card};
                }}
            """)

        if hasattr(self, "_send_btn"):
            self._send_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {bg_card};
                    color: {accent};
                    border: 1px solid {border};
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    background: {bg_main};
                    color: {accent};
                    border: 1px solid {accent};
                }}
                QPushButton:pressed {{
                    background: {accent};
                    color: {bg_main};
                }}
            """)

    def _build_content_panel(self) -> QWidget:
        """Pannello nativo Memory Vault & News Feed Sci-Fi ad alta leggibilità."""
        self._content_panel_w = QWidget()
        self._content_panel_w.setObjectName("ContentPanel")
        self._content_panel_w.hide()

        lay = QVBoxLayout(self._content_panel_w)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(6)

        hdr = QHBoxLayout()
        hdr.setSpacing(6)

        # Indicatore Neon di sezione
        self._content_title_lbl = QLabel("▶ LIVE DATA FEED")
        self._content_title_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        hdr.addWidget(self._content_title_lbl)

        from PyQt6.QtWidgets import QComboBox
        self._memory_file_combo = QComboBox()
        self._memory_file_combo.setFont(QFont("Segoe UI", 8))
        self._memory_file_combo.setFixedHeight(24)
        self._memory_file_combo.currentIndexChanged.connect(self._on_memory_file_changed)
        hdr.addWidget(self._memory_file_combo)

        # Pulsanti Azione (New, Save, Delete)
        self._cp_new_btn = QPushButton("+ NEW")
        self._cp_new_btn.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self._cp_new_btn.setFixedHeight(24)
        self._cp_new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cp_new_btn.clicked.connect(self._create_new_memory_file)
        hdr.addWidget(self._cp_new_btn)

        self._cp_save_btn = QPushButton("💾 SAVE")
        self._cp_save_btn.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self._cp_save_btn.setFixedHeight(24)
        self._cp_save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cp_save_btn.clicked.connect(self._save_current_memory_file)
        hdr.addWidget(self._cp_save_btn)

        self._cp_del_btn = QPushButton("🗑️")
        self._cp_del_btn.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self._cp_del_btn.setFixedHeight(24)
        self._cp_del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cp_del_btn.clicked.connect(self._delete_current_memory_file)
        hdr.addWidget(self._cp_del_btn)

        hdr.addStretch()

        # Pulsante DISMISS
        self._cp_dismiss_btn = QPushButton("DISMISS ✕")
        self._cp_dismiss_btn.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self._cp_dismiss_btn.setFixedHeight(22)
        self._cp_dismiss_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cp_dismiss_btn.clicked.connect(self._content_panel_w.hide)
        hdr.addWidget(self._cp_dismiss_btn)

        lay.addLayout(hdr)

        self._cp_sep = QFrame()
        self._cp_sep.setFrameShape(QFrame.Shape.HLine)
        lay.addWidget(self._cp_sep)

        # Editor di testo Notizie / Data Feed
        self._content_display = QTextEdit()
        self._content_display.setReadOnly(False)
        self._content_display.setMinimumHeight(120)
        self._content_display.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        lay.addWidget(self._content_display)

        # Applica immediatamente gli stili dinamici
        self._update_content_panel_styles()
        return self._content_panel_w

    def _update_content_panel_styles(self):
        """Aggiorna i colori del ContentPanel in base al tema attivo."""
        bg_main = getattr(self, "c_bg_main", "#0b0e14")
        bg_card = getattr(self, "c_bg_card", "#131722")
        border  = getattr(self, "c_border", "#1f293d")
        accent  = getattr(self, "c_accent", "#00f0ff")
        subtext = getattr(self, "c_subtext", "#e2e8f0")

        if hasattr(self, "_content_panel_w") and self._content_panel_w:
            self._content_panel_w.setStyleSheet(f"QWidget#ContentPanel {{ background: {bg_main}; border-top: 1px solid {border}; }}")

        if hasattr(self, "_content_title_lbl"):
            self._content_title_lbl.setStyleSheet(f"color: {accent}; background: transparent; letter-spacing: 1.5px;")

        if hasattr(self, "_memory_file_combo"):
            self._memory_file_combo.setStyleSheet(f"""
                QComboBox {{
                    background: {bg_card}; color: {subtext};
                    border: 1px solid {border}; border-radius: 4px; padding: 1px 8px;
                }}
                QComboBox QAbstractItemView {{
                    background: {bg_card}; color: {subtext};
                    selection-background-color: {bg_main}; selection-color: {accent};
                }}
            """)

        if hasattr(self, "_content_display"):
            self._content_display.setStyleSheet(f"""
                QTextEdit {{
                    background: {bg_main};
                    color: {subtext};
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 12px;
                    border: 1px solid {border};
                    border-radius: 6px;
                    padding: 10px;
                    selection-background-color: {bg_card};
                    selection-color: {accent};
                }}
                QScrollBar:vertical {{
                    background: {bg_main}; width: 6px; border: none; margin: 2px;
                }}
                QScrollBar::handle:vertical {{
                    background: {border}; border-radius: 3px; min-height: 20px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background: {accent};
                }}
            """)

        if hasattr(self, "_cp_sep"):
            self._cp_sep.setStyleSheet(f"color: {border}; margin: 1px 0;")

        if hasattr(self, "_cp_dismiss_btn"):
            self._cp_dismiss_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: #5a657b;
                    border: 1px solid {border}; border-radius: 4px; padding: 0 8px;
                }}
                QPushButton:hover {{ color: #ff3355; border-color: #ff3355; }}
            """)

    def _load_memory_vault_view(self):
        """Carica le note nel pannello inferiore dell'HUD collegando la tendina _memory_file_combo (ricorsivo)."""
        from pathlib import Path

        try:
            vault_path = self._get_or_setup_memory_dir()
            md_files = sorted([p for p in vault_path.rglob("*.md") if p.is_file()])

            combo = self._memory_file_combo

            combo.blockSignals(True)
            combo.clear()

            if md_files:
                for f in md_files:
                    rel_path = str(f.relative_to(vault_path)).replace("\\", "/")
                    combo.addItem(rel_path, str(f.resolve()))

                combo.setEnabled(True)
                combo.blockSignals(False)

                first_file = md_files[0]
                testo = first_file.read_text(encoding="utf-8", errors="ignore")
                self._show_content(f"🧠 {first_file.name}", testo)
            else:
                combo.addItem("Nessuna nota trovata", None)
                combo.setEnabled(False)
                combo.blockSignals(False)
                self._show_content("🧠 MEMORY VAULT", "Nessuna nota (.md) trovata nella cartella.")

            if hasattr(self, "_log"):
                self._log.append_log(f"SYS: Vault HUD caricato da {vault_path}")
        except Exception as e:
            if hasattr(self, "_log"):
                self._log.append_log(f"ERR: Impossibile mostrare il Vault: {e}")

    def _on_memory_file_changed(self, index):
        file_path_str = self._memory_file_combo.itemData(index)
        if not file_path_str:
            return
        from pathlib import Path
        path = Path(file_path_str)
        if path.exists():
            try:
                text_content = path.read_text(encoding="utf-8")
                self._content_display.setPlainText(text_content)
                
                # Forzatura diretta del font sull'intero documento PyQt
                font = QFont("Segoe UI", 10)
                font.setStyleHint(QFont.StyleHint.Monospace)
                self._content_display.document().setDefaultFont(font)
                self._content_display.setFont(font)
            except Exception as e:
                self._content_display.setPlainText(f"Errore lettura file: {e}")

    def _on_note_selected_from_combo(self, file_path_or_index):
        """Legge la nota selezionata dalla tendina e la mostra a schermo."""
        from pathlib import Path

        file_path = None
        if isinstance(file_path_or_index, (str, Path)):
            file_path = Path(file_path_or_index)
        elif hasattr(self, "_notes_combo"):
            # Recupera il percorso del file salvato nell'item corrente del menu
            file_path = self._notes_combo.currentData()

        if file_path and isinstance(file_path, Path) and file_path.exists():
            testo = file_path.read_text(encoding="utf-8", errors="ignore")
            self._show_note_content(f"🧠 {file_path.name}", testo)

    def _show_note_content(self, title: str, text: str):
        """Mostra il testo della nota nell'editor dell'HUD o nel pannello principale."""
        if hasattr(self, "_note_editor"):
            self._note_editor.setPlainText(text)
        elif hasattr(self, "_content_sig"):
            self._content_sig.emit(title[:48], text[:4000])

    def _on_memory_file_changed(self, index):
        file_path_str = self._memory_file_combo.itemData(index)
        if not file_path_str:
            return
        from pathlib import Path
        path = Path(file_path_str)
        if path.exists():
            try:
                text_content = path.read_text(encoding="utf-8")
                self._content_display.setPlainText(text_content)
                
                # Forzatura diretta del font sull'intero documento PyQt
                font = QFont("Segoe UI", 10)
                font.setStyleHint(QFont.StyleHint.Monospace)
                self._content_display.document().setDefaultFont(font)
                self._content_display.setFont(font)
            except Exception as e:
                self._content_display.setPlainText(f"Errore lettura file: {e}")

    def _save_current_memory_file(self):
        index = self._memory_file_combo.currentIndex()
        file_path_str = self._memory_file_combo.itemData(index)
        if not file_path_str:
            return
        from pathlib import Path
        path = Path(file_path_str)
        try:
            path.write_text(self._content_display.toPlainText(), encoding="utf-8")
            self._log.append_log(f"SYS: Nota {path.name} salvata.")
        except Exception as e:
            self._log.append_log(f"ERR: Salvataggio fallito per {path.name}: {e}")

    def _create_new_memory_file(self):
        from PyQt6.QtWidgets import QInputDialog
        from pathlib import Path
        title, ok = QInputDialog.getText(self, "Memory Vault", "Nome della nuova nota (.md):")
        if ok and title.strip():
            filename = title.strip()
            if not filename.endswith(".md"):
                filename += ".md"
            path = Path("./app_memory") / filename
            if not path.exists():
                path.write_text(f"# {title.strip()}\n\n", encoding="utf-8")
                self._log.append_log(f"SYS: Nota {filename} creata.")
            self._load_memory_vault_view()

    def _delete_current_memory_file(self):
        from PyQt6.QtWidgets import QMessageBox
        from pathlib import Path
        index = self._memory_file_combo.currentIndex()
        file_path_str = self._memory_file_combo.itemData(index)
        if not file_path_str:
            return
        path = Path(file_path_str)
        if path.exists():
            reply = QMessageBox.question(self, "Memory Vault", f"Eliminare la nota '{path.name}'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                path.unlink()
                self._log.append_log(f"SYS: Nota {path.name} eliminata.")
                self._load_memory_vault_view()

    def _show_content(self, title: str, text: str):
        self._content_title_lbl.setText(f"▶ {title.upper()[:48]}")
        self._content_display.setPlainText(text)
        
        # Formattazione tipografica per il Data Feed News
        font = QFont("Segoe UI", 10)
        self._content_display.document().setDefaultFont(font)
        self._content_display.setFont(font)
        
        first_show = not self._content_panel.isVisible()
        self._content_panel.show()
        if first_show:
            total = self._center_split.height()
            self._center_split.setSizes([max(total - 240, 120), 240])

    

    def _on_file_selected(self, source):
        # 1. Risoluzione del percorso in base al tipo di parametro ricevuto
        if isinstance(source, QModelIndex):
            if not hasattr(self, 'model'):
                return  # Evita il crash se invocato prima dell'inizializzazione del modello
            path = self.model.filePath(source)
        elif isinstance(source, (str, Path)):
            path = str(source)
        else:
            return

        p = Path(path)
    
        # 2. Controllo validità ed estensione .md
        if p.is_file() and p.suffix.lower() == ".md":
            self.current_file_path = p
        
            if hasattr(self, 'title_label'):
                self.title_label.setText(p.stem)

            if not hasattr(self, 'editor'):
                return

            try:
                self.editor.blockSignals(True)
                content = p.read_text(encoding="utf-8", errors="ignore")
                self.editor.setPlainText(content)
            except Exception as e:
                print(f"[JARVIS Vault Error] Impossibile leggere il file {p.name}: {e}")
                self.editor.setPlainText(f"⚠️ Errore durante il caricamento della nota:\n{e}")
            finally:
                # Assicura il ripristino dei segnali anche in caso di eccezione
                self.editor.blockSignals(False)

            # 3. Aggiornamento delle statistiche (conteggio parole/caratteri)
            if hasattr(self, '_update_stats'):
                self._update_stats()

    def notify_phone_connected(self) -> None:
        if self._remote_overlay and self._remote_overlay.isVisible():
            self._remote_overlay.mark_connected()

    def _open_remote(self):
        if not self.on_remote_clicked:
            self._log.append_log("SYS: Dashboard not running — remote unavailable.")
            return
        result = self.on_remote_clicked()
        if not result:
            self._log.append_log("SYS: Could not generate remote key.")
            return
        url    = result[0]
        key    = result[1]
        auto   = result[2] if len(result) >= 3 else ""
        manual = result[3] if len(result) >= 4 else url
        if self._remote_overlay:
            self._remote_overlay._do_close()
        cw  = self.centralWidget()
        ow, oh = RemoteKeyOverlay._OW, RemoteKeyOverlay._OH
        ov  = RemoteKeyOverlay(url, key, auto_login_url=auto, manual_url=manual,
                               expiry_secs=600, parent=cw)
        ov.set_new_key_callback(self.on_remote_clicked)
        ov.setGeometry(
            (cw.width()  - ow) // 2,
            (cw.height() - oh) // 2,
            ow, oh,
        )
        ov.closed.connect(lambda: setattr(self, '_remote_overlay', None))
        ov.show()
        self._remote_overlay = ov
        self._log.append_log(f"SYS: Remote key generated — manual: {manual or url}")

    # ── Auto-start ──────────────────────────────────────────────────────────────

    def _check_autostart(self) -> bool:
        """Returns True if auto-start is currently registered on this OS."""
        try:
            if _OS == "Windows":
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
                try:
                    winreg.QueryValueEx(key, "JARVIS_AI")
                    return True
                except FileNotFoundError:
                    return False
                finally:
                    winreg.CloseKey(key)
            elif _OS == "Darwin":
                return (Path.home() / "Library" / "LaunchAgents"
                        / "com.jarvis.assistant.plist").exists()
            else:
                return (Path.home() / ".config" / "autostart" / "jarvis.desktop").exists()
        except Exception:
            return False

    def _toggle_autostart(self):
        currently_on = self._check_autostart()
        try:
            script = str(Path(__file__).resolve().parent / "main.py")
            if _OS == "Windows":
                import winreg
                reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
                if currently_on:
                    winreg.DeleteValue(reg, "JARVIS_AI")
                else:
                    pythonw = Path(sys.executable).parent / "pythonw.exe"
                    exe = str(pythonw if pythonw.exists() else sys.executable)
                    winreg.SetValueEx(reg, "JARVIS_AI", 0, winreg.REG_SZ,
                                      f'"{exe}" "{script}"')
                winreg.CloseKey(reg)
            elif _OS == "Darwin":
                plist_dir = Path.home() / "Library" / "LaunchAgents"
                plist_dir.mkdir(parents=True, exist_ok=True)
                plist = plist_dir / "com.jarvis.assistant.plist"
                if currently_on:
                    plist.unlink(missing_ok=True)
                else:
                    plist.write_text(
                        '<?xml version="1.0" encoding="UTF-8"?>\n'
                        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
                        '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
                        '<plist version="1.0"><dict>\n'
                        '  <key>Label</key><string>com.jarvis.assistant</string>\n'
                        '  <key>ProgramArguments</key><array>\n'
                        f'    <string>{sys.executable}</string>\n'
                        f'    <string>{script}</string>\n'
                        '  </array>\n'
                        '  <key>RunAtLoad</key><true/>\n'
                        '</dict></plist>\n'
                    )
            else:
                desk_dir = Path.home() / ".config" / "autostart"
                desk_dir.mkdir(parents=True, exist_ok=True)
                desk = desk_dir / "jarvis.desktop"
                if currently_on:
                    desk.unlink(missing_ok=True)
                else:
                    desk.write_text(
                        "[Desktop Entry]\n"
                        f"Name={self._assistant_name}\n"
                        f"Exec={sys.executable} {script}\n"
                        "Type=Application\nTerminal=false\n"
                        "X-GNOME-Autostart-enabled=true\n"
                    )
            enabled = not currently_on
            self._update_autostart_btn(enabled)
            self._log.append_log(
                f"SYS: Auto-start {'enabled' if enabled else 'disabled'}.")
        except Exception as e:
            self._log.append_log(f"ERR: Auto-start failed — {e}")

    def _update_autostart_btn(self, enabled: bool):
        if not hasattr(self, '_autostart_btn'):
            return
        if enabled:
            self._autostart_btn.setText("◉  AUTO-START: ON")
            self._autostart_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #001a08; color: {C.GREEN};
                    border: 1px solid {C.GREEN_D}; border-radius: 3px;
                }}
                QPushButton:hover {{ background: #002010; }}
            """)
        else:
            self._autostart_btn.setText("◉  AUTO-START: OFF")
            self._autostart_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {C.TEXT_DIM};
                    border: 1px solid {C.BORDER}; border-radius: 3px;
                }}
                QPushButton:hover {{ color: {C.TEXT}; border: 1px solid {C.BORDER_B}; }}
            """)

    def _toggle_brief(self):
        from memory.config_manager import get_brief_enabled, save_brief_enabled
        new_val = not get_brief_enabled()
        save_brief_enabled(new_val)
        self._update_brief_btn(new_val)

    def _update_brief_btn(self, enabled: bool):
        if not hasattr(self, '_brief_btn'):
            return
        if enabled:
            self._brief_btn.setText("☀  MORNING BRIEF: ON")
            self._brief_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #001a08; color: {C.GREEN};
                    border: 1px solid {C.GREEN_D}; border-radius: 3px;
                    text-align: left; padding: 0 8px;
                }}
                QPushButton:hover {{ background: #002010; }}
            """)
        else:
            self._brief_btn.setText("☀  MORNING BRIEF: OFF")
            self._brief_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {C.TEXT_DIM};
                    border: 1px solid {C.BORDER}; border-radius: 3px;
                    text-align: left; padding: 0 8px;
                }}
                QPushButton:hover {{ color: {C.TEXT}; border: 1px solid {C.BORDER_B}; }}
            """)

    # ── Customization ────────────────────────────────────────────────────────────

    def _open_customize(self):
        cfg = _read_full_config()
        if self._customize_overlay:
            self._customize_overlay.hide()
        cw = self.centralWidget()
        ov = CustomizeOverlay(
            cfg.get("assistant_name", "JARVIS") or "JARVIS",
            cfg.get("user_name", ""),
            cfg.get("ui_color", "") or DEFAULT_UI_COLOR,
            parent=cw,
        )
        ow, oh = CustomizeOverlay._OW, CustomizeOverlay._OH
        oh = min(oh, cw.height() - 16)
        ov.setGeometry(
            (cw.width()  - ow) // 2,
            (cw.height() - oh) // 2,
            ow, oh,
        )
        ov.on_preview = self._preview_ui_color
        ov.saved.connect(self._apply_name_update)
        ov.show()
        self._customize_overlay = ov

    def _preview_ui_color(self, hex_color: str):
        """Canlı önizleme — tüm arayüzü yeni renge boyar (config'e YAZMAZ)."""
        old = current_palette()
        if apply_ui_accent(hex_color):
            retheme_all_widgets(old, current_palette())

    def _apply_name_update(self, name: str, user_name: str, ui_color: str = ""):
        """Update all name/theme-dependent UI elements and persist to config."""
        self._assistant_name = name.strip() or "JARVIS"
        display = self._assistant_name.upper()
        self.setWindowTitle(f"{display} — MARK XLIX")
        
        # Applicazione diretta di Segoe UI Moderno
        self._title_lbl.setText(display)
        self._title_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self._title_lbl.setStyleSheet("color: #00f0ff; background: transparent; letter-spacing: 3px;")

        if display in ("JARVIS", "J.A.R.V.I.S"):
            self._sub_lbl.setText("Just A Rather Very Intelligent System")
        else:
            self._sub_lbl.setText("Personal AI Assistant")
            
        self._sub_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Normal))
        self._sub_lbl.setStyleSheet("color: #5a657b; background: transparent; letter-spacing: 1px;")

        self._log._ai_name_lc = self._assistant_name.lower()
        self.hud._assistant_name = display

        color_changed = False
        if ui_color:
            old = current_palette()
            if apply_ui_accent(ui_color):
                retheme_all_widgets(old, current_palette())
                color_changed = old["PRI"] != C.PRI

        try:
            data = _read_full_config()
            data["assistant_name"] = self._assistant_name
            data["user_name"] = user_name.strip()
            if ui_color:
                data["ui_color"] = ui_color.strip().lower()
            API_FILE.write_text(json.dumps(data, indent=4), encoding="utf-8")
            self._log.append_log(f"SYS: Identity updated — {display}")
            if color_changed:
                self._log.append_log(f"SYS: UI colour applied — {ui_color}")
        except Exception as e:
            self._log.append_log(f"ERR: Config save failed — {e}")
    # ── Clipboard intelligence ───────────────────────────────────────────────────

    def _on_clipboard_changed(self):
        try:
            text = QApplication.clipboard().text().strip()
            if len(text) >= 10:
                self._clipboard_sig.emit(text)
        except Exception:
            pass

    def _show_clipboard_panel(self, text: str):
        self._clipboard_panel.show_clipboard(text)
        self._position_clipboard_panel()

    def _position_clipboard_panel(self):
        cw = self.centralWidget()
        pw = ClipboardPanel._W
        ph = self._clipboard_panel.sizeHint().height() or ClipboardPanel._H
        x = (cw.width() - pw) // 2
        y = cw.height() - ph - 6
        self._clipboard_panel.setGeometry(x, y, pw, ph)
        self._clipboard_panel.raise_()

    def _on_clipboard_action(self, cmd: str):
        if self.on_text_command:
            threading.Thread(target=self.on_text_command, args=(cmd,), daemon=True).start()

    # ────────────────────────────────────────────────────────────────────────────

    def _do_interrupt(self):
        if self.on_interrupt:
            self.on_interrupt()

    def _toggle_mute(self):
        self._muted = not self._muted
        self.hud.muted = self._muted
        self._style_mute_btn()
        if self._muted:
            self._apply_state("MUTED")
            self._log.append_log("SYS: Microphone muted.")
        else:
            self._apply_state("LISTENING")
            self._log.append_log("SYS: Microphone active.")

    def _style_mute_btn(self):
        if self._muted:
            self._mute_btn.setText("🔇  MICROPHONE MUTED")
            self._mute_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #140006; color: {C.MUTED_C};
                    border: 1px solid {C.MUTED_C}; border-radius: 3px;
                }}
            """)
        else:
            self._mute_btn.setText("🎙  MICROPHONE ACTIVE")
            self._mute_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #00140a; color: {C.GREEN};
                    border: 1px solid {C.GREEN}; border-radius: 3px;
                }}
                QPushButton:hover {{ background: #001f10; }}
            """)

    def _send(self):
        txt = self._input.text().strip()
        if not txt: return
        self._input.clear()
        self._log.append_log(f"You: {txt}")
        if self.on_text_command:
            threading.Thread(target=self.on_text_command, args=(txt,), daemon=True).start()

    def _apply_state(self, state: str):
        self.hud.state    = state
        self.hud.speaking = (state == "SPEAKING")

    def _check_config(self) -> bool:
        if not API_FILE.exists(): return False
        try:
            d = json.loads(API_FILE.read_text(encoding="utf-8"))
            return bool(d.get("gemini_api_key")) and bool(d.get("os_system"))
        except Exception:
            return False

    def _show_setup(self):
        ov = SetupOverlay(self.centralWidget())
        cw = self.centralWidget()
        ow, oh = 460, 390
        ov.setGeometry(
            (cw.width()  - ow) // 2,
            (cw.height() - oh) // 2,
            ow, oh,
        )
        ov.done.connect(self._on_setup_done)
        ov.show()
        self._overlay = ov

    def _on_setup_done(self, key: str, os_name: str):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        API_FILE.write_text(
            json.dumps({"gemini_api_key": key, "os_system": os_name}, indent=4),
            encoding="utf-8",
        )
        self._ready = True
        if self._overlay:
            self._overlay.hide()
            self._overlay = None
        self._apply_state("LISTENING")
        self._assistant_name = _read_full_config().get("assistant_name", "JARVIS") or "JARVIS"
        self._log.append_log(f"SYS: Initialised. OS={os_name.upper()}. {self._assistant_name} online.")

    def dragEnterEvent(self, event):
        """Accetta il file in ingresso ed evidenzia la zona di rilascio."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            if hasattr(self, '_drop_overlay'):
                self._drop_overlay.setGeometry(self.rect().adjusted(15, 15, -15, -15))
                self._drop_overlay.show()
                self._drop_overlay.raise_()

    def dragLeaveEvent(self, event):
        """Nasconde l'overlay se esci dalla finestra."""
        if hasattr(self, '_drop_overlay'):
            self._drop_overlay.hide()

    def dropEvent(self, event):
        if hasattr(self, '_drop_overlay'):
            self._drop_overlay.hide()

        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if file_path:
                    import actions.smart_drop_handler as sdh
                    sdh.process_dropped_file(file_path, parent_window=self)

class _RootShim:
    def __init__(self, app: QApplication):
        self._app = app
    def mainloop(self):
        self._app.exec()
    def protocol(self, *_):
        pass


class JarvisUI:
    def __init__(self, face_path: str, size=None):
        self._app = QApplication.instance() or QApplication(sys.argv)
        self._app.setStyle("Fusion")
        self._win = MainWindow(face_path)
        self._win.show()
        self.root = _RootShim(self._app)

        # Applicazione del tema salvato nel file di configurazione all'avvio
        self._load_and_apply_initial_theme()

    def _load_and_apply_initial_theme(self):
        """Legge il tema dal file di configurazione e lo applica a MainWindow."""
        import json
        from pathlib import Path

        config_path = Path("./config/settings.json")
        saved_theme = "Cyan Cyberpunk (Default)"

        if config_path.exists():
            try:
                config = json.loads(config_path.read_text(encoding="utf-8"))
                saved_theme = config.get("theme", saved_theme)
            except Exception:
                pass
        else:
            # Fallback su config.json se presente nella root
            root_config = Path("config.json")
            if root_config.exists():
                try:
                    config = json.loads(root_config.read_text(encoding="utf-8"))
                    saved_theme = config.get("theme", saved_theme)
                except Exception:
                    pass

        if hasattr(self._win, "apply_theme"):
            self._win.apply_theme(saved_theme)

    @property
    def muted(self) -> bool:
        return self._win._muted

    @muted.setter
    def muted(self, v: bool):
        if v != self._win._muted:
            self._win._toggle_mute()

    @property
    def current_file(self) -> str | None:
        return self._win._drop_zone.current_file()

    @property
    def on_text_command(self):
        return self._win.on_text_command

    @on_text_command.setter
    def on_text_command(self, cb):
        self._win.on_text_command = cb

    @property
    def on_remote_clicked(self):
        return self._win.on_remote_clicked

    @on_remote_clicked.setter
    def on_remote_clicked(self, cb):
        self._win.on_remote_clicked = cb

    @property
    def on_interrupt(self):
        return self._win.on_interrupt

    @on_interrupt.setter
    def on_interrupt(self, cb):
        self._win.on_interrupt = cb

    def notify_phone_connected(self) -> None:
        self._win.notify_phone_connected()

    def set_state(self, state: str):
        self._win._state_sig.emit(state)

    def write_log(self, text: str):
        self._win._log_sig.emit(text)

    def wait_for_api_key(self):
        while not self._win._ready:
            time.sleep(0.1)

    def _get_or_setup_memory_dir(self) -> Path:
        """Legge la cartella memoria dal config. Se non esiste, la fa scegliere all'utente."""
        from pathlib import Path
        import json
        from PyQt6.QtWidgets import QFileDialog

        config_path = Path("./config/settings.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config = {}
        if config_path.exists():
            try:
                config = json.loads(config_path.read_text(encoding="utf-8"))
            except Exception:
                config = {}

        # Se la cartella è già salvata e valida, la usa subito
        if "memory_folder" in config and config["memory_folder"]:
            path = Path(config["memory_folder"])
            if path.exists():
                return path

        # Corretto: si passa self._win come QWidget padre per il QFileDialog
        chosen_dir = QFileDialog.getExistingDirectory(
            self._win, 
            "INSTALLAZIONE JARVIS — Seleziona la cartella per la Memoria (.md)",
            str(Path.home())
        )

        if not chosen_dir:
            chosen_dir = "./app_memory"

        final_path = Path(chosen_dir)
        final_path.mkdir(parents=True, exist_ok=True)

        config["memory_folder"] = str(final_path.resolve())
        config_path.write_text(json.dumps(config, indent=4), encoding="utf-8")

        if hasattr(self, "_log"):
            self._log.append_log(f"SYS: Cartella memoria configurata su: {final_path.resolve()}")
        return final_path

    def show_content(self, title: str, text: str):
        """Thread-safe: display content in the panel below the HUD."""
        self._win._content_sig.emit(title[:48], text[:4000])

    def prompt_reconfig(self):
        """Thread-safe: show the API key setup overlay (e.g. after an auth error)."""
        self._win._ready = False
        self._win._reconfig_sig.emit()

    def show_camera_frame(self, img_bytes: bytes):
        """Thread-safe: show a webcam frame in the small overlay (screen captures)."""
        self._win._camera_sig.emit(img_bytes)

    def start_camera_stream(self) -> None:
        """Thread-safe: start live camera feed in the full HUD area."""
        self._win.start_camera_stream()

    def stop_camera_stream(self) -> None:
        """Thread-safe: stop the live camera feed."""
        self._win.stop_camera_stream()

    @property
    def assistant_name(self) -> str:
        return self._win._assistant_name

    def start_speaking(self):
        self.set_state("SPEAKING")

    def stop_speaking(self):
        if not self.muted:
            self.set_state("LISTENING")
from PyQt6.QtGui import QTextCursor, QTextBlockFormat, QTextCharFormat

FONT_MODERNO = QFont("Cascadia Code", 10)
FONT_MODERNO.setFamilies(["Cascadia Code", "Fira Code", "JetBrains Mono", "Consolas", "monospace"])

class MarkdownEditor(QTextEdit):
    """Editor di testo avanzato con font moderno e formattazione automatica stile Obsidian."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(FONT_MODERNO)

    def keyPressEvent(self, event):
        cursor = self.textCursor()

        # Invio automatico per elenchi puntati con '-' o '*'
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            block_text = cursor.block().text()
            stripped = block_text.strip()

            if stripped in ("-", "*"):
                cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                cursor.removeSelectedText()
                cursor.insertBlock()
                return

            elif block_text.startswith("- ") or block_text.startswith("* "):
                prefix = block_text[:2]
                super().keyPressEvent(event)
                self.insertPlainText(prefix)
                return

        super().keyPressEvent(event)

import os
from pathlib import Path
from PyQt6.QtCore import Qt, QTimer, QSize, QModelIndex, QRectF, QDir
from PyQt6.QtGui import QFont, QColor, QIcon, QKeySequence, QAction, QFileSystemModel
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QLabel, QTextEdit, QTreeView, QHeaderView,
    QPushButton, QMenu, QInputDialog, QMessageBox, QFrame,
    QAbstractItemView
)

class ObsidianVaultWindow(QMainWindow):
    """Memory Vault in perfetto stile Obsidian — Drag&Drop, Ordinamento Alfabetico & Editor Zen."""
    def __init__(self, vault_path: str, parent=None):
        super().__init__(parent)
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(parents=True, exist_ok=True)

        self.current_file_path = None

        # Timer per Auto-Save automatico (2 secondi dopo l'ultima modifica)
        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.setSingleShot(True)
        self._auto_save_timer.setInterval(2000)
        self._auto_save_timer.timeout.connect(self._auto_save_active_file)

        self.setWindowTitle("MEMORY VAULT — OBSIDIAN CORE")
        self.resize(1100, 700)
        self._setup_ui()
        self._apply_obsidian_theme()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # ── 1. SIDEBAR FILE EXPLORER ─────────────────────────────────────────
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(12, 12, 12, 12)
        sidebar_layout.setSpacing(10)

        sidebar_header = QHBoxLayout()
        vault_label = QLabel("VAULT EXPLORER")
        vault_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        vault_label.setStyleSheet("color: #7d8590; letter-spacing: 1px;")
        sidebar_header.addWidget(vault_label)
        sidebar_header.addStretch()

        btn_new_file = QPushButton("📄+")
        btn_new_file.setToolTip("Nuova Nota")
        btn_new_file.setFixedSize(26, 26)
        btn_new_file.clicked.connect(self._create_new_file)

        btn_new_folder = QPushButton("📁+")
        btn_new_folder.setToolTip("Nuova Cartella")
        btn_new_folder.setFixedSize(26, 26)
        btn_new_folder.clicked.connect(self._create_new_folder)

        btn_refresh = QPushButton("🔄")
        btn_refresh.setToolTip("Ricarica e Ordina")
        btn_refresh.setFixedSize(26, 26)
        btn_refresh.clicked.connect(self._refresh_and_sort)

        for btn in (btn_new_file, btn_new_folder, btn_refresh):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #7d8590;
                    border: none;
                    border-radius: 4px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: #1e2330;
                    color: #00f0ff;
                }
            """)
            sidebar_header.addWidget(btn)

        sidebar_layout.addLayout(sidebar_header)

        self.model = QFileSystemModel()
        self.model.setRootPath(str(self.vault_path))
        self.model.setReadOnly(False)
        self.model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)
        self.model.setNameFilters(["*.md"])
        self.model.setNameFilterDisables(False)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(str(self.vault_path)))
        self.tree_view.setDragEnabled(True)
        self.tree_view.setAcceptDrops(True)
        self.tree_view.setDropIndicatorShown(True)
        self.tree_view.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
        for i in range(1, 4):
            self.tree_view.setColumnHidden(i, True)
        
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(14)
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        self.tree_view.clicked.connect(self._on_file_selected)

        sidebar_layout.addWidget(self.tree_view)
        splitter.addWidget(sidebar_widget)

        # ── 2. EDITOR WORKSPACE (STILE ZEN) ──────────────────────────────────
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(24, 16, 24, 12)
        editor_layout.setSpacing(8)

        self.title_label = QLabel("Seleziona o crea una nota")
        self.title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #e6edf3; padding-bottom: 4px;")
        editor_layout.addWidget(self.title_label)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #21262d; max-height: 1px; border: none;")
        editor_layout.addWidget(sep)

        self.editor = QTextEdit()
        self.editor.setFont(QFont("Segoe UI", 11))
        self.editor.setPlaceholderText("Inizia a scrivere la tua nota in Markdown...")
        self.editor.textChanged.connect(self._on_text_changed)
        editor_layout.addWidget(self.editor)

        footer_layout = QHBoxLayout()
        self.status_lbl = QLabel("● Pronto")
        self.status_lbl.setFont(QFont("Segoe UI", 8))
        self.status_lbl.setStyleSheet("color: #7d8590;")

        self.stats_lbl = QLabel("0 parole | 0 caratteri")
        self.stats_lbl.setFont(QFont("Segoe UI", 8))
        self.stats_lbl.setStyleSheet("color: #7d8590;")

        footer_layout.addWidget(self.status_lbl)
        footer_layout.addStretch()
        footer_layout.addWidget(self.stats_lbl)
        editor_layout.addLayout(footer_layout)

        # ── 3. GRAPH VIEW 2D & TABBED WORKSPACE ──────────────────────────────
        from ui_graph import ObsidianGraphView

        # Inizializzazione della vista grafico col nuovo parser gerarchico
        self.graph_view = ObsidianGraphView(vault_path=self.vault_path, parent=self)

        self.right_tabs = QTabWidget()
        self.right_tabs.addTab(editor_widget, "📝 Editor Note")
        self.right_tabs.addTab(self.graph_view, "🕸️ Graph View 2D")

        # Applica subito lo stile cromatico dinamico ai tab
        self._update_notes_tabs_styles()

        splitter.addWidget(self.right_tabs)

        # Proporzione Splitter (250px Sidebar, 850px Workspace)
        splitter.setSizes([250, 850])
        main_layout.addWidget(splitter)

    def _update_notes_tabs_styles(self):
        """Aggiorna lo stile cromatico dei tab dell'Editor e del Graph View in base al tema attivo."""
        bg_main = getattr(self, "c_bg_main", "#0b0e14")
        bg_card = getattr(self, "c_bg_card", "#131722")
        border  = getattr(self, "c_border", "#1f293d")
        accent  = getattr(self, "c_accent", "#00f0ff")
        subtext = getattr(self, "c_subtext", "#7d8590")

        if hasattr(self, "right_tabs") and self.right_tabs:
            self.right_tabs.setStyleSheet(f"""
                QTabWidget::pane {{
                    border: 1px solid {border};
                    background-color: {bg_main};
                }}
                QTabBar::tab {{
                    background: {bg_card};
                    color: {subtext};
                    padding: 8px 16px;
                    border: none;
                    font-family: 'Segoe UI';
                    font-size: 12px;
                }}
                QTabBar::tab:selected {{
                    background: {bg_main};
                    color: {accent};
                    border-bottom: 2px solid {accent};
                }}
            """)

        # Propaga il cambio tema anche al GraphView 2D
        if hasattr(self, "graph_view") and hasattr(self.graph_view, "apply_theme"):
            self.graph_view.apply_theme(bg_main, accent, border, subtext)

    def _apply_obsidian_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0b0e14;
            }
            QWidget {
                background-color: #0b0e14;
                color: #c9d1d9;
            }
            QSplitter::handle {
                background-color: #1e2330;
            }
            QTreeView {
                background-color: #080a0f;
                border: none;
                color: #8b949e;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QTreeView::item {
                padding: 4px 6px;
                border-radius: 4px;
            }
            QTreeView::item:hover {
                background-color: #161b22;
                color: #f0f6fc;
            }
            QTreeView::item:selected {
                background-color: #1f2430;
                color: #00f0ff;
            }
            QTextEdit {
                background-color: #0b0e14;
                border: none;
                color: #e6edf3;
                selection-background-color: #1f2d40;
                selection-color: #00f0ff;
                line-height: 1.5;
            }
        """)

    def _refresh_and_sort(self):
        self.model.setRootPath(str(self.vault_path))
        self.tree_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        if hasattr(self, "graph_view") and self.graph_view:
            self.graph_view.refresh_graph()

    def _on_file_selected(self, index: QModelIndex):
        path = self.model.filePath(index)
        p = Path(path)
        if p.is_file() and p.suffix.lower() == ".md":
            self.current_file_path = p
            self.title_label.setText(p.stem)
            try:
                self.editor.blockSignals(True)
                content = p.read_text(encoding="utf-8")
                self.editor.setPlainText(content)
                self.editor.blockSignals(False)
                self._update_stats()
                self.status_lbl.setText("● Salvato")
                self.status_lbl.setStyleSheet("color: #00f0ff;")
            except Exception as e:
                self.editor.blockSignals(False)
                self.status_lbl.setText(f"Errore: {e}")

    def _on_text_changed(self):
        if self.current_file_path:
            self.status_lbl.setText("● In modifica...")
            self.status_lbl.setStyleSheet("color: #a855f7;")
            self._update_stats()
            self._auto_save_timer.start()

    def _auto_save_active_file(self):
        if self.current_file_path and self.current_file_path.exists():
            try:
                text = self.editor.toPlainText()
                self.current_file_path.write_text(text, encoding="utf-8")
                self.status_lbl.setText("● Salvato")
                self.status_lbl.setStyleSheet("color: #00f0ff;")
                # Aggiornamento real-time del grafico al salvataggio
                if hasattr(self, "graph_view") and self.graph_view:
                    self.graph_view.refresh_graph()
            except Exception as e:
                self.status_lbl.setText(f"Errore salvataggio: {e}")
                self.status_lbl.setStyleSheet("color: #ff3355;")

    def _update_stats(self):
        text = self.editor.toPlainText()
        words = len(text.split())
        chars = len(text)
        self.stats_lbl.setText(f"{words} parole | {chars} caratteri")

    def _create_new_file(self):
        name, ok = QInputDialog.getText(self, "Nuova Nota", "Nome della nota (.md):")
        if ok and name.strip():
            if not name.endswith(".md"):
                name += ".md"
            new_path = self.vault_path / name
            try:
                new_path.write_text(f"# {new_path.stem}\n\n", encoding="utf-8")
                self._refresh_and_sort()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile creare il file: {e}")

    def _create_new_folder(self):
        name, ok = QInputDialog.getText(self, "Nuova Cartella", "Nome della cartella:")
        if ok and name.strip():
            new_dir = self.vault_path / name.strip()
            try:
                new_dir.mkdir(parents=True, exist_ok=True)
                self._refresh_and_sort()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile creare la cartella: {e}")

    def _show_context_menu(self, position):
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return

        file_path = Path(self.model.filePath(index))
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 16px;
                color: #c9d1d9;
                font-family: 'Segoe UI';
                font-size: 12px;
            }
            QMenu::item:selected {
                background-color: #1f2430;
                color: #00f0ff;
            }
        """)

        act_rename = QAction("✏️ Rinomina", self)
        act_delete = QAction("🗑️ Elimina", self)

        act_rename.triggered.connect(lambda: self._rename_item(file_path))
        act_delete.triggered.connect(lambda: self._delete_item(file_path))

        menu.addAction(act_rename)
        menu.addAction(act_delete)
        menu.exec(self.tree_view.viewport().mapToGlobal(position))

    def _rename_item(self, target_path: Path):
        new_name, ok = QInputDialog.getText(self, "Rinomina", "Nuovo nome:", text=target_path.name)
        if ok and new_name.strip():
            new_path = target_path.parent / new_name.strip()
            try:
                target_path.rename(new_path)
                if self.current_file_path == target_path:
                    self.current_file_path = new_path
                    self.title_label.setText(new_path.stem)
                self._refresh_and_sort()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile rinominare: {e}")

    def _delete_item(self, target_path: Path):
        reply = QMessageBox.question(
            self, "Conferma eliminazione",
            f"Sei sicuro di voler eliminare '{target_path.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if target_path.is_file():
                    target_path.unlink()
                elif target_path.is_dir():
                    import shutil
                    shutil.rmtree(target_path)
                
                if self.current_file_path == target_path:
                    self.current_file_path = None
                    self.title_label.setText("Seleziona o crea una nota")
                    self.editor.clear()
                self._refresh_and_sort()
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile eliminare: {e}")

    def open_note(self, file_path: Path):
        """Apre la nota selezionata dal grafo 2D dentro l'editor e commuta la scheda."""
        self.current_file_path = file_path
        if file_path.exists():
            text = file_path.read_text(encoding='utf-8', errors='ignore')
            self.title_label.setText(file_path.stem)
            self.editor.setPlainText(text)
            self.right_tabs.setCurrentIndex(0) # Torna al tab Editor