from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout, 
    QLabel, 
    QPushButton, 
    QTableWidget,
    QTableWidgetItem, 
    QHBoxLayout, 
    QMessageBox
)
from ai.engine import generate_exercises
from database.db import Session
from database.models import PendingMessage, Student
from services.logger import log_event
from telegram_client.sync_wrapper import send_message_sync
from gui.preview_dialog import PreviewDialog
from datetime import datetime


class PendingMessagesWidget(QWidget):

    def __init__(self):
        super().__init__()
        #######################################
        self.layout = QVBoxLayout()

        self.title = QLabel("Pending Messages")

        self.table = QTableWidget()

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Student",
            "Username",
            "Message",
            "Sent"
        ])
        ###########################################
        self.refresh_button = QPushButton("Refresh")
        self.edit_button = QPushButton("Review")
        self.approve_button = QPushButton("Approve & Send All")
        self.delete_button = QPushButton("Delete")
        ###########################################
        

        ###########################################
        self.refresh_button.clicked.connect(self.load_pending_messages)
        self.edit_button.clicked.connect(self.review_message)
        self.approve_button.clicked.connect(self.approve_message)
        self.delete_button.clicked.connect(self.delete_message)
        ###########################################


        ###########################################
        button_layout = QHBoxLayout()

        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.approve_button)
        button_layout.addWidget(self.delete_button)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.table)
        ###########################################


        ###########################################
        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)
        ###########################################


        self.load_pending_messages()
    
    def load_pending_messages(self):

        session = Session()

        messages = (
            session.query(PendingMessage)
            .filter_by(sent=False)
            .all()
        )

        self.table.setRowCount(
            len(messages)
        )

        for row, message in enumerate(messages):

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(
                    str(message.id)
                )
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(
                    message.student_name
                )
            )

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(
                    message.student_username
                )
            )

            self.table.setItem(
                row,
                3,
                QTableWidgetItem(
                    message.message
                )
            )

            self.table.setItem(
                row,
                4,
                QTableWidgetItem(
                    str(message.sent)
                )
            )
        
        session.close()
        #self.hide()

    def review_message(self):

        selected_row = (
            self.table.currentRow()
        )

        if selected_row == -1:

            QMessageBox.warning(
                self,
                "Error",
                "Select a message first"
            )

            return
        message_id = int(
            self.table.item(
                selected_row,
                0
            ).text()
        )

        session = Session()
            
        pending = session.get(
            PendingMessage,
            message_id
        )

        if not pending:

            session.close()

            return

        while True:

            preview = PreviewDialog(
                pending.student_name,
                pending.message
            )

            preview.exec()

            print("ACTION:", preview.action)


            # CANCEL
            if preview.action == "cancel":
                
                session.close()

                return
            
            # ANOTHER EXERCISE
            if preview.action == "another":

                student = (
                    session.query(Student)
                    .filter_by(
                        telegram_username=(
                            pending.student_username
                        )
                    )
                    .first()
                )

                if not student:

                    session.close()

                    return

                exercise_data = generate_exercises(
                    subject=student.subject,
                    level=student.level,
                    student_id=student.id
                )

                if not exercise_data["ok"]:

                    QMessageBox.warning(
                        self,
                        "Error",
                        exercise_data["message"]
                    )

                    session.close()

                    return

                pending.message = (
                    exercise_data["content"]
                )

                pending.exercise_id = (
                    exercise_data["id"]
                )

                session.commit()

                continue

            # SEND CURRENT REVIEWED MESSAGE
            if preview.action == "send":

                final_message = (
                    preview.get_message()
                )

                try:

                    send_message_sync(
                        pending.student_username,
                        final_message
                    )

                    log_event("info", "pending_message_sent_after_review", pending_id=pending.id, student=pending.student_name, message_type=pending.message_type)

                    pending.message = (
                        final_message
                    )

                    pending.sent = True

                    pending.approved = True

                    student = session.get(
                        Student,
                        pending.student_id
                    )

                    if student:
                        student.last_generated_date = datetime.now().date()


                    session.commit()

                    QMessageBox.information(
                        self,
                        "Success",
                        "Message approved and sent"
                    )

                except Exception as e:

                    QMessageBox.warning(
                        self,
                        "Send Error",
                        str(e)
                    )

                    log_event("error", "pending_message_send_failed_review", pending_id=pending.id, error=str(e))
                break
            
        session.close()

        self.load_pending_messages()
        
    
    def delete_message(self):

        selected_row = (
            self.table.currentRow()
        )

        if selected_row == -1:

            QMessageBox.warning(
                self,
                "Error",
                "Select a message first"
            )

            return
        
        message_id = int(
            self.table.item(
                selected_row,
                0
            ).text()
        )

        session = Session()

        pending = session.get(
            PendingMessage,
            message_id

        )

        if pending:

            session.delete(
                pending
            )

            session.commit()
        
        log_event("warning", "pending_message_deleted", message_id=message_id)
        session.close()

        self.load_pending_messages()
    
    def approve_message(self):

        session = Session()

        pending_messages = (
            session.query(PendingMessage)
            .filter_by(sent=False)
            .all()
        )

        sent_count = 0

        for pending in pending_messages:

            try:

                send_message_sync(
                    pending.student_username,
                    pending.message
                )

                log_event("info", "pending_bulk_message_sent", pending_id=pending.id, student=pending.student_name, username=pending.student_username)

                pending.sent = True

                pending.approved = True 

                student = session.get(
                    Student,
                    pending.student_id
                )

                if student:
                    student.last_generated_date = datetime.now().date()
                
                sent_count += 1
            
            except Exception as e:
                log_event("error", "pending_bulk_send_failed", pending_id=pending.id, error=str(e))

        session.commit()
        
        session.close()

        QMessageBox.information(
            self,
            "Success",
            f"{sent_count} messages sent"
        )
        
        self.load_pending_messages()

    










