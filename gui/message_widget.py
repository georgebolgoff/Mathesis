from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel
)
from telegram_client.sync_wrapper import send_message_sync

class MessageWidget(QWidget):
    def __init__(self, get_student):
        super().__init__()

        self.get_student = get_student

        layout = QVBoxLayout()
        
        self.label = QLabel("Message Editor")

        self.editor = QTextEdit()

        self.send_button = QPushButton(
            "Send Message"
        )
        self.send_button.clicked.connect(self.send)

        layout.addWidget(self.label)
        layout.addWidget(self.editor)
        layout.addWidget(self.send_button)

        self.setLayout(layout)


    def send(self):
        student = self.get_student()

        if not student:
            self.label.setText("❌ No student selected")
            return
        
        message = self.editor.toPlainText()

        if not message.strip():
            self.label.setText("❌ Empty message")
            return


        self.label.setText(f"✅ Sent to {student['full_name']}")

        try:
            send_message_sync(student["telegram_username"], message)

            self.label.setText(f"✅ Sent to {student['full_name']}")

        except Exception as e:
            self.label.setText(f"❌ Error: {str(e)}")