from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QComboBox,
    QMessageBox
)

from database.db import Session
from database.models import Exercise

from services.exercise_refill_service import refill_exercises

class ExerciseDatabaseDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Exercise Database Manager")

        self.resize(700, 600)

        layout = QVBoxLayout()

        # SUBJECT

        layout.addWidget(QLabel("Subject"))

        self.subject_box = QComboBox()

        self.subject_box.addItems([
            "math",
            "english",
            "coding"
        ])

        layout.addWidget(self.subject_box)


        # LEVEL

        layout.addWidget(QLabel("Difficulty"))

        self.level_box = QComboBox()

        self.level_box .addItems([
            "easy",
            "medium",
            "hard"
        ])

        layout.addWidget(
            self.level_box
        )

        # PROMPT 

        layout.addWidget(
            QLabel("AI Prompt")
        )

        self.prompt_editor = QTextEdit()

        self.prompt_editor.setPlainText(
            self.build_default_prompt()
        )

        layout.addWidget(
            self.prompt_editor
        )

        # BUTTONS

        self.generate_button = QPushButton("Generate Exercises")
        self.clear_button = QPushButton("Clear Database Section")

        layout.addWidget(
            self.generate_button
        )

        layout.addWidget(
            self.clear_button
        )

        self.setLayout(layout)

        # SIGNALS

        self.subject_box.currentTextChanged.connect(
            self.update_prompt
        )

        self.level_box.currentTextChanged.connect(
            self.update_prompt
        )

        self.generate_button.clicked.connect(
            self.generate_exercise
        )

        self.clear_button.clicked.connect(
            self.clear_exercises
        )
    

    def build_default_prompt(self):
        subject = (
            self.subject_box.currentText()
        )

        level = (
            self.level_box.currentText()
        )

        return f"""
Generate 30 unique {subject} exercises.

Difficulty: {level}

Rules:
- concise
- Telegram friendly
- no explanations
- all exercises different

Return ONLY valid JSON array.

Example:
[
  "Exercise 1",
  "Exercise 2"
]
"""
    
    def update_prompt(self):
        self.prompt_editor.setPlainText(
            self.build_default_prompt()
        )
    
    def generate_exercise(self):

        subject = (
            self.subject_box.currentText()
        )

        level = (
            self.level_box.currentText()
        )

        prompt = (
            self.prompt_editor.toPlainText()
        )

        try:

            refill_exercises(
                subject,
                level,
                custom_prompt=prompt
            )

            QMessageBox.information(
                self,
                "Success",
                "Exercises generated"
            )

        except Exception as e:
             QMessageBox.warning(
                 self,
                 "Error",
                 str(e)
             )
    

    def clear_exercises(self):

        subject = (
            self.subject_box.currentText()
        )

        level = (
            self.level_box.currentText()
        )

        session = Session()

        (
            session.query(Exercise)
            .filter_by(
                subject=subject,
                level=level
            )
            .delete()
        )

        session.commit()

        session.close()

        QMessageBox.information(
            self,
            "Success",
            "Exercises deleted"
        )

