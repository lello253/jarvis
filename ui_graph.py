import math
import random
from pathlib import Path
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt6.QtGui import QPen, QColor, QBrush, QFont, QPainter
from PyQt6.QtCore import Qt, QPointF, QRectF, QTimer, QFileSystemWatcher


class NodeItem(QGraphicsItem):
    """Nodo grafico per la mappa di JARVIS (Radice, Cartelle e Note)."""
    def __init__(self, node_id: str, label: str, node_type: str, file_path: Path = None, parent_window=None):
        super().__init__()
        self.node_id = node_id
        self.label = label
        self.node_type = node_type  # 'ROOT', 'FOLDER', 'NOTE'
        self.file_path = file_path
        self.parent_window = parent_window

        self.vx = 0.0
        self.vy = 0.0

        # Dimensioni visive graduate
        if node_type == 'ROOT':
            self.radius = 18.0
        elif node_type == 'FOLDER':
            self.radius = 12.0
        else:
            self.radius = 7.0

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        self.is_hovered = False

    def boundingRect(self) -> QRectF:
        r = self.radius + 30
        return QRectF(-r, -r, 2 * r, 2 * r)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Recupera i colori del tema dal GraphView
        view = self.scene().views()[0] if self.scene() and self.scene().views() else None
        accent = getattr(view, "accent_color", QColor("#00f0ff"))
        subtext = getattr(view, "subtext_color", QColor("#8a99ad"))

        if self.node_type == 'ROOT':
            fill_color = QColor("#7000ff")
            border_color = accent
        elif self.node_type == 'FOLDER':
            fill_color = QColor(accent.red(), accent.green(), accent.blue(), 180)
            border_color = accent
        else:  # NOTE
            fill_color = QColor(138, 153, 173, 160)
            border_color = subtext

        if self.is_hovered:
            fill_color = QColor("#ffffff")
            border_color = QColor("#ffffff")

        # Disegno Cerchio Nodo
        painter.setPen(QPen(border_color, 2.0 if (self.is_hovered or self.node_type == 'ROOT') else 1.0))
        painter.setBrush(QBrush(fill_color))
        painter.drawEllipse(QPointF(0, 0), self.radius, self.radius)

        # Disegno Etichetta Testo
        painter.setPen(QPen(QColor("#ffffff") if self.is_hovered else subtext))
        font_size = 8 if self.node_type != 'NOTE' else 7
        is_bold = QFont.Weight.Bold if self.node_type != 'NOTE' else QFont.Weight.Normal
        painter.setFont(QFont("Segoe UI", font_size, is_bold))
        painter.drawText(QRectF(-60, self.radius + 2, 120, 18), Qt.AlignmentFlag.AlignCenter, self.label)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if self.scene() and self.scene().views():
                self.scene().views()[0].viewport().update()
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        """Doppio clic sul nodo nota per aprirla nell'editor."""
        if self.node_type == 'NOTE' and self.file_path:
            win = self.parent_window
            if hasattr(win, 'open_note'):
                win.open_note(self.file_path)
            elif hasattr(win, '_on_file_selected') and hasattr(win, 'model'):
                idx = win.model.index(str(self.file_path))
                if idx.isValid():
                    win._on_file_selected(idx)
        super().mouseDoubleClickEvent(event)

    def hoverEnterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().hoverLeaveEvent(event)


class ObsidianGraphView(QGraphicsView):
    """Canvas 2D interattivo stile Obsidian con gerarchia a Nodi Cartella, Fisica e Refresh Realtime."""
    def __init__(self, vault_path: Path, parent=None):
        super().__init__(parent)
        self.vault_path = Path(vault_path) if vault_path else None
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        # Configurazione Rendering
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        # Colori predefiniti
        self.bg_color = QColor("#080a0f")
        self.accent_color = QColor("#00f0ff")
        self.border_color = QColor("#1f293d")
        self.subtext_color = QColor("#8a99ad")
        self.setBackgroundBrush(QBrush(self.bg_color))

        self.nodes = {}
        self.edges = []

        # Engine della Fisica (Molla e Repulsione 60 FPS)
        self._physics_timer = QTimer(self)
        self._physics_timer.timeout.connect(self._step_physics)
        self._physics_timer.start(16)

        # Debounce Timer per aggiornamenti puliti
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(200)
        self._refresh_timer.timeout.connect(self.refresh_graph)

        # File System Watcher
        self._watcher = QFileSystemWatcher(self)
        self._watcher.directoryChanged.connect(self._trigger_refresh)
        self._watcher.fileChanged.connect(self._trigger_refresh)

        self.refresh_graph()

    def _trigger_refresh(self, _=None):
        """Avvia un refresh ritardato di 200ms per evitare collisioni di I/O."""
        self._refresh_timer.start()

    def _update_watcher_paths(self):
        """Registra tutte le sottocartelle nel file watcher."""
        if not self.vault_path or not self.vault_path.exists():
            return

        current_dirs = self._watcher.directories()
        if current_dirs:
            self._watcher.removePaths(current_dirs)

        dirs_to_watch = [str(self.vault_path.resolve())]
        for p in self.vault_path.rglob("*"):
            if p.is_dir():
                dirs_to_watch.append(str(p.resolve()))

        if dirs_to_watch:
            self._watcher.addPaths(dirs_to_watch)

    def apply_theme(self, bg_hex: str, accent_hex: str, border_hex: str, subtext_hex: str):
        """Aggiorna i colori del grafico al cambio tema dell'HUD."""
        self.bg_color = QColor(bg_hex)
        self.accent_color = QColor(accent_hex)
        self.border_color = QColor(border_hex)
        self.subtext_color = QColor(subtext_hex)
        self.setBackgroundBrush(QBrush(self.bg_color))
        self._scene.update()
        self.viewport().update()

    def refresh_graph(self):
        """Ricostruisce la rete: CORE MEMORY -> CARTELLE -> NOTE."""
        self._scene.clear()
        self.nodes.clear()
        self.edges.clear()

        if not self.vault_path or not self.vault_path.exists():
            return

        self._update_watcher_paths()

        # 1. Nodo Centrale Radice
        root_node = NodeItem("ROOT", "🧠 CORE MEMORY", "ROOT", parent_window=self.parent())
        root_node.setPos(0, 0)
        self._scene.addItem(root_node)
        self.nodes["ROOT"] = root_node

        # 2. Scansione file .md ricorsiva
        notes = sorted([p for p in self.vault_path.rglob("*.md") if p.is_file()])
        if not notes:
            return

        for f in notes:
            rel_parts = f.relative_to(self.vault_path).parts

            if len(rel_parts) > 1:
                # File dentro una sotto-cartella
                folder_name = rel_parts[0]
                folder_id = f"FOLDER_{folder_name}"

                if folder_id not in self.nodes:
                    f_node = NodeItem(folder_id, f"📁 {folder_name.upper()}", "FOLDER", parent_window=self.parent())
                    angle = random.uniform(0, 2 * math.pi)
                    f_node.setPos(140 * math.cos(angle), 140 * math.sin(angle))
                    self._scene.addItem(f_node)
                    self.nodes[folder_id] = f_node

                    # Collega Cartella -> Radice
                    self.edges.append((root_node, f_node, 160.0))

                note_node = NodeItem(str(f), f.stem, "NOTE", f, parent_window=self.parent())
                parent_folder = self.nodes[folder_id]
                note_node.setPos(parent_folder.x() + random.uniform(-30, 30), parent_folder.y() + random.uniform(-30, 30))
                self._scene.addItem(note_node)
                self.nodes[str(f)] = note_node

                # Collega Nota -> Cartella
                self.edges.append((parent_folder, note_node, 75.0))

            else:
                # File nella radice principale
                note_node = NodeItem(str(f), f.stem, "NOTE", f, parent_window=self.parent())
                angle = random.uniform(0, 2 * math.pi)
                note_node.setPos(200 * math.cos(angle), 200 * math.sin(angle))
                self._scene.addItem(note_node)
                self.nodes[str(f)] = note_node

                # Collega Nota -> Radice Centrale direttamente
                self.edges.append((root_node, note_node, 200.0))

        self.viewport().update()

    def _step_physics(self):
        """Simulazione della fisica Force-Directed."""
        node_list = list(self.nodes.values())
        if not node_list:
            return

        # Repulsione tra nodi
        for i in range(len(node_list)):
            n1 = node_list[i]
            for j in range(i + 1, len(node_list)):
                n2 = node_list[j]
                dx = n2.x() - n1.x()
                dy = n2.y() - n1.y()
                dist = math.hypot(dx, dy) + 0.01
                if dist < 200:
                    force = (200 - dist) / dist * 0.35
                    n1.vx -= dx * force * 0.04
                    n1.vy -= dy * force * 0.04
                    n2.vx += dx * force * 0.04
                    n2.vy += dy * force * 0.04

        # Attrazione elastica
        for n1, n2, target_dist in self.edges:
            dx = n2.x() - n1.x()
            dy = n2.y() - n1.y()
            dist = math.hypot(dx, dy) + 0.01
            delta = dist - target_dist
            force = delta * 0.025

            if n1.node_type != 'ROOT':
                n1.vx += (dx / dist) * force
                n1.vy += (dy / dist) * force
            n2.vx -= (dx / dist) * force
            n2.vy -= (dy / dist) * force

        # Smorzamento
        for n in node_list:
            if n.node_type == 'ROOT':
                n.setPos(n.x() * 0.85, n.y() * 0.85)
                continue

            n.setPos(n.x() + n.vx, n.y() + n.vy)
            n.vx *= 0.80
            n.vy *= 0.80

        self.viewport().update()

    def drawBackground(self, painter: QPainter, rect: QRectF):
        """Traccia le linee di connessione."""
        super().drawBackground(painter, rect)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor(self.accent_color.red(), self.accent_color.green(), self.accent_color.blue(), 70))
        pen.setWidthF(1.2)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)

        for n1, n2, _ in self.edges:
            painter.drawLine(n1.pos(), n2.pos())

    def wheelEvent(self, event):
        """Zoom fluido."""
        zoom_factor = 1.12 if event.angleDelta().y() > 0 else 1 / 1.12
        self.scale(zoom_factor, zoom_factor)