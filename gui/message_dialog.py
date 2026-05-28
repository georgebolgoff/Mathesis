from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel
)


class MessageDialog(QDialog):
    def __init__(self, student_name):
        super().__init__()

        self.setWindowTitle("Send Message")

        self.resize(500, 300)

        layout = QVBoxLayout()
        
        title = QLabel(f"Message for {student_name}")
        self.editor = QTextEdit()
        self.send_button = QPushButton("Send")
        self.cancel_button = QPushButton("Cancel")

        self.send_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        layout.addWidget(title)
        layout.addWidget(self.editor)
        layout.addWidget(self.send_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def get_message(self):
        return self.editor.toPlainText()
