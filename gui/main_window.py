from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from database.db import Session
from database.models import PendingMessage
from gui.student_widget import StudentWidget
from gui.pending_messages_widget import PendingMessagesWidget
from gui.exercise_database_dialog import ExerciseDatabaseDialog
from gui.content_database_dialog import ContentDatabaseDialog
from scheduler.tasks import start_scheduler

from PyQt6.QtCore import QTimer

#### STEP 5 ####
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mathesis")
        self.resize(1200, 700)

        self.selected_student = None

        layout = QVBoxLayout()
        top_bar = QHBoxLayout()

        title = QLabel("Teacher Automation Dashboard")
        self.status_label = QLabel("Ready")
        self.pending_indicator = QLabel()
        self.pending_indicator.setMinimumWidth(35)
        self.pending_indicator.setStyleSheet("""
            font-size: 18px;
            padding-bottom: 2px;
                                             
        """)

        self.student_widget = StudentWidget(self.set_selected_student)
        self.pending_widget = PendingMessagesWidget()

        self.pending_indicator = QLabel()
        self.pending_button = QPushButton("Pending Messages")
        self.database_button = QPushButton("Content Database")

        

        self.pending_button.clicked.connect(self.toggle_pending_messages)
        self.database_button.clicked.connect(self.open_content_database)

        top_bar.addWidget(self.status_label)
        top_bar.addStretch()
        top_bar.addWidget(self.database_button)
        top_bar.addWidget(self.pending_button)
        top_bar.addWidget(self.pending_indicator)

        layout.addWidget(title)
        layout.addLayout(top_bar)
        layout.addWidget(self.student_widget)
        layout.addWidget(self.pending_widget)

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

    

    # def open_database_manager(self):

    #     dialog = ExerciseDatabaseDialog()

    #     dialog.exec()
    
    def open_content_database(self):

        dialog = ContentDatabaseDialog()

        dialog.exec()



