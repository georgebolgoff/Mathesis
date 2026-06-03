from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout,
    QTextEdit,
    QFileDialog,
    QLineEdit
)

from PyQt6 import QtGui
import os

from services.log_bus import log_bus


class LogWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.auto_scroll = True
        self.freeze = False

        self.current_logs = []
        self.all_logs = []

        self.build_ui()

        # 🔥 REAL-TIME CONNECTION (IMPORTANT PART)
        log_bus.log_emitted.connect(self.handle_live_log)

    # ---------------- UI ----------------
    def build_ui(self):

        layout = QVBoxLayout(self)

        title = QLabel("Application Logs")
        layout.addWidget(title)

        # BUTTON BAR
        btn_layout = QHBoxLayout()

        self.auto_scroll_btn = QPushButton("Auto-scroll: ON")
        self.freeze_btn = QPushButton("Freeze: OFF")
        self.export_btn = QPushButton("Export Logs")

        self.auto_scroll_btn.clicked.connect(self.toggle_auto_scroll)
        self.freeze_btn.clicked.connect(self.toggle_freeze)
        self.export_btn.clicked.connect(self.export_logs)

        btn_layout.addWidget(self.auto_scroll_btn)
        btn_layout.addWidget(self.freeze_btn)
        btn_layout.addWidget(self.export_btn)

        layout.addLayout(btn_layout)

        # SEARCH
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.filter_logs)
        layout.addWidget(self.search_input)

        # TABLE
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(3)
        self.log_table.setHorizontalHeaderLabels(
            ["Timestamp", "Level", "Message"]
        )

        self.log_table.cellClicked.connect(self.on_row_clicked)
        layout.addWidget(self.log_table)

        # DETAIL PANEL
        self.detail_box = QTextEdit()
        self.detail_box.setReadOnly(True)
        self.detail_box.setPlaceholderText("Click a log row to inspect details")
        self.detail_box.setFixedHeight(120)

        layout.addWidget(self.detail_box)

    # ---------------- REAL-TIME HANDLER ----------------
    def handle_live_log(self, timestamp, level, message):

        if self.freeze:
            return

        row = self.log_table.rowCount()
        self.log_table.insertRow(row)

        self.log_table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.log_table.setItem(row, 1, QTableWidgetItem(level))
        self.log_table.setItem(row, 2, QTableWidgetItem(message))

        self.apply_row_color(row, level)

        self.current_logs.append((timestamp, level, message))
        self.all_logs.append((timestamp, level, message))

        if self.auto_scroll:
            self.log_table.scrollToBottom()

    # ---------------- LOAD LOGS (file fallback) ----------------
    def load_logs(self):

        log_path = "logs/mathesis.log"

        if not os.path.exists(log_path):
            return

        self.log_table.setRowCount(0)
        self.current_logs.clear()
        self.all_logs.clear()

        with open(log_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        lines.reverse()

        for line in lines[:500]:

            line = line.strip()
            if not line:
                continue

            parts = line.split(" | ")
            if len(parts) != 3:
                continue

            timestamp, level, message = parts

            self.handle_live_log(timestamp, level, message)

    # ---------------- ROW CLICK ----------------
    def on_row_clicked(self, row, col):

        timestamp = self.log_table.item(row, 0).text()
        level = self.log_table.item(row, 1).text()
        message = self.log_table.item(row, 2).text()

        self.detail_box.setText(
            f"Timestamp: {timestamp}\n"
            f"Level: {level}\n"
            f"Message:\n{message}"
        )

    # ---------------- AUTO SCROLL ----------------
    def toggle_auto_scroll(self):
        self.auto_scroll = not self.auto_scroll
        self.auto_scroll_btn.setText(
            f"Auto-scroll: {'ON' if self.auto_scroll else 'OFF'}"
        )

    # ---------------- FREEZE ----------------
    def toggle_freeze(self):
        self.freeze = not self.freeze
        self.freeze_btn.setText(
            f"Freeze: {'ON' if self.freeze else 'OFF'}"
        )

    # ---------------- EXPORT ----------------
    def export_logs(self):

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            "logs_export.txt",
            "Text Files (*.txt)"
        )

        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            for t, l, m in self.current_logs:
                f.write(f"{t} | {l} | {m}\n")

    # ---------------- COLORING ----------------
    def apply_row_color(self, row, level: str):

        if level == "INFO":
            color = "#2ecc71"
        elif level == "WARNING":
            color = "#f39c12"
        elif level == "ERROR":
            color = "#e74c3c"
        else:
            color = "#ffffff"

        for col in range(3):
            item = self.log_table.item(row, col)
            if item:
                item.setForeground(QtGui.QColor(color))

    # ---------------- FILTER ----------------
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

    # ---------------- RENDER ----------------
    def render_logs(self, logs):

        self.log_table.setRowCount(0)

        for timestamp, level, message in logs:
            row = self.log_table.rowCount()
            self.log_table.insertRow(row)

            self.log_table.setItem(row, 0, QTableWidgetItem(timestamp))
            self.log_table.setItem(row, 1, QTableWidgetItem(level))
            self.log_table.setItem(row, 2, QTableWidgetItem(message))

            self.apply_row_color(row, level)