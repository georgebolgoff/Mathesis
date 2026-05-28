import asyncio
import threading

loop = asyncio.new_event_loop()


def start_background_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()



thread = threading.Thread(
    target=start_background_loop,
    daemon=True
)

thread.start()