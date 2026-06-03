from telethon import TelegramClient
from dotenv import load_dotenv
from pathlib import Path
from services.logger import logger 

import os

Base_DIR = Path(__file__).resolve().parent.parent

load_dotenv(Base_DIR / ".env")

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

if not api_id:
    raise RuntimeError(
        "API_ID missing from .env"
    )

if not api_hash:
    raise RuntimeError(
        "API_HASH missing from .env"
    )

api_id = int(api_id)

client = TelegramClient("teacher_session", api_id, api_hash)

async def start_client():

    await client.start()

    me = await client.get_me()

    logger.info(f"Telegram connected as "
                f"{me.username or me.first_name}"
            )

async def send_message(username, message):

    try:
        if not client.is_connected():

            logger.warning(
                "Telegram client disconnected. "
                "Reconnecting..."
            )
            await client.connect()

            logger.info("Telegram reconnect successful")
        
        entity = await client.get_input_entity(username)

        await client.send_message(
            entity,
            message
        )

        logger.info(f"Message sent to {username}")
    
    except Exception as e:
        logger.exception(f"Telegram send failed for {username}")
        raise


