from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QRectF
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QPushButton


class ToggleSwitch(QPushButton):
    """Botão de alternância estilo switch, com ícones de sol/lua fixos nas laterais."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("toggle_tema")
        self.setCheckable(True)
        self.setFixedSize(55, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # remove o desenho nativo do botão (fundo/borda do SO), deixando só o paintEvent customizado
        self.setStyleSheet(
            "QPushButton#toggle_tema { border: none; background: transparent; padding: 0px; }"
        )
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

        # --- Ícone no espaço vazio do track (lado oposto ao círculo) ---
        icon_diameter = diameter * 0.75
        icon_color = QColor("#FFFFFF") if self._pos > 0.5 else QColor("#4A4E54")

        if self._pos < 0.5:
            # Modo claro: desenha o sol no lado direito (espaço vazio)
            icon_x = x_max + (diameter - icon_diameter) / 2
            icon_y = margin + (diameter - icon_diameter) / 2
            self._desenhar_sol(painter, icon_x, icon_y, icon_diameter, icon_color)
        else:
            # Modo escuro: desenha a lua no lado esquerdo (espaço vazio)
            icon_x = x_min + (diameter - icon_diameter) / 2
            icon_y = margin + (diameter - icon_diameter) / 2
            self._desenhar_lua(painter, icon_x, icon_y, icon_diameter, icon_color, bg)

        # círculo deslizante por cima
        painter.setBrush(circle_color)
        painter.drawEllipse(QRectF(x, margin, diameter, diameter))

        painter.end()

    @staticmethod
    def _desenhar_sol(painter: QPainter, x: float, y: float, diametro: float, cor: QColor):
        """Desenha um sol simples: círculo (contorno) + raios curtos ao redor."""
        from PySide6.QtGui import QPen
        centro_x = x + diametro / 2
        centro_y = y + diametro / 2
        raio_nucleo = diametro * 0.32

        # núcleo: apenas contorno, sem preenchimento
        caneta_nucleo = QPen(cor)
        caneta_nucleo.setWidthF(diametro * 0.06)
        painter.setPen(caneta_nucleo)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(centro_x - raio_nucleo, centro_y - raio_nucleo,
                                    raio_nucleo * 2, raio_nucleo * 2))

        # raios ao redor do núcleo
        caneta_raios = QPen(cor)
        caneta_raios.setWidthF(diametro * 0.06)
        caneta_raios.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(caneta_raios)

        import math
        raio_interno = diametro * 0.42
        raio_externo = diametro * 0.5
        for angulo_graus in range(0, 360, 45):
            angulo = math.radians(angulo_graus)
            x1 = centro_x + raio_interno * math.cos(angulo)
            y1 = centro_y + raio_interno * math.sin(angulo)
            x2 = centro_x + raio_externo * math.cos(angulo)
            y2 = centro_y + raio_externo * math.sin(angulo)
            painter.drawLine(QRectF(x1, y1, 0, 0).topLeft(), QRectF(x2, y2, 0, 0).topLeft())

    @staticmethod
    def _desenhar_lua(painter: QPainter, x: float, y: float, diametro: float, cor: QColor, cor_recorte: QColor):
        """Desenha uma lua crescente: círculo cheio menos um círculo deslocado
        pintado com a cor de fundo atual do track (para o recorte funcionar em qualquer tema)."""
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(cor)
        painter.drawEllipse(QRectF(x, y, diametro, diametro))

        # "recorta" um círculo deslocado usando a cor de fundo ATUAL do track
        painter.setBrush(cor_recorte)
        deslocamento = diametro * 0.28
        recorte_diametro = diametro * 0.85
        painter.drawEllipse(QRectF(x + deslocamento, y - diametro * 0.05,
                                    recorte_diametro, recorte_diametro))

    @staticmethod
    def _lerp_color(c1: QColor, c2: QColor, t: float) -> QColor:
        r = int(c1.red() + (c2.red() - c1.red()) * t)
        g = int(c1.green() + (c2.green() - c1.green()) * t)
        b = int(c1.blue() + (c2.blue() - c1.blue()) * t)
        return QColor(r, g, b)