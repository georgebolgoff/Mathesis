import asyncio

from telegram_client.client import client

import telegram_client.async_loop as async_loop


from services.reaction_checker import check_reactions

def check_reactions_sync():

    future = asyncio.run_coroutine_threadsafe(
        check_reactions(),
        async_loop.loop
    )

    return future.result()