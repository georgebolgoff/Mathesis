import asyncio
from telegram_client.async_loop import loop
from telegram_client.student_sync import sync_students_from_telegram


def sync_students_sync():

    future = (
        asyncio.run_coroutine_threadsafe(
            sync_students_from_telegram(),
            loop
        )
    )

    return future.result()