import sys
from PyQt6.QtWidgets import QApplication
from board import KanbanBoard
from theme import apply_dark_palette

def main():
    app = QApplication(sys.argv)
    app.setPalette(apply_dark_palette())
    window = KanbanBoard()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
