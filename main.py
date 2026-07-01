import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from gui.main_window import MainWindow
from gui.startup_splash import StartupSplash
from gui.style import DARK_STYLE, SPLASH_STYLE
from workers.startup_worker import StartupWorker
from services.logger import logger, log_event






def main():

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE + SPLASH_STYLE)

    logger.info("Starting Qt application")

    splash = StartupSplash()
    splash.center_on_screen()
    splash.show()

    worker = StartupWorker()
    main_window = None

    def start_worker():
        worker.start()
    
    def on_progress(value, message):
        splash.set_progress(value, message)

    def on_finished():
        splash.set_progress(100, "Ready")

        def open_dashboard():
            nonlocal main_window

            log_event("info", "gui_launched")
            logger.info("gui_launched")

            main_window = MainWindow()
            splash.fade_out_then_show(main_window)
        
        QTimer.singleShot(300, open_dashboard)
    
    def on_failed(error_message):
        splash.show_error(error_message, retry_callback=start_worker)
    

    worker.progress_updated.connect(on_progress)
    worker.finished_ok.connect(on_finished)
    worker.failed.connect(on_failed)

    start_worker()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

