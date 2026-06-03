from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit
)

from PyQt6 import QtGui 

from services.logger import logger
from services.log_bus import log_bus

import os

class LogWidget(QWidget):

    def __init__(self):

        super().__init__()

        self.build_ui()

        log_bus.log_emitted.connect(self.add_log_row)



    def build_ui(self):

        layout = QVBoxLayout(self)

        title = QLabel("Application Logs")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search logs (message, level, timestamp)...")
        self.search_input.textChanged.connect(self.filter_logs)

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(3)
        self.log_table.setHorizontalHeaderLabels(
            ["Timestamp", "Level", "Message"]
        )

        layout.addWidget(title)
        layout.addWidget(self.search_input)
        layout.addWidget(self.log_table)

        #store logs in memory for filtering
        self.all_logs = []
    
    def load_logs(self):
        

        log_path = "logs/mathesis.log"

        if not os.path.exists(log_path):
            return

        self.log_table.setRowCount(0)
        self.all_logs = []

        with open(log_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        
        lines.reverse()

        for line in lines[:500]:

            line = line.strip()
            
            if not line:
                continue

            # EXPECTED FORMAT:
            # timestamp | level | message
            parts = line.split(" | ")

            # safety check (prevents crashes)
            if len(parts) != 3:
                # logger.warning(f"Malformed log line skipped: {line}")
                continue

            timestamp, level, message = parts

            log_entry = (timestamp, level, message)
            self.all_logs.append(log_entry)
        
        self.render_logs(self.all_logs)

    

    def add_log_row(self, timestamp, level, message):

        row = self.log_table.rowCount()
        self.log_table.insertRow(row)

        self.log_table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.log_table.setItem(row, 1, QTableWidgetItem(level))
        self.log_table.setItem(row, 2, QTableWidgetItem(message))

        self.log_table.scrollToBottom()
    

    def apply_row_color(self, row, level: str):

        if level == "INFO":
            color = "#2ecc71"  # green
        
        elif level == "WARNING":
            color = "#f39c12"  # orange
        
        elif level == "ERROR":
            color = "#e74c3c"  # red
        
        else:
            color = "#ffffff"
        

        for col in range(3):
            item = self.log_table.item(row, col)
            if item:
                item.setForeground(QtGui.QColor(color))
    


    def render_logs(self, logs):

        self.log_table.setRowCount(0)

        for timestamp, level, message in logs:

            row = self.log_table.rowCount()
            self.log_table.insertRow(row)

            self.log_table.setItem(row, 0, QTableWidgetItem(timestamp))
            self.log_table.setItem(row, 0, QTableWidgetItem(level))
            self.log_table.setItem(row, 2, QTableWidgetItem(message))


            self.apply_row_color(row, level)
    

    def filter_logs(self):

        query = self.search_input.text().lower().strip()

        if not query:
            self.render_logs(self.all_logs)
            return
        
        filtered = []

        for timestamp, level, message in self.all_logs:

            if (
                query in timestamp.lower()
                or query in level.lower()
                or query in message.lower()
            ):
                filtered.append((timestamp, level, message))
        
        self.render_logs(filtered)





    