"""
Implementation: Building the "Safe" Chat Room

To handle 50,000 users where any one of them might trigger a heavy task, you write the code like this:
"""

import asyncio
from concurrent.futures import ProcessPoolExecutor

# This is the "Chef" in the back (Separate Process = Parallelism)
def heavy_calculation(data):
    # Imagine complex audio processing or heavy math here
    return sum(i * i for i in range(10**7))

async def handle_user(user_id, executor, loop):
    while True:
        msg = await get_message(user_id)
        
        if "calculate" in msg:
            # WE DO NOT RUN IT HERE. We offload it.
            # This 'spawns' the work onto a worker process.
            result = await loop.run_in_executor(executor, heavy_calculation, msg)
            await send_message(user_id, result)
        else:
            await send_message(user_id, "Echo: " + msg)

async def main():
    loop = asyncio.get_running_loop()
    # Pre-spawn 4 workers (one for each CPU core)
    with ProcessPoolExecutor(max_workers=4) as executor:
        # Start 50,000 concurrent tasks
        users = [handle_user(i, executor, loop) for i in range(50000)]
        await asyncio.gather(*users)
