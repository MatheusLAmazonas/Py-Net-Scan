import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from ui.toggle_switch import ToggleSwitch

app = QApplication(sys.argv)
janela = QWidget()
layout = QVBoxLayout(janela)
layout.addWidget(ToggleSwitch())
janela.show()
sys.exit(app.exec())