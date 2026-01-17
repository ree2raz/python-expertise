import asyncio
import time

async def simulate_io_task(name, duration):
    print(f"⏳ Task {name}: Starting (will wait {duration}s)")
    # 'await' is the magic word. It tells the loop: "I'm waiting, go do something else!"
    await asyncio.sleep(duration) 
    print(f"✅ Task {name}: Finished after {duration}s")

async def main():
    start_time = time.perf_counter()
    
    # We schedule 3 tasks to run concurrently
    print("🚀 Starting Concurrent Event Loop...")
    await asyncio.gather(
        simulate_io_task("A", 3),
        simulate_io_task("B", 1),
        simulate_io_task("C", 2)
    )
    
    end_time = time.perf_counter()
    print(f"🏁 Total time elapsed: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
