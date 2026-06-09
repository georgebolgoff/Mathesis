import json
import os
import traceback
from PyQt6.QtWidgets import (
        QDialog, 
        QVBoxLayout, 
        QLabel, 
        QComboBox,
        QStackedWidget,
        QWidget,
        QTextEdit,
        QPushButton,
        QTableWidget,
        QTableWidgetItem,
            )

from PyQt6.QtCore import (
        QThread,
        QObject,
        pyqtSignal
)
from database.db import Session
from database.models import Exercise, Idiom, MessageTemplate
from openai import OpenAI
from dotenv import load_dotenv
from config.models import EXERCISE_MODEL, IDIOM_MODEL

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


class IdiomGeneratorWorker(QObject):

    finished = pyqtSignal()
    error = pyqtSignal(str)
    success = pyqtSignal(int)

    def __init__(self, level, prompt, client):

        super().__init__()

        self.level = level
        self.prompt = prompt
        self.client = client

    def run(self):

        try:

            print(
                f"USING IDIOM MODEL: "
                f"{IDIOM_MODEL}"
            )

            response = (
                self.client.chat.completions.create(
                    model=IDIOM_MODEL,
                    max_tokens=4000,
                    messages=[
                        {
                            "role": "user",
                            "content": self.prompt
                        }
                    ]
                )
            )


            raw_text = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )

            raw_text = (
                raw_text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            parsed = json.loads(raw_text)

            if isinstance(parsed, dict):

                idioms = parsed.get(
                    "idioms",
                    []
                )

            else:

                idioms = parsed

            session = Session()

            added = 0

            for item in idioms:

                if isinstance(item, dict):

                    content = item["content"]

                else:

                    content = str(item)

                exists = (
                    session.query(Idiom)
                    .filter_by(
                        content=content,
                        level=self.level
                    )
                    .first()
                )

                if exists:
                    continue

                idiom = Idiom(
                    level=self.level,
                    content=content
                )

                session.add(idiom)

                added += 1

            session.commit()

            session.close()

            self.success.emit(added)

        except Exception as e:

            traceback.print_exc()

            self.error.emit(str(e))

        finally:

            self.finished.emit()
        


class ExerciseGeneratorWorker(QObject):

    finished = pyqtSignal()
    error = pyqtSignal(str)
    success = pyqtSignal(int)

    def __init__(
            self,
            subject,
            level,
            prompt,
            client
    ):
        
        super().__init__()

        self.subject = subject
        self.level = level
        self.prompt = prompt
        self.client = client

    def run(self):

        try:

            print(
                f"USING EXERCISE MODEL: {EXERCISE_MODEL} "
            )

            response = (
                
                self.client.chat.completions.create(
                    model=EXERCISE_MODEL,
                    max_tokens=4000,
                    messages=[
                        {
                            "role": "user",
                            "content": self.prompt
                        }
                    ]
                )
            )
            
            raw_text = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )

            raw_text = (
                raw_text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            exercises = json.loads(raw_text)

            print(json.dumps(exercises[:3], indent=2))

            session = Session()

            added = 0

            seen_contents = set()

            for item in exercises:

                # JSON OBJECT FORMAT
                if isinstance(item, dict):

                    content = item.get(
                        "exercise",
                        str(item)
                    )

                    if item.get("options"):

                        content += (
                            "\n\nOptions:\n"
                            + "\n".join(item["options"])
                        )

                    if item.get("answer"):

                        content += (
                            f"\n\nAnswer: "
                            f"{item['answer']}"
                        )

                # SIMPLE STRING FORMAT
                else:

                    content = str(item)

                with session.no_autoflush:

                    exists = (
                        session.query(Exercise)
                        .filter_by(
                            content=content,
                            subject=self.subject,
                            level=self.level
                        )
                        .first()
                    )

                if exists:
                    continue

                exercise = Exercise(
                    subject=self.subject,
                    level=self.level,
                    content=content
                )

                session.add(exercise)

                added += 1
            
            session.commit()

            session.close()

            self.success.emit(added)
        except Exception as e:

            traceback.print_exc()

            self.error.emit(str(e))
        
        finally:

            self.finished.emit()
            


                



class ContentDatabaseDialog(QDialog):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Content Database Manager")
        self.resize(900, 600)

        self.layout = QVBoxLayout()

        # TITLE 
        self.title = QLabel("Content Database Manager")

        # DATABASE SELECTOR (IMPORTANT CORE FEATURE)
        self.database_selector = QComboBox()
        self.database_selector.addItems([
            "Exercises",
            "Idioms",
            "Message Templates"
        ])


        self.database_selector.currentTextChanged.connect(
            self.on_database_changed
        )

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.database_selector)


        self.setLayout(self.layout)


        self.content_stack = QStackedWidget()
        self.layout.addWidget(self.content_stack)


        self.exercises_page = QWidget()
        self.idioms_page = QWidget()
        self.templates_page = QWidget()

        self.load_exercises_ui()
        self.load_idioms_ui()
        self.load_templates_ui()


        self.content_stack.addWidget(self.exercises_page)
        self.content_stack.addWidget(self.idioms_page)
        self.content_stack.addWidget(self.templates_page)

        # initial load
        self.on_database_changed("Exercises")
    

    def on_database_changed(self, value):

        if value == "Exercises":
            self.content_stack.setCurrentWidget(self.exercises_page)
         
        elif value == "Idioms":
            self.content_stack.setCurrentWidget(self.idioms_page)
        
        elif value == "Message Templates":

            self.content_stack.setCurrentWidget(
                self.templates_page
            )
    
    def load_exercises_ui(self):
        if self.exercises_page.layout() is not None:
            return
        
        layout = QVBoxLayout()

        self.exercise_prompt = QTextEdit()

        self.exercise_subject = QComboBox()
        self.exercise_subject.addItems([
            "english",
            "french",
            "russian"
        ])

        self.exercise_level = QComboBox()
        self.exercise_level.addItems([
            "easy",
            "medium",
            "hard"
        ])

        self.exercise_subject.currentTextChanged.connect(
            self.update_exercise_prompt
        )

        self.exercise_level.currentTextChanged.connect(
            self.update_exercise_prompt
        )

        self.update_exercise_prompt()

        self.exercise_table = QTableWidget()

        self.exercise_table.setColumnCount(4)

        self.exercise_table.setHorizontalHeaderLabels([
            "ID",
            "Subject",
            "Level",
            "Content"
        ])
        self.exercise_generate = QPushButton("Generate Exercises")
        self.exercise_clear = QPushButton("Clear Database")

        self.exercise_generate.clicked.connect(self.generate_exercises)
        self.exercise_clear.clicked.connect(self.clear_exercises)

        layout.addWidget(QLabel("Subject"))
        layout.addWidget(self.exercise_subject)

        layout.addWidget(QLabel("Level"))
        layout.addWidget(self.exercise_level)

        layout.addWidget(QLabel("Exercise Prompt"))
        layout.addWidget(self.exercise_prompt)
        layout.addWidget(self.exercise_generate)
        layout.addWidget(self.exercise_clear)
        layout.addWidget(self.exercise_table)

        self.exercises_page.setLayout(layout)

        self.load_exercises_table()
    

    def load_exercises_table(self):

        session = Session()

        exercises = session.query(Exercise).all()

        self.exercise_table.setRowCount(len(exercises))

        for row, exercise in enumerate(exercises):

            self.exercise_table.setItem(
                row,
                0,
                QTableWidgetItem(str(exercise.id))
            )

            self.exercise_table.setItem(
                row,
                1,
                QTableWidgetItem(exercise.subject)
            )

            self.exercise_table.setItem(
                row,
                2,
                QTableWidgetItem(exercise.level)
            )

            self.exercise_table.setItem(
                row,
                3,
                QTableWidgetItem(exercise.content)
            )

        session.close()
    

    def load_idioms_table(self):

        session = Session()

        idioms = session.query(Idiom).all()

        self.idiom_table.setRowCount(
            len(idioms)
        )

        for row, idiom in enumerate(idioms):

            self.idiom_table.setItem(
                row,
                0,
                QTableWidgetItem(str(idiom.id))
            )

            self.idiom_table.setItem(
                row,
                1,
                QTableWidgetItem(idiom.level)
            )

            self.idiom_table.setItem(
                row,
                2,
                QTableWidgetItem(idiom.content)
            )

        session.close()

    

    def update_exercise_prompt(self):

        subject = self.exercise_subject.currentText()
        level = self.exercise_level.currentText()

        prompt = f"""
                    You are an expert {subject} teacher and curriculum designer.

                    Create a HIGH-DIVERSITY exercise database.

                    Generate EXACTLY 50 unique {subject} exercises.

                    Difficulty level:
                    {level}

                    IMPORTANT STUDENT PROFILE

                    Assume all students are native Russian speakers learning {subject}.

                    Exercises may use Russian when appropriate for translation tasks.

                    Do NOT use Spanish, German, Italian, Portuguese, or other foreign languages unless the selected subject itself requires them.

                    The goal is maximum variety and zero repetition.

                    ==================================================
                    EXERCISE PHILOSOPHY
                    ==================================================

                    Students should spend most of their time:

                    - choosing correct answers
                    - finding mistakes
                    - correcting mistakes
                    - selecting between alternatives
                    - translating sentences
                    - completing realistic dialogues
                    - identifying grammar errors
                    - identifying vocabulary errors
                    - rewriting sentences
                    - matching expressions with meanings

                    Avoid exercises where students invent large amounts of content themselves.

                    Avoid vague open-ended tasks.

                    Avoid exercises that depend on general knowledge.

                    Avoid questions that can be answered without using language skills.

                    BAD EXAMPLES:

                    "Where did you go on holiday?"

                    "What direction does the sun set?"

                    "Write a paragraph about your favorite animal."

                    "Tell us your opinion about technology."

                    "Complete the conversation with your own answer."

                    "Describe your dream vacation."

                    GOOD EXAMPLES:

                    Choose the correct verb.

                    Find the mistake.

                    Correct the sentence.

                    Choose the correct translation.

                    Select the best option.

                    Rewrite the sentence using Present Perfect.

                    Choose the correct preposition.

                    Identify the incorrect word.

                    Translate from Russian to {subject}.

                    Translate from {subject} to Russian.

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
                    - Multiple Choice
                    - Error Detection
                    - Sentence Correction
                    - Translation
                    - Fill in the Blank
                    - Dialogue Completion
                    - Matching
                    - Rewrite Sentences
                    - Choose the Correct Option
                    - Identify the Mistake

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

                    ==================================================
                    LEVEL RULES
                    ==================================================

                    For EASY:
                    - short sentences
                    - common vocabulary
                    - simple grammar
                    - no advanced conditionals
                    - no rare words
                    - no academic language

                    For MEDIUM:
                    - everyday real-world language
                    - moderate grammar complexity
                    - realistic conversations
                    - practical vocabulary

                    For HARD:
                    - advanced grammar
                    - nuanced vocabulary
                    - professional situations
                    - more complex sentence structures

                    ==================================================
                    DIVERSITY MATRIX RULE
                    ==================================================

                    Every exercise must combine different dimensions.

                    Examples:

                    Travel + Multiple Choice + Airport

                    Food + Error Detection + Restaurant

                    Technology + Vocabulary + Workplace

                    Present Perfect + Correction + Job Interview

                    Reported Speech + Translation + Phone Call

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

                    The exercise itself must contain enough information to solve it.

                    Do NOT create trivia questions.

                    Do NOT create geography questions.

                    Do NOT create science questions.

                    Do NOT create general knowledge questions.

                    Do NOT create opinion questions.

                    Do NOT create creative writing tasks.

                    Focus on language learning only.

                    The categories used to generate exercises are INTERNAL ONLY.

                    Grammar topics, vocabulary topics, skills, exercise types, context themes, difficulty dimensions, and diversity combinations must NEVER appear in the final exercise text.

                    Do NOT append labels such as:

                    (Travel)
                    (Grammar)
                    (Vocabulary)
                    (Restaurant)
                    (Airport)
                    (Matching)
                    (Translation)
                    (Present Perfect)
                    (Context - Hotel)
                    (Difficulty: Medium)

                    Do NOT place metadata in:

                    parentheses
                    brackets
                    prefixes
                    suffixes
                    tags
                    labels

                    BAD:

                    "Match the phrase 'check in' with its context: (a) hotel, (b) restaurant. (Travel, Hotel, Matching)"

                    "Choose the correct verb. (Present Perfect, Job Interview)"

                    "Translate into English. [Travel]"

                    GOOD:

                    "Match the phrase 'check in' with its context:
                    (a) hotel
                    (b) restaurant"

                    "Choose the correct verb:
                    I ___ for three companies before joining this one.
                    (worked / have worked)"

                    "Translate into English:
                    Я приехал в аэропорт слишком рано."

                    Exercises must look exactly like real exercises written by a teacher.

                    The student should never see which categories, dimensions, themes, or combinations were used to generate the exercise.

                    Each JSON item must contain ONLY the exercise itself.

                    Do NOT include:

                    explanations
                    answers
                    category names
                    topic names
                    metadata
                    tags
                    labels
                    difficulty indicators
                    generation notes

                    Return clean student-facing exercises only.


                    Every exercise must be:

                    Telegram friendly
                    concise
                    practical
                    realistic
                    useful for language learning
                    self-contained
                    clear and unambiguous

                    The exercise itself must contain enough information to solve it.

                    Do NOT create trivia questions.

                    Do NOT create geography questions.

                    Do NOT create science questions.

                    Do NOT create general knowledge questions.

                    Do NOT create opinion questions.

                    Do NOT create creative writing tasks.

                    Focus on language learning only.

                    MULTIPLE CHOICE REQUIREMENTS

                    Whenever an exercise requires choosing an answer, selecting an option, identifying the correct answer, or multiple-choice selection:

                    provide AT LEAST 5 answer options
                    5 to 8 options is preferred
                    all options must be plausible
                    avoid obviously wrong distractors
                    avoid joke answers
                    avoid duplicate options

                    BAD:

                    Choose the correct answer:
                    (a) go
                    (b) goes

                    GOOD:

                    Choose the correct answer:
                    (a) go
                    (b) goes
                    (c) going
                    (d) gone
                    (e) to go


                    ==================================================
                    OUTPUT FORMAT
                    ==================================================

                    Return ONLY a valid JSON array.

                    Example:

                    [
                        "Choose the correct option: She ___ to work every day. (go/goes)",
                        "Find the mistake: He don't like coffee.",
                        "Translate into English: Я купил новую машину вчера."
                    ]

                    No explanations.

                    No answers.

                    No numbering.

                    No markdown.

                    Return JSON only.
                    """
        self.exercise_prompt.setPlainText(prompt.strip())

    

    def update_idiom_prompt(self):

        level = self.idiom_level.currentText()

        prompt = f"""
            Generate 30 unique English idioms.

            Difficulty: {level}

            Rules:
            - suitable for English learners
            - Telegram friendly
            - concise
            - include meaning
            - include example sentence
            - all idioms different

            Return ONLY valid JSON array.

            Example:
            [
                {{
                    "content":
                    "Break the ice\\n\\n"
                    "Meaning: start conversation.\\n\\n"
                    "Example: He told a joke to break the ice."
                }}
            ]
            """

        self.idiom_prompt.setPlainText(
            prompt.strip()
        )

    
    def load_idioms_ui(self):
        if self.idioms_page.layout() is not None:
            return 

        layout = QVBoxLayout()

        self.idiom_prompt = QTextEdit()

        self.idiom_level = QComboBox()

        self.idiom_level.addItems([
            "easy",
            "medium",
            "hard"
        ])

        self.idiom_level.currentTextChanged.connect(
            self.update_idiom_prompt
        )

        self.update_idiom_prompt()

        self.idiom_table = QTableWidget()

        self.idiom_table.setColumnCount(3)

        self.idiom_table.setHorizontalHeaderLabels([
            "ID",
            "Level",
            "Content"
        ])

        self.idiom_generate = QPushButton(
            "Generate Idioms"
        )

        self.idiom_clear = QPushButton(
            "Clear Idioms"
        )

        self.idiom_generate.clicked.connect(
            self.generate_idioms
        )

        self.idiom_clear.clicked.connect(
            self.clear_idioms
        )

        layout.addWidget(QLabel("Level"))
        layout.addWidget(self.idiom_level)

        layout.addWidget(QLabel("Idiom Prompt"))
        layout.addWidget(self.idiom_prompt)

        layout.addWidget(self.idiom_generate)
        layout.addWidget(self.idiom_clear)

        layout.addWidget(self.idiom_table)

        self.idioms_page.setLayout(layout)
    

    def load_templates_ui(self):

        if self.templates_page.layout() is not None:
            return
        
        layout = QVBoxLayout()

        # TABLE

        self.templates_table = QTableWidget()

        self.templates_table.setColumnCount(3)

        self.templates_table.setHorizontalHeaderLabels([
            "ID",
            "Template Type",
            "Template Text"
        ])

        # EDITOR

        self.template_editor = QTextEdit()

        # BUTTONS

        self.save_template_button = QPushButton(
            "Save Template"
        )

        self.reload_template_button = QPushButton(
            "Reload Templates"
        )

        # CONNECTIONS 

        self.templates_table.itemSelectionChanged.connect(
            self.load_selected_template
        )

        self.save_template_button.clicked.connect(
            self.save_selected_template
        )

        self.reload_template_button.clicked.connect(
            self.load_templates_table
        )

        # LAYOUT

        layout.addWidget(
            QLabel("Message Templates")
        )

        layout.addWidget(
            self.templates_table
        )

        layout.addWidget(
            QLabel("Template Editor")
        )

        layout.addWidget(
            self.template_editor
        )

        layout.addWidget(
            self.save_template_button
        )

        layout.addWidget(
            self.reload_template_button
        )

        self.templates_page.setLayout(layout)

        self.load_templates_table()
    

    def load_templates_table(self):

        session = Session()

        templates = session.query(MessageTemplate).all()

        self.templates_table.setRowCount(len(templates))

        for row, template in enumerate(templates):

            self.templates_table.setItem(
                row,
                0,
                QTableWidgetItem(str(template.id))
            )

            self.templates_table.setItem(
                row,
                1,
                QTableWidgetItem(template.template_type)
            )

            self.templates_table.setItem(
                row,
                2,
                QTableWidgetItem(template.template_text)
            )

        session.close()
    

    def load_selected_template(self):

        selected_row = self.templates_table.currentRow()

        if selected_row == -1:
            return
        
        template_text = self.templates_table.item(selected_row, 2).text()

        self.template_editor.setPlainText(template_text)
    

    def save_selected_template(self):

        selected_row = self.templates_table.currentRow()

        if selected_row == -1:
            return
        
        template_id = int(
            self.templates_table.item(selected_row, 0).text()
        )

        new_text = self.template_editor.toPlainText()

        session = Session()

        template = session.get(MessageTemplate, template_id)

        if not template:
            session.close()
            return

        template.template_text = new_text

        session.commit()
        session.close()

        self.load_templates_table()


    
    def generate_exercises(self):

        subject = (
            self.exercise_subject
            .currentText()
        )

        level = (
            self.exercise_level
            .currentText()
        )

        prompt = (
            self.exercise_prompt
            .toPlainText()
        )

        self.exercise_generate.setEnabled(False)

        self.exercise_generate.setText(
            "Generating..."
        )

        self.exercise_thread = QThread()

        self.exercise_worker = (
            ExerciseGeneratorWorker(
                subject=subject,
                level=level,
                prompt=prompt,
                client=client
            )
        )

        self.exercise_worker.moveToThread(
            self.exercise_thread
        )
        
        self.exercise_thread.started.connect(
            self.exercise_worker.run
        )

        self.exercise_worker.success.connect(
            self.on_exercises_generated
        )

        self.exercise_worker.finished.connect(
            self.exercise_thread.quit
        )

        self.exercise_thread.finished.connect(
            self.exercise_worker.deleteLater
        )

        self.exercise_thread.finished.connect(
            self.on_exercise_generation_finished
        )

        self.exercise_thread.start()





    def generate_idioms(self):

        level = (
            self.idiom_level
            .currentText()
        )

        prompt = (
            self.idiom_prompt
            .toPlainText()
        )

        self.idiom_generate.setEnabled(False)
        self.idiom_generate.setText(
            "Generating..."
        )

        self.thread = QThread()

        self.worker = IdiomGeneratorWorker(
            level=level,
            prompt=prompt,
            client=client
        )

        self.worker.moveToThread(
            self.thread
        )

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.success.connect(
            self.on_idioms_generated
        )

        self.worker.error.connect(
            self.on_generation_error
        )

        self.worker.finished.connect(
            self.thread.quit
        )

        self.worker.finished.connect(
            self.worker.deleteLater
        )

        self.thread.finished.connect(
            self.thread.deleteLater
        )

        self.thread.finished.connect(
            self.on_generation_finished
        )

        self.thread.start()
    
    def on_idioms_generated(self, added):

        print(
            f"{added} idioms added"
        )

        self.load_idioms_table()
    

    def on_exercises_generated(self, added):

        print(
            f"{added} exercises added"
        )

        self.load_exercises_table()
    

    def on_exercise_generation_finished(self):

        self.exercise_generate.setEnabled(True)


        self.exercise_generate.setText(
            "Generate Exercises"
        )


    def on_generation_error(self, message):

        print(
            "IDIOM GENERATION ERROR:",
            message
        )


    def on_generation_finished(self):

        self.idiom_generate.setEnabled(True)

        self.idiom_generate.setText(
            "Generate Idioms"
        )

    def clear_exercises(self):

        session = Session()

        session.query(Exercise).delete()

        session.commit()

        session.close()

        self.load_exercises_table()
    

    def clear_idioms(self):

        session = Session()

        session.query(Idiom).delete()

        session.commit()

        session.close()

        self.load_idioms_table()  
    
        