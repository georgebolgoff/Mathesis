import asyncio

from PyQt6.QtCore import QThread, pyqtSignal

import telegram_client.async_loop as async_loop
from telegram_client.client import start_client
from telegram_client.sync_students import sync_students_sync
from database.seed_idioms import seed_idioms
from database.seed_templates import seed_message_templates
from scheduler.tasks import start_scheduler
from services.logger import logger, log_event


class StartupWorker(QThread):
    """
    Runs all blocking startup work off the UI thread.
    Emits progress updates for the splash screen.
    """

    progress_updated = pyqtSignal(int, str)
    finished_ok = pyqtSignal()
    failed = pyqtSignal(str)

    def run(self):
        try:
            self.progress_updated.emit(10, "Starting Mathesis...")

            log_event("info", "bootstrap_started")
            async_loop.start_loop_thread()
            log_event("info", "async_loop_ready")

            async_loop.loop_ready.wait()
            log_event("info", "async_loop_ready")

            self.progress_updated.emit(30, "Connecting to Telegram...")

            logger.info("Initializing Telegram client")
            asyncio.run_coroutine_threadsafe(
                start_client(),
                async_loop.loop,
            ).result()
            log_event("info", "telegram_initialized")

            self.progress_updated.emit(55, "Syncing students...")

            logger.info("Syncing students...")
            sync_students_sync()
            log_event("info", "students_synced")

            self.progress_updated.emit(75, "Preparing database...")

            logger.info("Seeding idioms...")
            seed_idioms()

            logger.info("Seeding message templates...")
            seed_message_templates()

            self.progress_updated.emit(100, "Ready")
            self.finished_ok.emit()
        
        except Exception as e:
            logger.exception("Startup failed")
            self.failed.emit(str(e))