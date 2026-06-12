import asyncio

import telegram_client.async_loop as async_loop


from services.streak_reaction_service import check_streak_resets


def check_streak_resets_sync():

    future = asyncio.run_coroutine_threadsafe(
        check_streak_resets(),
        async_loop.loop
    )

    return future.result()
