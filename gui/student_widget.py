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

from datetime import datetime, timedelta, time, date

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
from services.logger import logger



class StudentWidget(QWidget):
    def __init__(self, on_selected_student, on_status=None):
        super().__init__()

        self.on_selected_student = on_selected_student
        self.on_status = on_status or (lambda message, level="INFO": None)

        self.layout = QVBoxLayout()

        title = QLabel("Students")

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
            logger.info(f"ERROR: {e}")
        
    def _notify_status(self, message, level="INFO"):
            self.on_status(message, level)
    

    def _day_bounds(self, day: date):
        start = datetime.combine(day, time.min)
        end = start + timedelta(days=1)
        return start, end
    
    def _attempts_sent_on_day(self, session, student_id: int, day:date):
        start, end = self._day_bounds(day)
        return (
            session.query(ExerciseAttempt)
            .filter(
                ExerciseAttempt.student_id == student_id,
                ExerciseAttempt.sent_at >= start,
                ExerciseAttempt.sent_at < end,
            )
            .order_by(ExerciseAttempt.sent_at.asc())
            .all()
        )
    
    def _build_reset_text(self, session, student):
        """
        Show 48h countdown if ANY exercise still waiting for 💯.
        For multi-exercise students, use the oldest unapproved attempt.
        """

        unapproved = (
            session.query(ExerciseAttempt)
            .filter_by(
                student_id=student.id,
                streak_awarded=False,
                reset_processed=False,
            )
            .order_by(ExerciseAttempt.sent_at.asc())
            .first()
        )

        if not unapproved:
            return "-"
        
        remaining = (
            unapproved.sent_at
            + timedelta(hours=48)
            - datetime.utcnow()
        )

        total_seconds = max(int(remaining.total_seconds()), 0)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f"{hours:02d}h {minutes:02d}m {seconds:02d}s"



    def _build_progress_status(self, session, student):
        """
        Returns (text, background_color)
        """
        exercises_per_day = getattr(student, "exercises_per_day", 1) or 1
        today = datetime.utcnow().date()

        if exercises_per_day <= 1:
            latest_attempt = (
                session.query(ExerciseAttempt)
                .filter_by(student_id=student.id)
                .order_by(ExerciseAttempt.sent_at.desc())
                .first()
            )

            if not latest_attempt:
                return "No Exercise", QColor(80, 80, 80)
            
            if latest_attempt.streak_awarded:
                return "Completed", QColor(0, 120, 0)
            
            return "Waiting", QColor(120, 0, 0)
        
        # Multi-exercise student

        todays_attempts = self._attempts_sent_on_day(
            session, 
            student.id,
            today,
        )

        if not todays_attempts:
            return "No Exercise Today", QColor(80, 80, 80)
        
        approved = sum(1 for a in todays_attempts if a.streak_awarded)
        total = len(todays_attempts)

        if (
            approved == total
            and getattr(student, "last_streak_credit_date", None) == today
        ):
            return "Day Complete", QColor(0, 120, 0)
        
        if approved == total:
            return f"{approved}/{total} Today", QColor(120, 90, 0)

        return f"{approved}/{total} Today", QColor(120, 90,0)




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

            reset_text = self._build_reset_text(session, student)

            self.table.setItem(
                row,
                6, 
                QTableWidgetItem(reset_text)
            )
            progress_text, progress_color = self._build_progress_status(
                session,
                student
            )

            status_item = QTableWidgetItem(progress_text)
            status_item.setBackground(progress_color)

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

            daily_send_times=data["daily_send_times"],

            exercises_per_day=data["exercises_per_day"],

            active=data["active"],

            streak=data["streak"],
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

            student.daily_send_times = data["daily_send_times"]

            student.exercises_per_day = data["exercises_per_day"]

            student.daily_send_time = (
                data["daily_send_time"]
            )

            student.active = (
                data["active"]
            )

            student.streak = data["streak"]

            if data["mark_today_approved"]:
                today = datetime.utcnow().date()
                start = datetime.combine(today, time.min)
                end = start + timedelta(days=1)

                todays_attempts = (
                    session.query(ExerciseAttempt)
                    .filter(
                        ExerciseAttempt.student_id == student.id,
                        ExerciseAttempt.sent_at >= start,
                        ExerciseAttempt.sent_at < end,
                    )
                    .all()
                )

                for attempt in todays_attempts:
                    attempt.streak_awarded  = True
                
                exercises_per_day = (
                    getattr(student, "exercises_per_day", 1) or 1
                )

                if (
                    todays_attempts
                    and len(todays_attempts) >= exercises_per_day
                    and all(a.streak_awarded for a in todays_attempts)
                ):
                    
                    student.last_streak_credit_date = today
                    student.last_approved_exercise_at = datetime.utcnow()

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

            self._notify_status("Telegram sync completed")
        
        except Exception as e:

            self._notify_status(
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

                    self._notify_status(
                        exercise_data["message"],
                        "WARNING",

                    )

                    return

                exercise_id = (
                    exercise_data["id"]
                )

                raw_content = exercise_data["content"]

                exercise_text = format_message(
                    student_id=student.id,
                    content=raw_content,
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
                
                logger.info(
                    f"SELECTED TOPIC DATA: {selected_data}"
                )

                self._notify_status(
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

                    self._notify_status(
                        f"Sent to {student.full_name}"
                    )
                
                except Exception as e:
                    self._notify_status(
                        f"Failed: {e}",
                        "ERROR",
                    )
                
                return

    
    def finished_generating(self):

        self._notify_status("All exercises completed")
    
    def generate_for_student(self, student):

        from ai.engine import generate_exercises

        exercise = generate_exercises(
                subject=student.subject,
                level=student.level,
                student_id=student.id
            )

        if not exercise["ok"]:
            self._notify_status(
                exercise["message"],
                "WARNING"
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
                
                reset_text = self._build_reset_text(session, student)

                reset_item = self.table.item(row, 6)

                if reset_item:
                    reset_item.setText(reset_text)
                
                progress_text, progress_color = self._build_progress_status(
                    session,
                    student,
                )
                
                status_item = self.table.item(row, 7)
                if not status_item:
                    continue
                status_item.setText(progress_text)
                status_item.setBackground(progress_color)

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
            
            self._notify_status(
                idiom_data["message"],
                "WARNING"
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

            logger.info(f"ACTION: {preview.action}")

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

                    self._notify_status( 
                        idiom_data["message"],
                        "WARNING",
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

                    self._notify_status(
                        f"Idiom sent to "
                        f"{student.full_name}"
                    )
                
                except Exception as e:
                    self._notify_status(
                        f"Failed: {e}",
                        "ERROR",
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
        
        except Exception as e:
            self._notify_status(
                f"Send failed: {e}",
                "ERROR",
            )
