from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from database.db import Session
from database.models import PendingMessage
from gui.student_widget import StudentWidget
from gui.pending_messages_widget import PendingMessagesWidget
from gui.content_database_dialog import ContentDatabaseDialog
from services.log_bus import log_bus
from gui.log_widget import LogWidget

from PyQt6.QtCore import QTimer, Qt


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mathesis")
        self.resize(1200, 700)

        self.selected_student = None

        layout = QVBoxLayout()
        top_bar = QHBoxLayout()

        title = QLabel("Teacher Automation Dashboard")

        self.pending_indicator = QLabel()
        self.pending_indicator.setMinimumWidth(35)
        self.pending_indicator.setStyleSheet("""
            font-size: 18px;
            padding-bottom: 2px;
                                             
        """)

        self.latest_log_label = QLabel("")
        self.latest_log_label.setStyleSheet("""
            color: #bbbbbb;
            font-size: 12px;
            padding: 4px;
        """)

        self.student_widget = StudentWidget(self.set_selected_student, on_status=self.show_status,)
        self.pending_widget = PendingMessagesWidget()
        self.pending_widget.hide()
        self.log_widget = LogWidget()
        self.log_widget.hide()


        self.pending_button = QPushButton("Pending Messages")
        self.database_button = QPushButton("Content Database")
        self.logs_button = QPushButton("Logs")

        

        self.pending_button.clicked.connect(self.toggle_pending_messages)
        self.database_button.clicked.connect(self.open_content_database)
        self.logs_button.clicked.connect(self.show_logs)

        log_bus.log_emitted.connect(
            self.show_latest_log, 
            Qt.ConnectionType.QueuedConnection
        )

        top_bar.addStretch()
        top_bar.addWidget(self.logs_button)
        top_bar.addWidget(self.database_button)
        top_bar.addWidget(self.pending_button)
        top_bar.addWidget(self.pending_indicator)

        layout.addWidget(title)
        layout.addLayout(top_bar)
        layout.addWidget(self.student_widget)
        layout.addWidget(self.pending_widget)
        layout.addWidget(self.log_widget)
        layout.addWidget(self.latest_log_label)

        self.setLayout(layout)
        
        self.update_pending_indicator()

        self.pending_timer = QTimer()
        self.pending_timer.timeout.connect(self.refresh_pending_ui)
        self.pending_timer.start(3000)
    
    def set_selected_student(self, student):
        self.selected_student = student
    

    def get_selected_student(self):
        return self.selected_student


    def toggle_pending_messages(self):

        if self.pending_widget.isVisible():
            self.pending_widget.hide()
        
        else:
            self.log_widget.hide()
            self.pending_widget.load_pending_messages()
            self.pending_widget.show()
    

    def update_pending_indicator(self):

        session = Session()

        count = (
            session.query(PendingMessage)
            .filter_by(sent=False)
            .count()
        )

        session.close()

        if count == 0:
            self.pending_indicator.setText(
                "●"
            )
            self.pending_indicator.setStyleSheet(""" 
                color: #44ff88;
                font-size: 18px;
                font-weight:bold;
            """)
        
        else:

            self.pending_indicator.setText(
                f"● {count}!"
            )

            self.pending_indicator.setStyleSheet("""
                color: #ff4444;
                font-size: 18px;
                font-weight: bold;
            """)

    def refresh_pending_ui(self):

        self.update_pending_indicator()

        if self.pending_widget.isVisible():

            self.pending_widget.load_pending_messages()

    
    def open_content_database(self):

        dialog = ContentDatabaseDialog()

        dialog.exec()
    
    def show_logs(self):
        
        if self.log_widget.isVisible():
            self.log_widget.stop_tailing()
            self.log_widget.hide()
        
        else:

            self.pending_widget.hide()
            self.log_widget.load_logs()
            self.log_widget.start_tailing()
            self.log_widget.show()
    

    def show_status(self, message, level="INFO"):
        """Called by StudentWidget for user-facing action feedback."""
        self._display_status(message, level)
    
    
    def show_latest_log(self, timestamp, level, message):
        """Called by log_bus for backend logger output."""
        self._display_status(message, level)
    
    
    def _display_status(self, message, level="INFO"):
        self.latest_log_label.setText(f"[{level}] {message}")
        QTimer.singleShot(3000, self._clear_latest_log)
    

    def _clear_latest_log(self):
        self.latest_log_label.setText("")
    



