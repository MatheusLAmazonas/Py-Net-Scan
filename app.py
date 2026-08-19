import sys
import os  # <-- ADICIONE
import ctypes

from PySide6.QtGui import QIcon  # <-- ADICIONE
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def load_stylesheet(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()



def main():

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "meuapp.custom.id"
        )
    except Exception:
        pass
    
    app = QApplication(sys.argv)

    

    caminho_icone = os.path.join(
        os.path.dirname(__file__), "resources", "logopy.png"
    )
    app.setWindowIcon(QIcon(caminho_icone))

    app.setStyle("Fusion")

    app.setStyleSheet(
        load_stylesheet("resources/styles.qss")
    )

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()