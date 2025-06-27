# dialog.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QTextEdit, QComboBox,
    QPushButton, QLabel, QDialogButtonBox, QCheckBox, QHBoxLayout
)
from PyQt6.QtCore import Qt


class AddCardDialog(QDialog):
    def __init__(self, parent=None, priority='Low', checklist=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Task")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #d6d6d6;
                font-size: 14px;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #121212;
                border: 1px solid #005577;
                border-radius: 6px;
                padding: 6px;
                color: #d6d6d6;
            }
            QPushButton {
                background-color: #00aaff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0088cc;
            }
        """)

        self.layout = QVBoxLayout(self)

        # Title input
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Task title")
        self.layout.addWidget(self.title_input)

        # Description input
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Task description")
        self.desc_input.setFixedHeight(80)
        self.layout.addWidget(self.desc_input)

        # Priority dropdown
        self.priority_select = QComboBox()
        self.priority_select.addItems(["Low", "Med", "High"])
        self.priority_select.setCurrentText(priority)
        self.layout.addWidget(self.priority_select)

        # Checklist label
        self.layout.addWidget(QLabel("Checklist:"))

        # Checklist layout
        self.checklist_items = []
        self.checklist_rows = []
        self.checklist_layout = QVBoxLayout()
        self.layout.addLayout(self.checklist_layout)

        self.set_checklist(checklist or [])

        # Add checklist item button
        self.add_checklist_button = QPushButton("+ Add Subtask")
        self.add_checklist_button.clicked.connect(self.add_checklist_item)
        self.layout.addWidget(self.add_checklist_button)

        # OK/Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

    def set_checklist(self, checklist):
        self.clear_checklist()
        for item in checklist:
            if isinstance(item, dict):
                self.add_checklist_item(item.get('text', ''), item.get('done', False))
            else:
                self.add_checklist_item(str(item), False)

    def clear_checklist(self):
        for row in self.checklist_rows:
            while row.count():
                item = row.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            self.checklist_layout.removeItem(row)
        self.checklist_items.clear()
        self.checklist_rows.clear()

    def add_checklist_item(self, text='', done=False):
        row = QHBoxLayout()
        checkbox = QCheckBox()
        checkbox.setChecked(done)

        line_edit = QLineEdit()
        line_edit.setText(str(text))

        remove_button = QPushButton("Remove")
        remove_button.setFixedWidth(70)

        def remove():
            checkbox.deleteLater()
            line_edit.deleteLater()
            remove_button.deleteLater()
            self.checklist_items.remove((checkbox, line_edit, remove_button))
            self.checklist_rows.remove(row)
            while row.count():
                item = row.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            self.checklist_layout.removeItem(row)

        remove_button.clicked.connect(remove)

        row.addWidget(checkbox)
        row.addWidget(line_edit)
        row.addWidget(remove_button)

        self.checklist_layout.addLayout(row)
        self.checklist_items.append((checkbox, line_edit, remove_button))
        self.checklist_rows.append(row)

    def get_data(self):
        title = self.title_input.text().strip()
        description = self.desc_input.toPlainText().strip()
        priority = self.priority_select.currentText()
        checklist = []
        for checkbox, line_edit, _ in self.checklist_items:
            text = line_edit.text().strip()
            if text:
                checklist.append({'text': text, 'done': checkbox.isChecked()})
        return title, description, priority, checklist
