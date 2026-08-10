import sys

from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def load_stylesheet(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()


def main():
    app = QApplication(sys.argv)

    app.setStyle("Fusion")

    app.setStyleSheet(
        load_stylesheet("resources/styles.qss")
    )

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()