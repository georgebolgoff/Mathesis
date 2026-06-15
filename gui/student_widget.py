from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout,
    QLabel,
    QDialog,
    QInputDialog,
    QMessageBox,
)

from PyQt6.QtGui import QColor
from PyQt6.QtCore import QTimer

from datetime import datetime, timedelta

from database.db import Session
from database.models import Student, ExerciseHistory, PendingMessage, ExerciseAttempt
from ai.idiom_engine import generate_idiom, save_idiom_history
from gui.student_dialog import StudentDialog
from gui.preview_dialog import PreviewDialog
from gui.message_dialog import MessageDialog
from gui.topic_selection_dialog import TopicSelectionDialog
from telegram_client.sync_wrapper import send_message_sync
from telegram_client.sync_students import sync_students_sync
from services.message_formatter import format_message



class StudentWidget(QWidget):
    def __init__(self, on_selected_student):
        super().__init__()

        self.on_selected_student = on_selected_student

        self.layout = QVBoxLayout()

        title = QLabel("Students")
        self.status_label = QLabel("Ready")

        self.table = QTableWidget()

        self.table.setColumnCount(12)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Full Name",
            "Telegram",
            "Level",
            "Subjects",
            "🔥 Streak",
            "⏳ Reset In",
            "✅ Progress",
            "Active",
            "Exercise",
            "Idiom",
            "Message"
        ])

        self.add_button = QPushButton("Add Student")
        self.remove_button = QPushButton("Remove Student")
        self.sync_button = QPushButton("Sync Telegram Students")
        self.edit_button = QPushButton("Edit Student")
        self.reset_delivery_button = QPushButton("Reset Daily Delivery")


        self.add_button.clicked.connect(self.add_student)
        self.remove_button.clicked.connect(self.remove_student)
        self.edit_button.clicked.connect(self.edit_student)
        self.reset_delivery_button.clicked.connect(self.reset_daily_delivery)
        self.sync_button.clicked.connect(self.sync_students)
        self.table.itemSelectionChanged.connect(self.get_selected_student)

        button_layout = QHBoxLayout()

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.sync_button)
        button_layout.addWidget(self.reset_delivery_button)


        self.layout.addWidget(title)
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.table)
        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)

        self.refresh_timer = QTimer()

        self.refresh_timer.timeout.connect(
            self.refresh_streak_columns
        )

        self.refresh_timer.start(1000)

        try:
            self.load_students()
        except Exception as e:
            print("ERROR:", e)


    def load_students(self):

        session = Session()

        students = session.query(Student).all()

        self.table.setRowCount(0)

        self.table.setRowCount(len(students))

        for row, student in enumerate(students):

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(str(student.id))
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(student.full_name)
            )

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(student.telegram_username)
            )

            self.table.setItem(
                row,
                3,
                QTableWidgetItem(student.level.upper())
            )

            self.table.setItem(
                row,
                4,
                QTableWidgetItem(student.subject)
            )

            self.table.setItem(
                row,
                5,
                QTableWidgetItem(str(student.streak))
            )

            latest_attempt = (
                session.query(ExerciseAttempt)
                .filter_by(
                    student_id=student.id
                )
                .order_by(
                    ExerciseAttempt.sent_at.desc()
                )
                .first()
            )

            if (
                latest_attempt 
                and
                not latest_attempt.streak_awarded
            ):
                
                remaining = (
                    latest_attempt.sent_at
                    + timedelta(hours=48)
                    - datetime.utcnow()
                )

                total_seconds = max(
                    int(remaining.total_seconds()),
                    0
                )

                hours = total_seconds // 3600

                minutes = (
                    total_seconds % 3600
                ) // 60

                seconds = (
                    total_seconds % 60
                )

                reset_text = (
                    f"{hours:02d}h "
                    f"{minutes:02d}m "
                    f"{seconds:02d}s"

                )
            
            else:

                reset_text = "-"
            

            self.table.setItem(
                row,
                6,
                QTableWidgetItem(reset_text)
            )

            status_item = QTableWidgetItem()

            if not latest_attempt:

                status_item.setText("No Exercise")

                status_item.setBackground(
                    QColor(80, 80, 80)
                )

            elif latest_attempt.streak_awarded:

                status_item.setText("Completed")

                status_item.setBackground(
                    QColor(0, 120, 0)
                )
            
            else:

                status_item.setText("Waiting")

                status_item.setBackground(
                    QColor(120, 0, 0)
                )
            

            self.table.setItem(
                row,
                7,
                status_item
            )

            self.table.setItem(
                row,
                8,
                QTableWidgetItem(str(student.active))
            )

            generate_button = QPushButton("Generate")

            generate_button.clicked.connect(
                lambda checked=False,
                s=student: self.generate_for_student(s)
            )

            self.table.setCellWidget(
                row,
                9,
                generate_button
            )

            idiom_button = QPushButton("Idiom")

            idiom_button.clicked.connect(
                lambda _,
                s=student: self.send_idiom(s)
            )

            self.table.setCellWidget(
                row,
                10,
                idiom_button
            )

            message_button = QPushButton("Message")

            message_button.clicked.connect(
                lambda checked=False,
                s=student: self.message_student(s)
            )

            self.table.setCellWidget(
                row,
                11,
                message_button
            )

        session.close()
    
    def add_student(self):
        dialog = StudentDialog()
        
        result = dialog.exec()

        if not result:
            return
        
        data = dialog.get_data()

        session = Session()

        student = Student(
            full_name=data["full_name"],

            telegram_username=data["telegram_username"],

            level=data["level"].lower(),

            subject=data["subject"],

            daily_send_time=data["daily_send_time"],

            active=data["active"]
        )
        try:
            session.add(student)

            session.commit()
        except Exception as e:
            session.rollback()

            QMessageBox.warning(
                self,
                "Database Error",
                str(e)
            )
        finally:

            session.close()

        self.load_students()

    def edit_student(self):
        selected_row = self.table.currentRow()

        if selected_row == -1:

            QMessageBox.warning(
                self,
                "Error",
                "Select a student first"
            )
            return
        
        student_id = int(
            self.table.item(selected_row, 0).text()
        )

        session = Session()

        student = session.get(
            Student,
            student_id
        )

        if not student:

            session.close()

            return
        
        dialog = StudentDialog(student)

        result = dialog.exec()

        if not result:

            session.close()

            return
        data = dialog.get_data()

        try:

            student.full_name = (
                data["full_name"]
            )

            student.telegram_username = (
                data["telegram_username"]
            )

            student.level = (
                data["level"].lower()
            )

            student.subject = (
                data["subject"]
            )

            student.daily_send_time = (
                data["daily_send_time"]
            )

            student.active = (
                data["active"]
            )

            session.commit()
        except Exception as e:

            session.rollback()

            QMessageBox.warning(
                self,
                "Database Error",
                str(e)
            )
        
        finally:

            session.close()
        
        self.load_students()
    
    def remove_student(self):
        selected_row = self.table.currentRow()

        if selected_row == -1:
            QMessageBox.warning(
                self,
                "Error",
                "Select a student first."
            )
            return
        
        student_id = int(self.table.item(selected_row, 0).text())

        session = Session()

        student = session.get(Student, student_id)

        if student:
            session.delete(student)
            session.commit()
        
        session.close()

        self.load_students()
    

    def reset_daily_delivery(self):

        selected_row = self.table.currentRow()

        if selected_row == -1:

            QMessageBox.warning(
                self, "Error",
                "Select a student first"
            )
        
        id_item = self.table.item(
            selected_row,
            0
        )

        if id_item is None:

            QMessageBox.warning(
                self,
                "Error",
                "Invalid student row selected"
            )

            return

        student_id = int(
            id_item.text()
        )

        session = Session()

        try:

            student = session.get(
                Student,
                student_id
            )

            if not student:

                return
            
            student.last_generated_date = None
            student.last_sent_date = None

            session.commit()

            QMessageBox.information(
                self,
                "Success",
                (
                    f"Daily delivery reset for\n"
                    f"{student.full_name}"
                )
            )

        finally:

            session.close()
            



    def sync_students(self):
        try:
            sync_students_sync()

            self.load_students()

            self.status_label.setText("Telegram sync completed")
        
        except Exception as e:

            self.status_label.setText(
                f"Sync failed: {e}"
            )


    def preview_exercise(self, student, exercise):

        from ai.engine import generate_exercises
        from database.models import ExerciseHistory
        from services.message_formatter import format_message

        exercise_id = exercise["id"]

        exercise_text = format_message(
            student_id=student.id,
            content=exercise["content"],
            template_type="exercise"
        )

        while True:

            preview = PreviewDialog(
                student.full_name,
                exercise_text
            )

            preview.exec()

            if preview.action is None:
                return

            # CANCEL
            if preview.action == "cancel":
                return

            # ANOTHER
            if preview.action == "another":

                exercise_data = generate_exercises(
                    subject=student.subject,
                    level=student.level,
                    student_id=student.id
                )

                if not exercise_data["ok"]:

                    self.status_label.setText(
                        exercise_data["message"]
                    )

                    return

                exercise_id = (
                    exercise_data["id"]
                )

                exercise_text = format_message(
                    student_id=student.id,
                    content=exercise_data["content"],
                    template_type="exercise"
                )

                continue

            # CHOOSE TOPICS 
            if preview.action == "choose_topics":

                topic_dialog = (
                    TopicSelectionDialog()
                )

                result = topic_dialog.exec()

                if not result:
                    continue

                selected_data = (
                    topic_dialog.get_selected_data()
                )
                
                print(
                    "SELECTED TOPIC DATA:",
                    selected_data
                )

                self.status_label.setText(
                    "Advanced generation "
                    "system coming next..."
                )

                continue

            # FINAL CONFIRMED SEND
            if preview.action == "send":
                final_message = (preview.get_message())

                try:

                    session = Session()

                    pending = PendingMessage(
                        student_id=student.id,
                        student_username=student.telegram_username,
                        student_name=student.full_name,
                        message=final_message,
                        message_type="exercise",
                        exercise_id=exercise_id
                    )

                    session.add(pending)

                    history = ExerciseHistory(
                        student_id=student.id,
                        exercise_id=exercise_id
                    )

                    session.add(history)

                    session.commit()

                    session.close()

                    self.status_label.setText(
                        f"Sent to {student.full_name}"
                    )
                
                except Exception as e:
                    self.status_label.setText(
                        f"Failed: {e}"
                    )
                
                return

    
    def finished_generating(self):

        self.status_label.setText("All exercises completed")
    
    def generate_for_student(self, student):

        from ai.engine import generate_exercises

        exercise = generate_exercises(
                subject=student.subject,
                level=student.level,
                student_id=student.id
            )

        if not exercise["ok"]:
            self.status_label.setText(
                exercise["message"]
            )
            return

        self.preview_exercise(
            student,
            exercise
        )
    

    def refresh_streak_columns(self):

        session = Session()

        try:

            students = session.query(Student).all()

            for row, student in enumerate(students):

                # streak
                streak_item = self.table.item(row, 5)

                if streak_item:
                    streak_item.setText(
                        str(student.streak)
                    )
                
                # reset timer
                latest_attempt = (
                    session.query(ExerciseAttempt)
                    .filter_by(
                        student_id=student.id
                    )
                    .order_by(
                        ExerciseAttempt.sent_at.desc()
                    )
                    .first()
                )

                if (
                    latest_attempt
                    and
                    not latest_attempt.streak_awarded
                ):
                    
                    remaining = (
                        latest_attempt.sent_at
                        + timedelta(hours=48)
                        - datetime.utcnow()
                    )

                    total_seconds = max(
                        int(remaining.total_seconds()),
                        0
                    )

                    hours = total_seconds // 3600

                    minutes = (
                        total_seconds % 3600
                    ) // 60

                    seconds = (
                        total_seconds % 60
                    )

                    reset_text = (
                        f"{hours:02d}h "
                        f"{minutes:02d}m "
                        f"{seconds:02d}s"
                    )
                
                else:

                    reset_text = "-"
                

                reset_item = self.table.item(row, 6)

                if reset_item:
                    reset_item.setText(reset_text)
                

                
                # status column
                status_item = self.table.item(row, 7)

                if not status_item:
                    continue
                    
                
                if not latest_attempt:

                    status_item.setText(
                        "No Exercise"
                    )

                    status_item.setBackground(
                        QColor(80, 80, 80)
                    )
                
                elif latest_attempt.streak_awarded:

                    status_item.setText(
                        "Completed"
                    )

                    status_item.setBackground(
                        QColor(0, 120, 0)
                    )
                
                else:

                    status_item.setText(
                        "Waiting"
                    )

                    status_item.setBackground(
                        QColor(120, 0, 0)
                    )
                

        finally:

            session.close()


    def generate_exercise(self):

        from workers.exercise_worker import ExerciseWorker

        self.worker = ExerciseWorker()

        self.worker.exercise_ready.connect(self.preview_exercise)

        self.worker.finished_signal.connect(
            self.finished_generating
        )

        self.worker.start()
    

    def get_selected_student(self):
        row = self.table.currentRow()

        if row == -1:
            return None
        

        student = {
            "id": int(self.table.item(row, 0).text()),
            "full_name": self.table.item(row, 1).text(),
            "telegram_username": self.table.item(row, 2).text(),
            "level": self.table.item(row, 3).text(),
            "subject": self.table.item(row, 4).text(),
            "active": self.table.item(row, 8).text()
        }

        self.on_selected_student(student)

        return student


    def send_idiom(self, student):

        idiom_data = generate_idiom(
            level=student.level,
            student_id=student.id
        )

        if not idiom_data["ok"]:
            
            self.status_label.setText(
                idiom_data["message"]
            )

            return
        

        idiom_id = idiom_data["id"]

        idiom_text = format_message(
            student_id=student.id,
            content=idiom_data["content"],
            template_type="idiom"
        )

        while True:

            preview = PreviewDialog(
                student.full_name,
                idiom_text,
                dialog_type="idiom"
            )

            preview.exec()

            print("ACTION:", preview.action)

            # CANCEL 
            if preview.action == "cancel":
                return
            

            # ANOTHER
            if preview.action == "another":

                idiom_data = generate_idiom(
                    level=student.level,
                    student_id=student.id
                )

                if not idiom_data["ok"]:

                    self.status_label.setText( 
                        idiom_data["message"]
                    )

                    return

                idiom_id = idiom_data["id"]

                idiom_text = format_message(
                    student_id=student.id,
                    content=idiom_data["content"],
                    template_type="idiom"
                )

                continue

            # SEND
            if preview.action == "send":

                final_message = (
                    preview.get_message()
                )

                try:

                    session = Session()

                    pending = PendingMessage(
                        student_id=student.id,
                        student_username=student.telegram_username,
                        student_name=student.full_name,
                        message=final_message,
                        message_type="idiom"
                    )

                    session.add(pending)

                    session.commit()
                    session.close()

                    save_idiom_history(
                        student.id,
                        idiom_id
                    )

                    self.status_label.setText(
                        f"Idiom sent to "
                        f"{student.full_name}"
                    )
                
                except Exception as e:
                    self.status_label.setText(
                        f"Failed: {e}"
                    )
                
                return
                



    
    def message_student(self, student):

        dialog = MessageDialog(
            student.full_name
        )

        result = dialog.exec()

        if not result:
            return
        
        message = dialog.get_message()

        if not message.strip():
            return
        
        try:

            send_message_sync(
                student.telegram_username,
                message
            )

            self.status_label.setText(
                f"Message sent to {student.full_name}"
            )
        
        except Exception as e:
            self.status_label.setText(
                f"Send failed: {e}"
            )
