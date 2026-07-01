from PyQt6.QtCore import QObject, pyqtSignal

class LogBus(QObject):
    """
    Central real-time log broadcaster.
    Any part of the app can emit logs here,
    and UI widgets can listen to them.
    """

    log_emitted = pyqtSignal(str, str, str)
    # (timestamp, level, message)


log_bus = LogBus()

