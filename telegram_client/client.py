from telethon import TelegramClient
from dotenv import load_dotenv
import os

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

client = TelegramClient("teacher_session", api_id, api_hash)

async def start_client():
    await client.start()
    print("Telegram connected")

async def send_message(username, message):
    try:
        if not client.is_connected():
            await client.connect()
        
        entity = await client.get_input_entity(username)

        await client.send_message(
            entity,
            message
        )

        print(f"Sent message to {username}")
    
    except Exception as e:
        print("Telegram send error:", e)
        raise


