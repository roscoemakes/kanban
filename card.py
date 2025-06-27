import json
from PyQt6.QtWidgets import QLabel, QMenu, QDialog, QVBoxLayout, QDialogButtonBox
from PyQt6.QtCore import Qt, QMimeData, QByteArray, QDataStream, QIODevice
from PyQt6.QtGui import QDrag

from dialog import AddCardDialog

MIME_TYPE = 'application/x-kanbancarddata'

class KanbanCard(QLabel):
    def __init__(self, card_id, title, description, parent=None, tag=None, priority=None, checklist=None):
        super().__init__(parent)
        self.card_id = card_id
        self.title = title
        self.description = description
        self.tag = tag or ''
        self.priority = priority or 'Low'
        self.checklist = checklist if checklist is not None else []
        self.theme = 'dark'
        self.update_card_text()

        self.setWordWrap(True)
        self.setMargin(10)
        self.setMinimumWidth(250)
        self.setMaximumWidth(280)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

    def set_theme(self, theme):
        self.theme = theme
        self.update_card_text()

    def update_card_text(self):
        tag_html = ''
        if self.tag:
            color = {'Bug': '#e74c3c', 'Feature': '#2980b9', 'Urgent': '#f39c12'}.get(self.tag, '#888888')
            tag_html = f'<span style="background:{color};color:white;padding:2px 8px;border-radius:8px;font-size:12px;margin-bottom:4px;">{self.tag}</span><br>'

        checklist_html = self.checklist_summary()

        self.setText(f"{tag_html}{checklist_html}<b>{self.title}</b><br><small>{self.description}</small>")

        # Theme-based styles
        bg, fg = (
            ('#f5f5f5', '#222222') if self.theme == 'light' else
            ('#ffffff', '#18453B') if self.theme == 'msu' else
            ('#1e1e1e', '#d6d6d6')
        )

        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {fg};
                border-radius: 10px;
                padding: 12px;
                border-left: 10px solid {self.priority_color()};
            }}
            QLabel:hover {{
                background-color: {'#eeeeee' if self.theme == 'msu' else '#333333'};
            }}
        """)

    def checklist_summary(self):
        if not self.checklist:
            return ''
        done = sum(1 for item in self.checklist if item.get('done'))
        total = len(self.checklist)
        return f'<span style="font-size:12px;color:#888;">{done}/{total} done</span><br>'

    def priority_color(self):
        return {'Low': '#27ae60', 'Med': '#f39c12', 'High': '#e74c3c'}.get(self.priority, '#888888')

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            drag = QDrag(self)
            mime_data = QMimeData()
            data = QByteArray()
            stream = QDataStream(data, QIODevice.OpenModeFlag.WriteOnly)
            stream.writeQString(self.card_id)
            stream.writeQString(self.title)
            stream.writeQString(self.description)
            stream.writeQString(self.tag)
            stream.writeQString(self.priority)
            stream.writeQString(json.dumps(self.checklist))
            mime_data.setData(MIME_TYPE, data)
            drag.setMimeData(mime_data)
            drag.setPixmap(self.grab())
            drag.setHotSpot(event.pos())
            drag.exec(Qt.DropAction.MoveAction)
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        elif event.button() == Qt.MouseButton.RightButton:
            self.contextMenuEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        tag_menu = menu.addMenu("Set Tag")
        for tag in ["Bug", "Feature", "Urgent", "None"]:
            tag_menu.addAction(tag)
        prio_menu = menu.addMenu("Set Priority")
        for level in ["Low", "Med", "High"]:
            prio_menu.addAction(level)

        action = menu.exec(event.globalPosition().toPoint())
        if action:
            text = action.text()
            if text == "Edit":
                self.edit_card()
            elif text == "Delete":
                self.remove_card()
            elif text in ["Bug", "Feature", "Urgent", "None"]:
                self.set_tag('' if text == "None" else text)
            elif text in ["Low", "Med", "High"]:
                self.set_priority(text)

    def set_tag(self, tag):
        self.tag = tag
        self.update_card_text()
        self.update_model("tag", tag)

    def set_priority(self, priority):
        self.priority = priority
        self.update_card_text()
        self.update_model("priority", priority)

    def update_model(self, key, value):
        column = self.parent()
        while column and not hasattr(column, 'key'):
            column = column.parent()
        board = column
        while board and not hasattr(board, 'data'):
            board = board.parent()
        if board and column:
            for item in board.data['columns'][column.key]['items']:
                if item['id'] == self.card_id:
                    item[key] = value
                    break

    def edit_card(self):
        dialog = AddCardDialog(self, priority=self.priority, checklist=self.checklist)
        dialog.title_input.setText(self.title)
        dialog.desc_input.setText(self.description)
        dialog.priority_select.setCurrentText(self.priority)
        if dialog.exec():
            new_title, new_desc, new_priority, new_checklist = dialog.get_data()
            self.title = new_title
            self.description = new_desc
            self.priority = new_priority
            self.checklist = new_checklist
            self.update_card_text()
            self.update_model('title', new_title)
            self.update_model('description', new_desc)
            self.update_model('priority', new_priority)
            self.update_model('checklist', new_checklist)

    def remove_card(self):
        column = self.parent()
        while column and not hasattr(column, 'key'):
            column = column.parent()
        board = column
        while board and not hasattr(board, 'data'):
            board = board.parent()
        if column and hasattr(column, 'cards') and self in column.cards:
            column.cards.remove(self)
        if column and hasattr(column, 'scroll_layout'):
            column.scroll_layout.removeWidget(self)
        self.setParent(None)
        if board and column:
            items = board.data['columns'][column.key]['items']
            board.data['columns'][column.key]['items'] = [item for item in items if item['id'] != self.card_id]

    def mouseDoubleClickEvent(self, event):
        dlg = QDialog(self)
        dlg.setWindowTitle("Subtasks")
        layout = QVBoxLayout()
        if self.checklist:
            for item in self.checklist:
                text = item.get('text', str(item))
                done = item.get('done', False)
                label = QLabel(f"{'✅' if done else '⬜'} {text}")
                layout.addWidget(label)
        else:
            layout.addWidget(QLabel("No subtasks"))
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(dlg.accept)
        layout.addWidget(buttons)
        dlg.setLayout(layout)
        dlg.exec()
