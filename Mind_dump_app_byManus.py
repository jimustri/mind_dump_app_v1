
import sys
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QListWidget, QListWidgetItem, QAbstractItemView
from PyQt6.QtCore import Qt

class MindDumpDB:
    def __init__(self, db_name="mind_dump.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS thoughts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                thought TEXT
            )
        """)
        self.conn.commit()

    def save_thought(self, thought):
        if thought:
            today = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute("INSERT INTO thoughts (date, thought) VALUES (?, ?)", (today, thought))
            self.conn.commit()
            return True
        return False

    def get_thoughts_by_date(self):
        self.cursor.execute("SELECT date, thought FROM thoughts ORDER BY date DESC, id DESC")
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

class MindDumpApp(QWidget):
    def __init__(self):
        super().__init__()
        self.db = MindDumpDB()
        self.setWindowTitle("Mind Dump")
        self.setGeometry(100, 100, 600, 400)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        self.init_ui()
        self.load_thoughts()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Input section
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter your distracting thought...")
        self.input_field.returnPressed.connect(self.save_and_refresh)
        input_layout.addWidget(self.input_field)

        self.submit_button = QPushButton("Add Thought")
        self.submit_button.clicked.connect(self.save_and_refresh)
        input_layout.addWidget(self.submit_button)
        main_layout.addLayout(input_layout)

        # List display section
        self.thought_list = QListWidget()
        self.thought_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.thought_list)

        self.setLayout(main_layout)

    def save_and_refresh(self):
        thought = self.input_field.text().strip()
        if self.db.save_thought(thought):
            self.input_field.clear()
            self.load_thoughts()

    def load_thoughts(self):
        self.thought_list.clear()
        thoughts = self.db.get_thoughts_by_date()
        
        current_date = None
        for date, thought in thoughts:
            if date != current_date:
                date_item = QListWidgetItem(f"--- {date} ---")
                date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                date_item.setForeground(Qt.GlobalColor.blue)
                self.thought_list.addItem(date_item)
                current_date = date
            
            thought_item = QListWidgetItem(f"  - {thought}")
            self.thought_list.addItem(thought_item)

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MindDumpApp()
    window.show()
    sys.exit(app.exec())


