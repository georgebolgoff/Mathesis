from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QGraphicsOpacityEffect,
)

from PyQt6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QTimer,
)


class StartupSplash(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mathesis")
        self.setFixedSize(420,380)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        self._bar_animation = None
        self._fade_out_anumation = None
        self._fade_in_animation = None
        self._pulse_animation = None 

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 24)
        root.setSpacing(0)

        self.logo_label = QLabel("Σ")
        self.logo_label.setObjectName("SplashLogo")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("Starting Mathesis...")
        self.status_label.setObjectName("SplashStatus")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)

        self.error_label = QLabel("")
        self.error_label.setObjectName("SplashError")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.hide()

        self.retry_button = QPushButton("Retry")
        self.retry_button.hide()
        self.retry_button.clicked.connect(self._on_retry_clicked)

        self.quit_button = QPushButton("Quit")
        self.quit_button.hide()
        self.quit_button.clicked.connect(QApplication.instance().quit)

        error_buttons = QHBoxLayout()
        error_buttons.addStretch()
        error_buttons.addWidget(self.retry_button)
        error_buttons.addWidget(self.quit_button)
        error_buttons.addStretch()

        brand_label = QLabel("Mathesis")
        brand_label.setObjectName("SplashBrand")
        brand_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        root.addStretch()
        root.addWidget(self.logo_label)
        root.addSpacing(28)
        root.addWidget(self.status_label)
        root.addSpacing(14)
        root.addWidget(self.progress_bar)
        root.addSpacing(16)
        root.addWidget(self.error_label)
        root.addLayout(error_buttons)
        root.addStretch()
        root.addWidget(brand_label)

        self._retry_callback = None
        self._start_logo_pulse()
    
    def center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2,
        )

    def _start_logo_pulse(self):
        opacity = QGraphicsOpacityEffect(self.logo_label)
        self.logo_label.setGraphicsEffect(opacity)

        animation = QPropertyAnimation(opacity, b"opacity", self)
        animation.setDuration(1200)
        animation.setStartValue(0.45)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        animation.setLoopCount(-1)
        animation.start()

        self._pulse_animation = animation

    def set_progress(self, value: int, message: str):
        self.status_label.setText(message)

        animation = QPropertyAnimation(self.progress_bar, b"value", self)
        animation.setDuration(450)
        animation.setStartValue(self.progress_bar.value())
        animation.setEndValue(value)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()

        self._bar_animation = animation

    
    def show_error(self, message: str, retry_callback=None):
        self._retry_callback = retry_callback

        self.status_label.setText("Startup failed")
        self.error_label.setText(message)
        self.error_label.show()

        self.retry_button.setVisible(retry_callback is not None)
        self.quit_button.show()

        self.progress_bar.setStyleSheet("""
            QProgressBar {
                                        
                background-color: #2b2b2b;
                border: none;
                border-radius: 3px;
                min-height: 6px;
                max-height: 6px;
            }
            QProgressBar::chunk {
                background-color: #ff6b6b;
                border-radius: 3px;
                }
        """)
    
    def _on_retry_clicked(self):
        self.error_label.hide()
        self.retry_button.hide()
        self.quit_button.hide()

        self.progress_bar.setStyleSheet("")
        self.set_progress(0, "Starting Mathesis...")

        if self._retry_callback:
            self._retry_callback()
    

    def fade_out_then_show(self, main_window: QWidget):

        def start_fade_in():
            self.close()

            main_window.setWindowOpacity(0.0)
            main_window.show()

            fade_in = QPropertyAnimation(main_window, b"windowOpacity", self)
            fade_in.setDuration(300)
            fade_in.setStartValue(0.0)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
            fade_in.start()

            self._fade_in_animation = fade_in

        
        fade_out = QPropertyAnimation(self, b"windowOpacity", self)
        fade_out.setDuration(300)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.InOutCubic)
        fade_out.finished.connect(start_fade_in)
        fade_out.start()

        self._fade_in_animation = fade_out 
