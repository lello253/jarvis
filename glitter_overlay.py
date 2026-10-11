import random
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class SparkleParticle:

    def __init__(self, w: int, h: int, mode: str = "glitter"):
        self.w = w
        self.h = h
        self.mode = mode
        self.reset()

    def reset(self):
        self.x = random.randint(0, max(1, self.w))
        self.y = random.randint(0, max(1, self.h))
        
        if self.mode == "stars":
            self.size = random.randint(1, 4)
        elif self.mode == "ocean":
            self.size = random.randint(2, 5)
        else:
            self.size = random.randint(2, 6)

        self.alpha = random.randint(40, 230)
        self.fade_speed = random.choice([2, 4, 6])
        self.fading_out = True

        # Palette per ciascun tema
        if self.mode == "stars":
            colors = [
                QColor(255, 255, 255),  # Bianco
                QColor(186, 230, 253),  # Azzurro Chiaro
                QColor(56, 189, 248),   # Ciano Stellare
                QColor(129, 140, 248),  # Indaco Viola
                QColor(192, 132, 252),  # Viola Nebulosa
            ]
        elif self.mode == "ocean":
            colors = [
                QColor(0, 242, 254),    # Ciano Elettrico
                QColor(79, 172, 254),   # Blu Cristallino
                QColor(56, 239, 125),   # Verde Acquamarina
                QColor(186, 230, 253),  # Azzurro Superficie
                QColor(255, 255, 255),  # Bolla Bianca
            ]
        else:
            colors = [
                QColor(255, 102, 204),  # Rosa Sparkle
                QColor(255, 215, 0),    # Oro
                QColor(255, 182, 193),  # Rosa Chiaro
                QColor(255, 255, 255),  # Bianco
                QColor(200, 150, 255),  # Lilla
            ]
        self.color = random.choice(colors)

    def update(self):
        """Aggiorna trasparenza e movimento della particella."""
        # Se è in modalità oceano, fa fluttuare le bolle leggermente verso l'alto
        if self.mode == "ocean":
            self.y -= 0.5
            if self.y < 0:
                self.y = self.h
                self.x = random.randint(0, max(1, self.w))

        if self.fading_out:
            self.alpha -= self.fade_speed
            if self.alpha <= 20:
                self.fading_out = False
        else:
            self.alpha += self.fade_speed
            if self.alpha >= 240:
                self.fading_out = True
                if random.random() < 0.2:
                    self.reset()


class GlitterOverlay(QWidget):
    """Overlay trasparente per brillantini, campo stellare o bolle oceaniche."""

    def __init__(
        self,
        parent: QWidget | None = None,
        count: int = 80,
        mode: str = "glitter",
    ):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.mode = mode
        self.particles = []
        self.count = count

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.hide()

    def set_mode(self, mode: str):
        """Cambia la modalità tra 'glitter', 'stars' e 'ocean' rigenerando le particelle."""
        if self.mode != mode:
            self.mode = mode
            w, h = self.width(), self.height()
            if w > 0 and h > 0:
                self.particles = [
                    SparkleParticle(w, h, mode=self.mode)
                    for _ in range(self.count)
                ]

    def resizeEvent(self, event):
        w, h = self.width(), self.height()
        if w > 0 and h > 0:
            self.particles = [
                SparkleParticle(w, h, mode=self.mode) for _ in range(self.count)
            ]
        super().resizeEvent(event)

    def start(self):
        self.show()
        if not self.timer.isActive():
            self.timer.start(33)  # ~30 FPS

    def stop(self):
        self.timer.stop()
        self.hide()

    def _animate(self):
        for p in self.particles:
            p.update()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for p in self.particles:
            c = QColor(p.color)
            c.setAlpha(p.alpha)

            painter.setPen(QPen(c, 1.5))
            painter.drawPoint(int(p.x), int(p.y))

            s = p.size
            painter.drawLine(
                int(p.x - s), int(p.y), int(p.x + s), int(p.y)
            )  # Orizzontale
            painter.drawLine(
                int(p.x), int(p.y - s), int(p.x), int(p.y + s)
            )  # Verticale