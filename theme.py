# theme.py

from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt


def apply_dark_palette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#121212"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#d6d6d6"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#1e1e1e"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#2e2e2e"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#121212"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#d6d6d6"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#1e1e1e"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#d6d6d6"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#00aaff"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    return palette


def apply_global_dark_stylesheet(app):
    """Apply global dark mode with custom widget tweaks."""
    app.setPalette(apply_dark_palette())
    app.setStyleSheet("""
        QWidget {
            background-color: #121212;
            color: #d6d6d6;
            font-size: 14px;
        }
        QPushButton {
            background-color: #00aaff;
            color: white;
            border-radius: 6px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background-color: #0088cc;
        }
        QLineEdit, QTextEdit, QComboBox {
            background-color: #1e1e1e;
            border: 1px solid #005577;
            border-radius: 4px;
            padding: 6px;
        }
        QMenu {
            background-color: #1e1e1e;
            color: #d6d6d6;
        }
        QMenu::item:selected {
            background-color: #00aaff;
            color: #ffffff;
        }
    """)
