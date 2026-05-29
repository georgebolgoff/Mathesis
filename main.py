import sys
import asyncio
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.style import DARK_STYLE
from telegram_client.client import start_client
from telegram_client.async_loop import loop
from telegram_client.sync_students import sync_students_sync
from database.seed_exercises import seed_exercises
from database.seed_idioms import seed_idioms
from database.seed_templates import seed_message_templates



def bootstrap():
    asyncio.run_coroutine_threadsafe(
        start_client(),
        loop
    ).result()

def main():
    bootstrap()

    sync_students_sync()

    seed_exercises()

    seed_idioms()

    seed_message_templates()

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)

    window = MainWindow()

    window.show()

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

