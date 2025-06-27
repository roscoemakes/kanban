import json
import copy
import os
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QMenuBar, QFileDialog, QFrame
)
from PyQt6.QtGui import QPalette, QColor
from column import KanbanColumn

# Default structure
initial_data = {
    'columns': {
        'backlog': {'name': 'Backlog', 'items': []},
        'todo': {'name': 'To Do', 'items': []},
        'inprogress': {'name': 'In Progress', 'items': []},
        'testing': {'name': 'Testing', 'items': []},
        'done': {'name': 'Done', 'items': []}
    }
}

class KanbanBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kanban")
        self.resize(1600, 800)
        self.theme = 'dark'
        self.data = copy.deepcopy(initial_data)
        self.columns = {}

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(0)

        for idx, (key, col_data) in enumerate(self.data['columns'].items()):
            col_widget = KanbanColumn(key, col_data['name'], col_data['items'], self)
            col_widget.set_theme(self.theme)
            self.columns[key] = col_widget
            self.layout.addWidget(col_widget)

            if idx < len(self.data['columns']) - 1:
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.VLine)
                separator.setFrameShadow(QFrame.Shadow.Sunken)
                separator.setLineWidth(2)
                separator.setStyleSheet("color: #ffffff; background-color: #ffffff;")
                self.layout.addWidget(separator)

        self.menubar = QMenuBar(self)
        self.menu_layout = QVBoxLayout()
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_layout.setSpacing(0)
        self.menu_layout.addWidget(self.menubar)
        self.menu_layout.addLayout(self.layout)
        self.setLayout(self.menu_layout)

        file_menu = self.menubar.addMenu("File")
        file_menu.addAction("New", self.new_board)
        file_menu.addAction("Open...", self.open_board_dialog)
        file_menu.addAction("Save", self.save_board)
        file_menu.addAction("Save As...", self.save_as_board)

        theme_menu = self.menubar.addMenu("Edit").addMenu("Theme")
        theme_menu.addAction("Light", lambda: self.set_theme('light'))
        theme_menu.addAction("Dark", lambda: self.set_theme('dark'))
        theme_menu.addAction("MSU", lambda: self.set_theme('msu'))

    def new_board(self):
        self.data = copy.deepcopy(initial_data)
        self.refresh_board()

    def save_board(self, filename="kanban_save.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def save_as_board(self):
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setNameFilter("Kanban Boards (*.json)")
        file_dialog.setDefaultSuffix("json")
        if file_dialog.exec():
            filename = file_dialog.selectedFiles()[0]
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)

    def open_board_dialog(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Kanban Boards (*.json)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        if file_dialog.exec():
            filename = file_dialog.selectedFiles()[0]
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                self.refresh_board()

    def refresh_board(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        self.columns.clear()

        for idx, (key, col_data) in enumerate(self.data['columns'].items()):
            col_widget = KanbanColumn(key, col_data['name'], col_data['items'], self)
            col_widget.set_theme(self.theme)
            self.columns[key] = col_widget
            self.layout.addWidget(col_widget)

            if idx < len(self.data['columns']) - 1:
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.VLine)
                separator.setFrameShadow(QFrame.Shadow.Sunken)
                separator.setLineWidth(2)
                separator.setStyleSheet("color: #ffffff; background-color: #ffffff;")
                self.layout.addWidget(separator)

    def set_theme(self, theme):
        self.theme = theme

        bg_color = {
            'light': '#f5f5f5',
            'dark': '#121212',
            'msu': '#18453B'
        }.get(theme, '#121212')

        self.setStyleSheet(f"background-color: {bg_color};")

        for col in self.columns.values():
            col.set_theme(theme)

        self.refresh_board()

        palette = self.palette()
        highlight = QColor("#00aaff") if theme != 'msu' else QColor("#18453B")
        fg = QColor("#222222") if theme == 'light' else QColor("#ffffff")
        palette.setColor(QPalette.ColorRole.WindowText, fg)
        palette.setColor(QPalette.ColorRole.ButtonText, fg)
        palette.setColor(QPalette.ColorRole.Highlight, highlight)
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        self.setPalette(palette)
