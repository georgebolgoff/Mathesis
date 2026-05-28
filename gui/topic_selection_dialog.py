from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QWidget,
    QCheckBox,
    QGroupBox,
    QGridLayout,
    QComboBox,
    QHBoxLayout
)

from ai.topic_taxonomy import (
    GRAMMAR_TOPICS,
    VOCABULARY_TOPICS,
    EXERCISE_TYPES,
    SKILLS,
    DIFFICULTY_MODIFIERS,
    EDUCATIONAL_THEMES
)


class TopicSelectionDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Advanced Exercise Generator"
        )

        self.resize(900, 700)

        main_layout = QVBoxLayout()

        title = QLabel(
            "Choose Educational Parameters"
        )

        main_layout.addWidget(title)

        # SCROLL AREA

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll_widget = QWidget()

        scroll_layout = QVBoxLayout()

        # LEVEL

        level_layout = QHBoxLayout()

        level_layout.addWidget(
            QLabel("Difficulty Level")
        )

        self.level_box = QComboBox()

        self.level_box.addItems([
            "easy",
            "medium",
            "hard"
        ])

        level_layout.addWidget(
            self.level_box
        )

        scroll_layout.addLayout(
            level_layout
        )

        # GROUPS

        grammar_group = self.build_checkbox_group(
            "Grammar Topics",
            GRAMMAR_TOPICS
        )

        vocabulary_group = self.build_checkbox_group(
            "Vocabulary Topics",
            VOCABULARY_TOPICS
        )

        exercise_group = self.build_checkbox_group(
            "Exercise Types",
            EXERCISE_TYPES
        )

        skills_group = self.build_checkbox_group(
            "Skills",
            SKILLS
        )

        difficulty_group = self.build_checkbox_group(
            "Difficulty Modifiers",
            DIFFICULTY_MODIFIERS
        )

        themes_group = self.build_checkbox_group(
            "Educational Themes",
            EDUCATIONAL_THEMES
        )

        self.grammar_checkboxes = (
            grammar_group["checkboxes"]
        )

        self.vocabulary_checkboxes = (
            vocabulary_group["checkboxes"]
        )

        self.exercise_type_checkboxes = (
            exercise_group["checkboxes"]
        )

        self.skills_checkboxes = (
            skills_group["checkboxes"]
        )

        self.difficulty_modifier_checkboxes = (
            difficulty_group["checkboxes"]
        )

        self.theme_checkboxes = (
            themes_group["checkboxes"]
        )

        # ADD GROUPS

        scroll_layout.addWidget(
            grammar_group["group"]
        )

        scroll_layout.addWidget(
            vocabulary_group["group"]
        )

        scroll_layout.addWidget(
            exercise_group["group"]
        )

        scroll_layout.addWidget(
            skills_group["group"]
        )

        scroll_layout.addWidget(
            difficulty_group["group"]
        )

        scroll_layout.addWidget(
            themes_group["group"]
        )

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

        scroll_layout.addWidget(
            self.generate_button
        )

        scroll_layout.addWidget(
            self.cancel_button
        )

        scroll_widget.setLayout(
            scroll_layout
        )

        scroll.setWidget(scroll_widget)

        main_layout.addWidget(scroll)

        self.setLayout(main_layout)

    
    def build_checkbox_group(
            self,
            title,
            items
    ):

        group = QGroupBox(title)

        layout = QGridLayout()

        checkboxes = []

        row = 0
        col = 0

        for item in items:

            checkbox = QCheckBox(item)

            layout.addWidget(
                checkbox,
                row,
                col
            )

            checkboxes.append(
                checkbox
            )

            col += 1

            # 3 columns now instead of 2

            if col >= 3:

                col = 0

                row += 1

        group.setLayout(layout)

        return {
            "group": group,
            "checkboxes": checkboxes
        }


    def get_checked_items(
            self,
            checkbox_list
    ):

        return [

            checkbox.text()

            for checkbox in checkbox_list

            if checkbox.isChecked()
        ]


    def get_selected_data(self):

        return {

            "level":
            self.level_box.currentText(),

            "grammar_topics":
            self.get_checked_items(
                self.grammar_checkboxes
            ),

            "vocabulary_topics":
            self.get_checked_items(
                self.vocabulary_checkboxes
            ),

            "exercise_types":
            self.get_checked_items(
                self.exercise_type_checkboxes
            ),

            "skills":
            self.get_checked_items(
                self.skills_checkboxes
            ),

            "difficulty_modifiers":
            self.get_checked_items(
                self.difficulty_modifier_checkboxes
            ),

            "themes":
            self.get_checked_items(
                self.theme_checkboxes
            )
        }