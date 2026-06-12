from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QCheckBox,
    QTimeEdit
)

from PyQt6.QtCore import QTime


class StudentDialog(QDialog):
    def __init__(self, student=None):
        super().__init__()

        self.setWindowTitle("Student Form")

        layout = QVBoxLayout()

        # FULL NAME

        layout.addWidget(
            QLabel("Full Name")
        )

        self.name_input = QLineEdit()

        layout.addWidget(
            self.name_input
        )

        # TELEGRAM USERNAME

        layout.addWidget(
            QLabel("Telegram Username")
        )

        self.telegram_input = QLineEdit()

        layout.addWidget(
            self.telegram_input
        )

        # LEVEL

        layout.addWidget(
            QLabel("Level")
        )

        self.level_input = QComboBox()

        self.level_input.addItems([
            "A1",
            "A2",
            "B1",
            "B2",
            "C1",
            "C2"
        ])

        layout.addWidget(
            self.level_input
        )

        # SUBJECTS

        layout.addWidget(
            QLabel("Subject")
        )

        self.subject_input = QComboBox()

        self.subject_input.addItems([
            "math",
            "english",
            "coding"
        ])

        layout.addWidget(
            self.subject_input
        )

        # DAILY SEND TIME

        layout.addWidget(
            QLabel("Daily Send Time")
        )

        self.time_input = QTimeEdit()

        self.time_input.setTime(QTime(9, 0))

        layout.addWidget(
            self.time_input
        )

        #Active status

        self.active_input = QCheckBox(
            "Active"
        )

        self.active_input.setChecked(True)

        layout.addWidget(
            self.active_input
        )

        # SAVE BUTTON

        self.save_button = QPushButton("Save")

        self.save_button.clicked.connect(
            self.accept
        )

        layout.addWidget(self.save_button)

        if student:
            self.name_input.setText(
                student.full_name
            )

            self.telegram_input.setText(
                student.telegram_username
            )

            index = self.level_input.findText(student.level)
            if index != -1:
                self.level_input.setCurrentIndex(index)
            
            index = self.subject_input.findText(student.subject)
            if index != -1:
                self.subject_input.setCurrentIndex(index)

            hour, minute = map(
                int,
                student.daily_send_time.split(":")
            )

            self.time_input.setTime(
                QTime(hour, minute)
            )

            self.active_input.setChecked(
                student.active
            )

        self.setLayout(layout)

    def get_data(self):
        return {
          "full_name": self.name_input.text(),

          "telegram_username": self.telegram_input.text(),

          "level": self.level_input.currentText(),

          "subject": self.subject_input.currentText(),

          "daily_send_time":
          self.time_input.time().toString(
              "HH:mm"
          ),
          "active": self.active_input.isChecked()

        }
