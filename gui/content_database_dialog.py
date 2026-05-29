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

            models = [
                "openrouter/auto",
                "meta-llama/llama-3.3-70b-instruct:free",
                "qwen/qwen3-coder:free",
                "deepseek/deepseek-chat-v3-0324:free"
            ]

            response = None

            last_error = None

            for model_name in models:

                try:

                    print(
                        f"TRYING MODEL: "
                        f"{model_name}"
                    )

                    temp_response = (
                        self.client.chat.completions.create(
                            model=model_name,

                            messages=[
                                {
                                    "role": "user",
                                    "content": self.prompt
                                }
                            ]
                        )
                    )

                    if (
                        temp_response is None
                        or not temp_response.choices
                    ):
                        raise Exception(
                            "Empty AI response"
                        )

                    response = temp_response

                    print(
                        f"SUCCESS: "
                        f"{model_name}"
                    )

                    break

                except Exception as e:

                    print(
                        f"MODEL ERROR: "
                        f"{model_name}"
                    )

                    print(e)

                    last_error = e

            if response is None:

                raise Exception(
                    str(last_error)
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

            models = [
                "openrouter/auto",
                "meta-llama/llama-3.3-70b-instruct:free",
                "qwen/qwen3-coder:free",
                "deepseek/deepseek-chat-v3-0324:free"
            ]

            response = None

            last_error = None

            for model_name in models:

                try:

                    print(
                        f"TRYING MODEL: "
                        f"{model_name}"
                    )

                    temp_response = (
                        self.client.chat.completions.create(
                            model=model_name,

                            messages=[
                                {
                                    "role": "user",
                                    "content": self.prompt
                                }
                            ]
                        )
                    )

                    if (
                        temp_response is None
                        or not temp_response.choices
                    ):
                        raise Exception(
                            "Empty AI response"
                        )
                    
                    
                    response = temp_response

                    print(
                        f"SUCCESS: "
                        f"{model_name}"
                    )

                    break
                
                except Exception as e:

                    print(
                        f"MODEL ERROR: "
                        f"{model_name}"
                    )

                    print(e)

                    last_error = e

            if response is None:

                raise Exception(
                    str(last_error)
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

            session = Session()

            added = 0

            seen_contents = set()

            for item in exercises:

                # HANDLE JSON OBJECTS
                if isinstance(item, dict):
                    
                    content = (
                        f"{item['exercise']}\n\n"
                        f"Options:\n"
                        f"{chr(10).join(item['options'])}\n\n"
                        f"Answer: {item['answer']}" 
                    )
                
                # HANDLE SIMPLE STRING EXERCISES
                else:

                    content = str(item)
                
                # PREVENT SQLALCHEMY AUTOFLUSH CRASH

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
                
                # SKIP IF ALREADY EXISTS IN DATABASE

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
            Generate 30 unique {subject} language-learning exercises.

            Difficulty: {level}

            STUDENT PROFILE:
            - ordinary language learners
            - NOT university students
            - NOT literature students
            - NOT linguistics students
            - exercises must be practical and useful in real life

            IMPORTANT RULES:
            - every exercise MUST be fully self-contained
            - the student must be able to solve it immediately
            - do NOT require external texts
            - do NOT reference books, authors, articles, or essays
            - do NOT generate abstract academic tasks
            - do NOT generate literary analysis
            - do NOT generate rhetorical analysis
            - do NOT generate intertextual analysis
            - do NOT generate philosophy questions
            - do NOT generate exercises without context
            - do NOT generate vague instructions

            ALLOWED EXERCISE TYPES:
            - fill in the blank
            - translation
            - sentence correction
            - choose the correct word
            - verb conjugation
            - short dialogue completion
            - vocabulary practice
            - grammar practice
            - word order
            - question formation
            - prepositions
            - articles
            - tenses
            - everyday conversation

            STYLE RULES:
            - Telegram friendly
            - concise
            - practical
            - easy to read
            - max 3 short lines per exercise
            - all exercises different

            GOOD EXAMPLE:
            "Fill in the blank:
            Yesterday I ___ to school.
            (a) go
            (b) went
            (c) gone
            (d) will
            "

            BAD EXAMPLE:
            "Identify and interpret the author's intertextual references."

            Every exercise must include enough information
            for the student to answer without additional explanation.
            Each exercise must start with:

            - Translate:
            - Fill in the blank:
            - Correct the mistake:
            - Choose the correct option:

            Return ONLY valid JSON array.

            Example:
            [
                "Translate:\\nI am hungry.",
                "Fill in the blank:\\nShe ___ to school every day."
            ]
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
    
        