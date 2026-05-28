import asyncio

from telegram_client.client import (
    send_message
)

from telegram_client.async_loop import (
    loop
)


def send_message_sync(username, message):

    future = asyncio.run_coroutine_threadsafe(
        send_message(username, message),
        loop
    )

    return future.result()