import asyncio

from telegram_client.client import (
    send_message
)

import telegram_client.async_loop as async_loop


def send_message_sync(username, message):

    future = asyncio.run_coroutine_threadsafe(
        send_message(username, message),
        async_loop.loop
    )

    return future.result()