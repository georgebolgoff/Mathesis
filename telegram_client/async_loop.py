import asyncio
import threading

loop = None

loop_ready = threading.Event()

def start_background_loop():

    global loop 

    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    loop_ready.set()

    
    loop.run_forever()
    
        

def start_loop_thread():

    thread = threading.Thread(
        target=start_background_loop,
        daemon=True
    )

    thread.start()