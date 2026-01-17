import asyncio
import time

async def handle_websocket():
    """Simulates receiving audio packets every 100ms."""
    for i in range(10):
        print(f"🎙️ Received audio packet {i}")
        await asyncio.sleep(0.1)  # Non-blocking wait

async def heavy_audio_analysis():
    """Simulates CPU-heavy math (e.g., FFT or Pitch detection)."""
    print("⚙️ Starting heavy analysis...")
    # This is a 'System Trap': No await here, just pure math!
    start = time.perf_counter()
    while time.perf_counter() - start < 0.5:
        _ = 2 ** 1000  # Busy work
    print("✅ Analysis complete!")

async def main():
    # Attempting to run them "together"
    await asyncio.gather(handle_websocket(), heavy_audio_analysis())

asyncio.run(main())
