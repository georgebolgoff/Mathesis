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
    QComboBox
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

        self.resize(700, 800)

        self.layout = QVBoxLayout()

        title = QLabel(
            "Choose Educational Parameters"
        )

        self.layout.addWidget(title)

        # SCROLL AREA 

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        content_widget = QWidget()

        content_layout = QVBoxLayout()

        # LEVEL

        self.level_box = QComboBox()

        self.level_box.addItems([
            "easy",
            "medium",
            "hard"
        ])

        content_layout.addWidget(
            self.level_box
        )

        # TOPIC GROUPS 

        self.grammar_checkboxes = (
            self.build_checkbox_group(
                "Grammar Topic",
                GRAMMAR_TOPICS
            )
        )

        self.vocabulary_checkboxes = (
            self.build_checkbox_group(
                "Vocabulary Topics",
                VOCABULARY_TOPICS
            )
        )

        self.exercise_type_checkboxes = (
            self.build_checkbox_group(
                "Exercise Types",
                EXERCISE_TYPES
            )
        )

        self.skills_checkboxes = (
            self.build_checkbox_group(
                "Skills",
                SKILLS
            )
        )

        self.difficulty_modifier_checkboxes = (
            self.build_checkbox_group(
                "Difficulty Modifiers",
                DIFFICULTY_MODIFIERS
            )
        )

        self.theme_checkboxes = (
            self.buld_checkbox_group(
                "Educational Themes",
                EDUCATIONAL_THEMES
            )
        )

        # ADD GROUPS

        content_layout.addWidget(
            self.grammar_checkboxes["group"]
        )

        content_layout.addWidget(
            self.vocabulary_checkboxes["group"]
        )

        content_layout.addWidget(
            self.exercise_type_checkboxes["group"]
        )

        content_layout.addWidget(
            self.skills_checkboxes["group"]
        )

        content_layout.addWidget(
            self.difficulty_modifier_checkboxes["group"]
        )

        content_layout.addWidget(
            self.theme_checkboxes["group"]
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

        content_layout.addWidget(
            self.generate_button
        )

        content_layout.addWidget(
            self.cancel_button
        )

        content_layout.setLayout(
            content_layout
        )

        scroll.setWidget(content_widget)

        self.layout.addWidget(scroll)

        self.setLayout(self.layout)
    
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

            checkboxes.append(checkbox)

            col += 1

            row += 1
        
        group.setLayout(layout)

        return {
            "group": group,
            "checkboxes": checkboxes
        }
    

    def get_selected_data(self):

        return {
            "level":
            self.level_box.currentText(),

            "grammar topics":
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
    

    def get_checked_items(self, group_data):

        return [
            
            checkbox.text()

            for checkbox in (
                group_data["checkboxes"]
            )

            if checkbox.isChecked()
        ]