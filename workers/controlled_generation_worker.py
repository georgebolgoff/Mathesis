from PyQt6.QtCore import (
    QThread,
    pyqtSignal
)

from ai.engine import (
    generate_controlled_exercise
)


class ControlledGenerationWorker(QThread):

    success = pyqtSignal(str)

    error = pyqtSignal(str)

    def __init__(self, selected_data):

        super().__init__()

        self.selected_data = (
            selected_data
        )

    def run(self):

        try:

            result = (
                generate_controlled_exercise(
                    self.selected_data
                )
            )

            if not result["ok"]:

                self.error.emit(
                    result["message"]
                )

                return

            self.success.emit(
                result["content"]
            )

        except Exception as e:

            self.error.emit(
                str(e)
            )