from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem
)

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

        self.log_table = QTableWidget()

        self.log_table.setColumnCount(3)

        self.log_table.setHorizontalHeaderLabels(
            [
                "Timestamp",
                "Level",
                "Message"
            ]
        )

        layout.addWidget(title)

        layout.addWidget(self.log_table)
    
    def load_logs(self):
        

        log_path = "logs/mathesis.log"

        if not os.path.exists(log_path):
            return

        self.log_table.setRowCount(0)

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
                logger.warning(f"Malformed log line skipped: {line}")
                continue

            timestamp, level, message = parts

            row = self.log_table.rowCount() 
            self.log_table.insertRow(row)

            self.log_table.setItem(
                row,
                0,
                QTableWidgetItem(timestamp)
            )

            self.log_table.setItem(
                row,
                1,
                QTableWidgetItem(level)
            )

            self.log_table.setItem(
                row,
                2,
                QTableWidgetItem(message)
            )
    

    def add_log_row(self, timestamp, level, message):

        row = self.log_table.rowCount()
        self.log_table.insertRow(row)

        self.log_table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.log_table.setItem(row, 1, QTableWidgetItem(level))
        self.log_table.setItem(row, 2, QTableWidgetItem(message))

        self.log_table.scrollToBottom()



    