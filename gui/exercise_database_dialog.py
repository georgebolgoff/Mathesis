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
            "A1",
            "A2",
            "B1",
            "B2",
            "C1",
            "C2"
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
                You are an expert {subject} teacher and curriculum designer.

                Create a HIGH-DIVERSITY exercise database.

                Generate EXACTLY 50 unique {subject} exercises.

                CEFR Level:
                {level}

                Level definitions:

                A1:
                Very basic language.
                Simple vocabulary.
                Short sentences.

                A2:
                Basic everyday communication.
                Simple grammar.

                B1:
                Intermediate communication.
                Daily situations.
                Moderate complexity.

                B2:
                Upper intermediate.
                More abstract topics.
                Longer texts.

                C1:
                Advanced language use.
                Professional and academic contexts.

                C2:
                Near-native proficiency.
                Complex vocabulary.
                Nuanced language.

                The goal is maximum variety and zero repetition.

                ==================================================
                DIVERSITY REQUIREMENTS
                ==================================================

                Distribute exercises across these categories:

                Grammar:
                - Present Simple
                - Present Continuous
                - Past Simple
                - Present Perfect
                - Future Simple
                - Passive Voice
                - Conditionals
                - Reported Speech
                - Articles
                - Prepositions

                Vocabulary:
                - Food
                - Travel
                - Work
                - Education
                - Health
                - Shopping
                - Daily Life
                - Technology
                - Business
                - Environment

                Skills:
                - Reading
                - Writing
                - Speaking
                - Grammar
                - Vocabulary

                Exercise Types:
                - Translation
                - Fill in the blanks
                - Multiple Choice
                - Sentence Correction
                - Dialogue Completion
                - Error Detection
                - Matching
                - Short Answer
                - Sentence Building
                - Rewrite Sentences

                Context Themes:
                - Restaurant
                - Hotel
                - Airport
                - School
                - Workplace
                - Café
                - Supermarket
                - Doctor Visit
                - Vacation
                - Job Interview
                - Phone Call
                - Daily Conversation

                Difficulty Modifiers:
                - Very Short
                - Challenging
                - Exam Style
                - Conversational
                - Formal English
                - Real-Life Situations

                ==================================================
                DIVERSITY MATRIX RULE
                ==================================================

                Every exercise must combine different dimensions.

                Examples:

                Travel + Dialogue + Speaking + Airport

                Food + Multiple Choice + Vocabulary + Restaurant

                Technology + Reading + Business + Workplace

                Conditionals + Writing + Vacation

                Present Perfect + Error Detection + Job Interview

                No two exercises may use the same combination.

                ==================================================
                ANTI-REPETITION RULES
                ==================================================

                Avoid:

                - duplicate topics
                - duplicate wording
                - duplicate exercise structures
                - duplicate question formats
                - duplicate vocabulary sets
                - duplicate grammar patterns

                Every exercise must feel different from the previous ones.

                ==================================================
                EXERCISE DISTRIBUTION
                ==================================================

                Ensure a balanced mixture of:

                Grammar-focused exercises
                Vocabulary-focused exercises
                Reading exercises
                Writing exercises
                Speaking exercises

                Ensure a balanced mixture of:

                Translation
                Dialogue
                Fill in the blanks
                Multiple choice
                Matching
                Correction
                Short answer
                Sentence building

                ==================================================
                CURRICULUM DESIGN
                ==================================================

                Design the 50 exercises as if they belong to a professional language-learning curriculum.

                Progress naturally across the exercise set.

                Mix easy and challenging thinking tasks while respecting overall difficulty level "{level}".

                ==================================================
                QUALITY RULES
                ==================================================

                Every exercise must be:

                - Telegram friendly
                - concise
                - practical
                - realistic
                - useful for language learning
                - self-contained
                - clear and unambiguous

                No explanations.
                No answers.
                No numbering.

                ==================================================
                OUTPUT FORMAT
                ==================================================

                Return ONLY a valid JSON array.

                Example:

                [
                "Exercise text",
                "Exercise text",
                "Exercise text"
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

