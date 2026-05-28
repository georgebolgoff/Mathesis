from PyQt6.QtCore import QThread, pyqtSignal
from database.db import Session
from database.models import Student

from ai.engine import generate_exercises

import random

import time 


class ExerciseWorker(QThread):

    exercise_ready = pyqtSignal(object, object)
    finished_signal = pyqtSignal()

    def run(self):
        session = Session()

        students = session.query(Student).all()

        for student in students:
            if not student.active:
                continue

            try:

                exercise = generate_exercises(
                    subject=student.subject,
                    level=student.level,
                    student_id=student.id
                )

                self.exercise_ready.emit(
                    student,
                    exercise
                )
                time.sleep(1)
            
            except Exception as e:
                print(f"Generation failed: {e}")

        session.close()

        self.finished_signal.emit()

