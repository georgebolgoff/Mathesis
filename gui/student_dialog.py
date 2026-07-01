from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QCheckBox,
    QTimeEdit, 
    QSpinBox,
    QMessageBox,
)

from PyQt6.QtCore import QTime


class StudentDialog(QDialog):
    def __init__(self, student=None):
        super().__init__()

        self.setWindowTitle("Student Form")
        self.resize(420, 580)

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

        # EXERCISES PER DAY

        layout.addWidget(QLabel("Exercises per day"))
        self.exercises_per_day_input = QSpinBox()
        self.exercises_per_day_input.setMinimum(1)
        self.exercises_per_day_input.setMaximum(5)
        self.exercises_per_day_input.setValue(1)
        self.exercises_per_day_input.valueChanged.connect(
            self._sync_send_times_with_count
        )
        layout.addWidget(self.exercises_per_day_input)

        # SEND TIMES
        layout.addWidget(
            QLabel("Send times (comma separated, e.g. 09:00,18:00)")
        )
        self.send_times_input = QLineEdit()
        self.send_times_input.setPlaceholderText("09:00")
        layout.addWidget(self.send_times_input)

        # FIRST SEND TIME (Legacy field / quick editor for slot 1)
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime(9, 0))
        self.time_input.timeChanged.connect(self._sync_first_send_time)
        layout.addWidget(self.time_input)

        #Active status

        self.active_input = QCheckBox(
            "Active"
        )

        self.active_input.setChecked(True)

        layout.addWidget(
            self.active_input
        )

        # STREAK

        layout.addWidget(
            QLabel("Streak")
        )

        self.streak_input = QSpinBox()
        self.streak_input.setMinimum(0)
        self.streak_input.setMaximum(999)
        self.streak_input.setValue(0)
        self.streak_input.setToolTip(
            "Manually set the student's streak count"
        )

        layout.addWidget(
            self.streak_input
        )

        self.mark_today_approved_input = QCheckBox(
            "Mark today's exercises as approved (💯)"
        )

        self.mark_today_approved_input.setToolTip(
            "Use when exercises were done but you forgot to reach with 💯"
            "Clears Waiting status and prevents 48h streak reset for today."
        )
        self.mark_today_approved_input.hide()

        layout.addWidget(
            self.mark_today_approved_input
        )

        # SAVE BUTTON

        self.save_button = QPushButton("Save")

        self.save_button.clicked.connect(
            self._on_save_clicked
        )

        layout.addWidget(self.save_button)

        if student:
            self.name_input.setText(student.full_name or "")

            self.telegram_input.setText(student.telegram_username or "")

            level_index = self.level_input.findText(
                (student.level or "").upper()
            )
            if level_index != -1:
                self.level_input.setCurrentIndex(level_index)

            subject_index = self.subject_input.findText(student.subject or "")

            if subject_index != -1:
                self.subject_input.setCurrentIndex(subject_index)

            exercises_per_day = getattr(student, "exercises_per_day", 1) or 1

            self.exercises_per_day_input.setValue(exercises_per_day)

            send_times = (
                getattr(student, "daily_send_times", None)
                or student.daily_send_time
                or "09:00"
            )

            self.send_times_input.setText(send_times)

            first_time = send_times.split(",")[0].strip()

            hour, minute = map(int, first_time.split(":"))

            self.time_input.setTime(QTime(hour, minute))

            self.active_input.setChecked(student.active)

            self.streak_input.setValue(student.streak or 0)
            self.mark_today_approved_input.show()

        self.setLayout(layout)
    

    def _sync_first_send_time(self):
        """
        Keep first slot in send_times in sync with the time picker.
        """

        first = self.time_input.time().toString("HH:mm")

        raw = self.send_times_input.text().strip()
        if not raw:
            self.send_times_input.setText(first)
            return
        
        parts = [p.strip() for p in raw.split(",") if p.strip()]

        if not parts:
            self.send_times_input.setText(first)
            return
        
        parts[0] = first

        self.send_times_input.setText(", ".join(parts))

    def _sync_send_times_with_count(self, count):
        """
        If user increases exercises/day, add default second slot.
        If user decreases, trim extra slots.
        """
        parts = [
            p.strip()
            for p in self.send_times_input.text().split(",")
            if p.strip()
        ]

        if not parts:
            parts = [self.time_input.time().toString("HH:mm")]

        while len(parts) < count:
            if len(parts) == 1:
                parts.append("18:00")
            else:
                parts.append(parts[-1])

        parts = parts[:count]

        self.send_times_input.setText(", ".join(parts))

    def _validate_send_times(self, text, expected_count):

        parts = [p.strip() for p in text.split(",") if p.strip()]

        if len(parts) != expected_count:
            return (
                False,
                f"Provide exactly {expected_count} send time(s)."
            )
        
        for part in parts:

            try:

                hour, minute = map(int, part.split(":"))

                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError
                
            except ValueError:

                return (
                    False,
                    f"Invalid time format: '{part}'. Use HH:mm."
                )
            
        return True, ", ".join(parts)
    
    def _on_save_clicked(self):

        count = self.exercises_per_day_input.value()

        ok, message = self._validate_send_times(
            self.send_times_input.text(),
            count,
        )

        if not ok:
            QMessageBox.warning(self, "Invalid send times", message)
            return
        
        self.send_times_input.setText(message)

        self.accept()

    def get_data(self):

        send_times = self.send_times_input.text().strip()

        first_time = send_times.split(",")[0].strip()

        return {
            "full_name": self.name_input.text().strip(),
            "telegram_username": self.telegram_input.text().strip(),
            "level": self.level_input.currentText(),
            "subject": self.subject_input.currentText(),
            "daily_send_time": first_time,
            "daily_send_times": send_times,
            "exercises_per_day": self.exercises_per_day_input.value(),
            "active": self.active_input.isChecked(),
            "streak": self.streak_input.value(),
            "mark_today_approved": self.mark_today_approved_input.isChecked(),
        }
