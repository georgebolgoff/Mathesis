import sys
import asyncio
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.style import DARK_STYLE
from telegram_client.client import start_client
import telegram_client.async_loop as async_loop
from telegram_client.sync_students import sync_students_sync
from database.seed_idioms import seed_idioms
from database.seed_templates import seed_message_templates
from services.logger import logger, log_event






def bootstrap():

    log_event("info", "bootstrap_started")

    async_loop.start_loop_thread()
    log_event("info", "async_loop_started")

    async_loop.loop_ready.wait()
    log_event("info", "async_loop_ready")

    logger.info("Initializing Telegram client")
    asyncio.run_coroutine_threadsafe(
        start_client(),
        async_loop.loop
    ).result()
    log_event("info","telegram_initialized")

def main():
    bootstrap()

    logger.info("Syncing students...")
    sync_students_sync()
    log_event("info", "students_synced")

    # logger.info("Seeding exercises...")
    # seed_exercises()

    logger.info("Seeding idioms...")
    seed_idioms()

    logger.info("Seeding message templates...")
    seed_message_templates()

    logger.info("Starting Qt application")

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)

    window = MainWindow()

    window.show()

    log_event("info", "gui_launched")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

#### v2
# import asyncio
# from telegram_client.client import start_client, send_message

# async def main():
#     await start_client()

#     await send_message("George", "Hello from my automation app!")


# asyncio.run(main())


#### v1
#asyncio.run(start_client())

