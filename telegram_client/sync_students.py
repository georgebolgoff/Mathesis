import asyncio
import telegram_client.async_loop as async_loop
from telegram_client.student_sync import sync_students_from_telegram


def sync_students_sync():

    future = asyncio.run_coroutine_threadsafe(
        sync_students_from_telegram(),
        async_loop.loop
    )

    return future.result()