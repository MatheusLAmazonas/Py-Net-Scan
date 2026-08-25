from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QRectF
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QPushButton


class ToggleSwitch(QPushButton):
    """Botão de alternância estilo switch, com ícones de sol/lua fixos nas laterais."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(11, 10)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # remove o desenho nativo do botão (fundo/borda do SO), deixando só o paintEvent customizado
        self.setStyleSheet("QPushButton { border: none; background: transparent; }")
        self.setFlat(True)

        # posição do círculo: 0.0 = esquerda (claro), 1.0 = direita (escuro)
        self._pos = 0.0

        self._anim = QPropertyAnimation(self, b"pos_anim", self)
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked: bool):
        self._anim.stop()
        self._anim.setStartValue(self._pos)
        self._anim.setEndValue(1.0 if checked else 0.0)
        self._anim.start()

    def get_pos(self):
        return self._pos

    def set_pos(self, value):
        self._pos = value
        self.update()

    pos_anim = Property(float, get_pos, set_pos)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        radius = rect.height() / 2

        # cor de fundo (track): interpola de cinza claro para cinza-azulado escuro
        bg_light = QColor("#D5D8DC")
        bg_dark = QColor("#3C4148")
        bg = self._lerp_color(bg_light, bg_dark, self._pos)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg)
        painter.drawRoundedRect(QRectF(rect), radius, radius)

        # círculo deslizante — sólido, sem ícone interno
        margin = 2
        diameter = rect.height() - margin * 2
        x_min = margin
        x_max = rect.width() - diameter - margin
        x = x_min + (x_max - x_min) * self._pos

        circle_light = QColor("#FFFFFF")
        circle_dark = QColor("#9AA0A6")
        circle_color = self._lerp_color(circle_light, circle_dark, self._pos)

        painter.setBrush(circle_color)
        painter.drawEllipse(QRectF(x, margin, diameter, diameter))

        painter.end()

    @staticmethod
    def _lerp_color(c1: QColor, c2: QColor, t: float) -> QColor:
        r = int(c1.red() + (c2.red() - c1.red()) * t)
        g = int(c1.green() + (c2.green() - c1.green()) * t)
        b = int(c1.blue() + (c2.blue() - c1.blue()) * t)
        return QColor(r, g, b)