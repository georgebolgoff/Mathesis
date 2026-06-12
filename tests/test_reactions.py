import sys
from pathlib import Path
import asyncio 

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from telegram_client.client import client, start_client

async def main():

    await start_client()

    entity = await client.get_entity(
        "@asolnechnaya8"
    )

    messages = await client.get_messages(
        entity,
        limit=20
    )

    for msg in messages:

        print("\nMESSAGE:")
        print(msg.text)

        print("REACTIONS:")
        print(msg.reactions)


asyncio.run(main())