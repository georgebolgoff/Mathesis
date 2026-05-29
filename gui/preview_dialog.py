from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel
)

from ai.engine import generate_controlled_exercise
from gui.topic_selection_dialog import TopicSelectionDialog


class PreviewDialog(QDialog):

    def __init__(self, student_name, message, dialog_type="exercise"):
        super().__init__()

        self.preview_type = dialog_type

        self.setWindowTitle(
            "Exercise Preview"
        )

        self.resize(500, 400)

        self.action = None

        layout = QVBoxLayout()

        title = QLabel(
            f"Preview for {student_name}"
        )

        self.editor = QTextEdit()

        self.editor.setPlainText(message)

        self.send_button = QPushButton(
            "Confirm And Send This Exercise"
        )

        self.another_button = QPushButton(
            "Another Exercise"
        )

        self.cancel_button = QPushButton(
            "Cancel"
        )

        self.choose_topics_button = QPushButton(
            "Choose Topics"
        )

        self.confirm_button = QPushButton(
            "Confirm And Send"
        )

        self.confirm_button.hide()

        self.send_button.setDefault(False)
        self.send_button.setAutoDefault(False)

        self.another_button.setDefault(False)
        self.another_button.setAutoDefault(False)

        self.cancel_button.setDefault(False)
        self.cancel_button.setAutoDefault(False)

        self.send_button.clicked.connect(
            self.prepare_send
        )

        self.another_button.clicked.connect(
            self.another_clicked
        )

        self.choose_topics_button.clicked.connect(
            self.choose_topics
        )

        self.confirm_button.clicked.connect(
            self.confirm_send
        )

        self.cancel_button.clicked.connect(
            self.cancel_clicked
        )

        layout.addWidget(title)
        layout.addWidget(self.editor)
        layout.addWidget(self.send_button)
        layout.addWidget(self.another_button)
        
        # ONLY FOR EXERCISES
        if self.dialog_type == "exercise":

            layout.addWidget(

                layout.addWidget(
                    self.choose_topics_button
                )
            )

        layout.addWidget(self.confirm_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def send_clicked(self):

        self.action = "send"

        self.accept()
    
    def prepare_send(self):

        self.send_button.hide()
        self.another_button.hide()
        self.confirm_button.show()
        self.action = "prepare_send"

    
    def confirm_send(self):
        
        print("CONFIRM SEND CLICKED")

        self.action = "send"

        self.accept()


    def another_clicked(self):

        self.action = "another"

        self.accept()


    def cancel_clicked(self):

        self.action = "cancel"

        self.reject()
    

    def get_message(self):

        return self.editor.toPlainText()
    
    def choose_topics(self):

        dialog = TopicSelectionDialog()

        result = dialog.exec()

        if not result:
            return 
        
        selected_data = (
            dialog.get_selected_data()
        )

        print(
            "SELECTED TOPIC DATA:",
            selected_data
        )

        result = (
            generate_controlled_exercise(
                selected_data
            )
        )

        if not result["ok"]:

            print(
                "CONTROLLED GENERATION ERROR:",
                result["message"]
            )

            return
        
        self.editor.setPlainText(
            result["content"]
        )
    
