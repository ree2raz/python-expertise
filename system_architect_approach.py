import asyncio
import time
from concurrent.futures import ProcessPoolExecutor

async def handle_websocket():
    """Simulates receiving audio packets every 100ms."""
    for i in range(10):
        print(f"🎙️ Received audio packet {i}")
        await asyncio.sleep(0.1)  # Non-blocking wait

def cpu_bound_math():
    """The heavy lifting, moved outside the async loop."""
    start = time.perf_counter()
    while time.perf_counter() - start < 0.5:
        _ = 2 ** 1000
    return "Analysis Result"

async def main():
    loop = asyncio.get_running_loop()
    
    # We create a 'Worker' (a separate Process to bypass the GIL)
    with ProcessPoolExecutor() as pool:
        print("🚀 System started...")
        
        # We 'schedule' the math to run on a DIFFERENT CPU CORE
        # but we don't 'await' it immediately so the loop stays free!
        analysis_task = loop.run_in_executor(pool, cpu_bound_math)
        
        # Now the WebSocket handler can run smoothly on the main thread
        await handle_websocket()
        
        result = await analysis_task
        print(f"🏁 Final {result}")

asyncio.run(main())
