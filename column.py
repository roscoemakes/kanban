from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QMenu
)
from PyQt6.QtCore import Qt, QMimeData, QByteArray, QDataStream, QIODevice, QPoint
from PyQt6.QtGui import QFont
from card import KanbanCard, MIME_TYPE
from dialog import AddCardDialog
import json

class KanbanColumn(QWidget):
    def __init__(self, key, name, items, parent=None):
        super().__init__(parent)
        self.key = key
        self.name = name
        self.items = items
        self.cards = []
        self.theme = 'dark'

        self.setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_column_context_menu)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(12)

        self.header = QLabel(name)
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.layout.addWidget(self.header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; }")

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_content.setLayout(self.scroll_layout)

        self.scroll.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll)

        self.setLayout(self.layout)
        self.load_cards()

    def set_theme(self, theme):
        self.theme = theme
        if theme == 'light':
            self.setStyleSheet("background-color: #f5f5f5; border-radius: 15px;")
            self.header.setStyleSheet("color: #222222; font-weight: bold;")
        elif theme == 'msu':
            self.setStyleSheet("""
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 15px;
                padding: 8px;
            """)
            self.header.setStyleSheet("color: #18453B; font-weight: bold;")
        else:
            self.setStyleSheet("""
                background-color: #1c1c1c;
                border: 1px solid #333;
                border-radius: 15px;
                padding: 8px;
            """)
            self.header.setStyleSheet("color: #00aaff; font-weight: bold;")

        for card in self.cards:
            card.set_theme(theme)

    def load_cards(self):
        for card_data in self.items:
            card = KanbanCard(
                card_id=card_data['id'],
                title=card_data['title'],
                description=card_data['description'],
                parent=self,
                tag=card_data.get('tag', ''),
                priority=card_data.get('priority', 'Low'),
                checklist=card_data.get('checklist', [])
            )
            card.set_theme(self.theme)
            self.cards.append(card)
            self.scroll_layout.addWidget(card)
        self.scroll_layout.addStretch()

    def show_column_context_menu(self, pos):
        menu = QMenu(self)
        add_task_action = menu.addAction("New Task")
        action = menu.exec(self.mapToGlobal(pos))
        if action == add_task_action:
            self.show_add_dialog()

    def show_add_dialog(self):
        dialog = AddCardDialog(self)
        if dialog.exec():
            title, desc, priority, checklist = dialog.get_data()
            if not title.strip():
                return

            parent = self.parent()
            while parent is not None and not hasattr(parent, 'data'):
                parent = parent.parent()
            if parent is None:
                return

            max_id = 0
            for col in parent.data['columns'].values():
                for item in col['items']:
                    try:
                        max_id = max(max_id, int(item['id']))
                    except:
                        pass
            new_id = str(max_id + 1)

            new_card = KanbanCard(new_id, title, desc, self, '', priority, checklist)
            new_card.set_theme(self.theme)
            self.cards.append(new_card)
            self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, new_card)

            parent.data['columns'][self.key]['items'].append({
                'id': new_id,
                'title': title,
                'description': desc,
                'tag': '',
                'priority': priority,
                'checklist': checklist
            })

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(MIME_TYPE):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(MIME_TYPE):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat(MIME_TYPE):
            data = event.mimeData().data(MIME_TYPE)
            stream = QDataStream(data, QIODevice.OpenModeFlag.ReadOnly)
            card_id = stream.readQString()
            title = stream.readQString()
            description = stream.readQString()
            tag = stream.readQString()
            priority = stream.readQString()
            checklist = json.loads(stream.readQString())

            parent = self.parent()
            while parent and not hasattr(parent, 'columns'):
                parent = parent.parent()
            if not parent:
                return

            source_column = None
            card_to_remove = None
            for col_key, col_widget in parent.columns.items():
                for card in col_widget.cards:
                    if card.card_id == card_id:
                        source_column = col_widget
                        card_to_remove = card
                        break

            if card_to_remove and source_column:
                source_column.cards.remove(card_to_remove)
                source_column.scroll_layout.removeWidget(card_to_remove)
                card_to_remove.setParent(None)
                for item in parent.data['columns'][source_column.key]['items']:
                    if item['id'] == card_id:
                        parent.data['columns'][source_column.key]['items'].remove(item)
                        parent.data['columns'][self.key]['items'].append(item)
                        break

            new_card = KanbanCard(card_id, title, description, self, tag, priority, checklist)
            new_card.set_theme(self.theme)
            self.cards.append(new_card)

            insert_index = self.get_drop_index(event.position().toPoint())
            self.scroll_layout.insertWidget(insert_index, new_card)

            event.acceptProposedAction()
        else:
            event.ignore()

    def get_drop_index(self, pos: QPoint) -> int:
        for i in range(self.scroll_layout.count() - 1):
            item = self.scroll_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if pos.y() < widget.y() + widget.height() // 2:
                    return i
        return self.scroll_layout.count() - 1

    def dragLeaveEvent(self, event):
        event.accept()
