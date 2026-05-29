from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QWidget,
    QScrollArea,
    QComboBox
)

from PyQt6.QtCore import Qt


class TopicSelectionDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Advanced Exercise Generator"
        )

        self.resize(800, 600)

        main_layout = QVBoxLayout()

        # TITLE

        title = QLabel(
            "Advanced Exercise Generator"
        )

        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 6px;
        """)

        main_layout.addWidget(title)

        # LEVEL

        level_label = QLabel("Difficulty")

        self.level_box = QComboBox()

        self.level_box.addItems([
            "easy",
            "medium",
            "hard"
        ])

        main_layout.addWidget(level_label)
        main_layout.addWidget(self.level_box)

        # SCROLL AREA

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        container = QWidget()

        content_layout = QHBoxLayout()

        left_column = QVBoxLayout()

        right_column = QVBoxLayout()

        # =========================================
        # GRAMMAR
        # =========================================

        self.grammar_list = self.create_list([
            "Present Simple",
            "Present Continuous",
            "Past Simple",
            "Present Perfect",
            "Future Simple",
            "Passive Voice",
            "Conditionals",
            "Reported Speech",
            "Articles",
            "Prepositions"
        ])

        left_column.addWidget(
            QLabel("Grammar Topics")
        )

        left_column.addWidget(
            self.grammar_list
        )

        # =========================================
        # VOCABULARY
        # =========================================

        self.vocabulary_list = self.create_list([
            "Food",
            "Travel",
            "Work",
            "Education",
            "Health",
            "Shopping",
            "Daily Life",
            "Technology",
            "Business",
            "Environment"
        ])

        left_column.addWidget(
            QLabel("Vocabulary Topics")
        )

        left_column.addWidget(
            self.vocabulary_list
        )

        # =========================================
        # EXERCISE TYPES
        # =========================================

        self.exercise_type_list = self.create_list([
            "Translation",
            "Fill in the blanks",
            "Multiple choice",
            "Sentence correction",
            "Dialogue",
            "Error detection",
            "Matching",
            "Short answer"
        ])

        right_column.addWidget(
            QLabel("Exercise Types")
        )

        right_column.addWidget(
            self.exercise_type_list
        )

        # =========================================
        # SKILLS
        # =========================================

        self.skill_list = self.create_list([
            "Reading",
            "Writing",
            "Speaking",
            "Listening",
            "Grammar",
            "Vocabulary"
        ])

        right_column.addWidget(
            QLabel("Skills")
        )

        right_column.addWidget(
            self.skill_list
        )

        # =========================================
        # DIFFICULTY MODIFIERS
        # =========================================

        self.modifier_list = self.create_list([
            "Very Short",
            "Challenging",
            "Exam Style",
            "Conversational",
            "Formal English",
            "Real-life Situations"
        ])

        right_column.addWidget(
            QLabel("Difficulty Modifiers")
        )

        right_column.addWidget(
            self.modifier_list
        )

        # =========================================
        # THEMES
        # =========================================

        self.context_themes = self.create_list([
            "At a Restaurant",
            "At a Hotel",
            "At an Airport",
            "At a Party",
            "At School",
            "At Work",
            "In a Café",
            "In a Supermarket",
            "At the Doctor",
            "On Vacation",
            "During a Job Interview",
            "On the Phone"
        ])

        right_column.addWidget(
            QLabel("Context Themes Themes")
        )

        right_column.addWidget(
            self.theme_list
        )

        # =========================================

        content_layout.addLayout(left_column)

        content_layout.addLayout(right_column)

        container.setLayout(content_layout)

        scroll.setWidget(container)

        main_layout.addWidget(scroll)

        # BUTTONS

        self.generate_button = QPushButton(
            "Generate Controlled Exercise"
        )

        self.cancel_button = QPushButton(
            "Cancel"
        )

        self.generate_button.clicked.connect(
            self.accept
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

        main_layout.addWidget(
            self.generate_button
        )

        main_layout.addWidget(
            self.cancel_button
        )

        self.setLayout(main_layout)

    def create_list(self, items):

        widget = QListWidget()

        for item in items:

            list_item = QListWidgetItem(item)

            list_item.setFlags(
                list_item.flags() |
                Qt.ItemFlag.ItemIsUserCheckable
            )

            list_item.setCheckState(
                Qt.CheckState.Unchecked
            )

            widget.addItem(list_item)

        widget.setMinimumHeight(180)

        return widget

    def get_selected_data(self):

        return {
            "level": (
                self.level_box.currentText()
            ),

            "grammar_topics":
            self.get_checked_items(
                self.grammar_list
            ),

            "vocabulary_topics":
            self.get_checked_items(
                self.vocabulary_list
            ),

            "exercise_types":
            self.get_checked_items(
                self.exercise_type_list
            ),

            "skills":
            self.get_checked_items(
                self.skill_list
            ),

            "difficulty_modifiers":
            self.get_checked_items(
                self.modifier_list
            ),

            "context_themes":
            self.get_checked_items(
                self.context_themes
            )
        }

    def get_checked_items(self, list_widget):

        results = []

        for i in range(list_widget.count()):

            item = list_widget.item(i)

            if (
                item.checkState()
                ==
                Qt.CheckState.Checked
            ):

                results.append(
                    item.text()
                )

        return results