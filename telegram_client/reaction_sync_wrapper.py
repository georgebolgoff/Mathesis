import asyncio

import telegram_client.async_loop as async_loop

from services.streak_reaction_service import check_reaction_approvals

def check_reactions_sync():

    future = asyncio.run_coroutine_threadsafe(
        check_reaction_approvals(),
        async_loop.loop
    )

    return future.result()