# Concurrency and Parallelism

> Separating "Dealing with a lot of things" from "Doing a lot of things at once".

## 1. The Concurrency Model (Wait-Time Management)

This script demonstrates Concurrency. Think of this as a single chef 👨‍🍳 managing three different pots on a stove. The chef isn't cooking three things at the exact same nanosecond, but they are managing the progress of all three by switching when one is just "simmering."

Code : `what_is_concurrency.py`

## 2. The Parallelism Model (Raw Power)
This script demonstrates Parallelism. This is no longer one chef; this is three separate kitchens 🏭🏭🏭, each with its own chef, stove, and ingredients. They are physically working at the exact same time on different CPU cores.

Code : `what_is_parallelism.py`

## The Mental Model Comparison

| -- | -- | -- | -- |
| Concept | Mental Image | Primary Constraint | Best For |
| Concurrency | 1 Waiter serving 10 tables | "The ""Waiter"" (Thread) speed" | "I/O, Network, WebSockets" |
| Parallelism | 10 Waiters serving 10 tables | "Number of ""Tables"" (CPU Cores) | "Math, Image processing, Compression" |

### Let's Test Your Mental Model

- If you run the Concurrency script (`what_is_concurrency.py`), Task A takes 3 seconds, Task B takes 1 second, and Task C takes 2 seconds.Based on the code, why is the "Total time elapsed" roughly 3 seconds instead of 6 seconds ($3+1+2$) ?
    - Because the tasks are just "waiting" (simulating I/O), they can all wait at the same time. The total time is simply the duration of the longest task ($3s$) because the 1-second and 2-second tasks finish while the 3-second task is still counting down.This is the Wait-Time Management model.

- Parallelism model (`what_is_parallelism.py`). In this script, we aren't "waiting"—we are "doing" (calculating math). 
    - In Python, there is a famous constraint called the Global Interpreter Lock (GIL). Think of the GIL as a single "Execution Key" 🔑. Even if you have 4 CPU cores, a single Python process only has one key. Only the person holding the key can use a core to execute Python code.In the Parallelism script, we used multiprocessing.Pool(). This creates 4 entirely different Python processes, which means we now have 4 separate keys.
    - If you have a 4-core machine and you need to run 4 heavy math tasks that each take 5 seconds:
        - If you ran them in a single-threaded loop (one after another), it would take 20 seconds.
        - If you ran them using asyncio (the concurrency model we just looked at), it would still take 20 seconds.

    - Why do you think asyncio (which worked so well for the 3-second waiting task) fails to save any time when the tasks are heavy math calculations? 🧐
        - asyncio is cooperative. A task must explicitly "cooperate" by yielding control (using await) back to the event loop. If a task is busy doing math, it never hits an await, so the event loop is "starved" and can't switch to anything else.

> In the industry, we call this "Blocking the Event Loop." 🛑 It’s one of the most common performance killers in Python systems.

### The Universal Scaling Problem

- This isn't just a Python problem. Whether you're using Node.js (JavaScript), Go, or Rust, the mental model for handling scale always comes down to these two questions:
    - Is the CPU waiting? (Network request, reading a file, waiting for a database).
        - Solution: Concurrency (Event loops, Green threads).
    - Is the CPU working? (Calculating audio frequencies, encrypting data, AI inference).
        - Solution: Parallelism (Multiple Processes, Multiple OS Threads).

--

### Designing the "Hybrid" System

- You use a Hybrid Model, imagine this architecture :
    - The Manager (Asyncio): One thread handles 5,000 active WebSocket connections. It's great at "waiting" for audio packets. 🎙️
    - The Workers (Multiprocessing): Whenever an audio packet needs "work" (like converting speech to text), the Manager ships that data off to a worker on a different core. ⚙️

### The Cost of Parallelism

- While Parallelism gives us more power, it isn't "free." In Python, when you move from a single-threaded asyncio loop to multiprocessing, you encounter a new challenge: Data Communication.
- In the asyncio script, all tasks shared the same memory. In the multiprocessing script, each process has its own private memory "island." 🏝️
- If you have a 10MB audio buffer in the Manager process and you want a Worker process to process it, you have to copy that data over.

## "Data Copying" Tax

- When we use standard Inter-Process Communication (IPC) like Pipes or Sockets, the OS acts as a middleman. If Process A wants to send a 10MB audio buffer to Process B, the data usually travels like this:
    - Copy 1: From Process A's memory into the Kernel's memory 🧠.
    - Copy 2: From the Kernel's memory into Process B's memory 📥.
- At a small scale, this is fine. But at thousands of users, your CPU spends more time moving bytes around than actually processing them. This creates Bus Contention (the data highway gets jammed) and adds several milliseconds of latency.

### The Solution: Zero-Copy Shared Memory 🚀

- To solve this, we use Shared Memory. Instead of moving the data, we tell the OS to let both processes look at the exact same physical RAM address.
    - How it works: Process A writes the audio into a shared block. Process B reads it instantly. The data never moves.
    - Implementation: In Python, we use `multiprocessing.shared_memory`.

--

### Scaling to 50,000 Chatters 💬

- You hit the nail on the head regarding RAM. If we used OS Threads (1 thread per user), the memory overhead for the "Thread Stacks" alone would be massive:

$$50,000 \text{ threads} \times 1 \text{ MB/thread} = 50 \text{ GB RAM}$$

- How we do it: The Event Loop 🎡

To handle this, we use Green Threads (managed by asyncio). Instead of the OS managing the switching, Python's Event Loop manages it.

```py
import asyncio

async def handle_chat_user(user_id):
    # This 'thread' only uses a few KB of RAM
    while True:
        message = await socket.receive() # Loop pauses here, freeing the CPU
        await socket.send(f"Echo: {message}")

async def main():
    # We can spawn 50,000 of these easily
    tasks = [handle_chat_user(i) for i in range(50000)]
    await asyncio.gather(*tasks)
```

By using await, the function effectively "suspends" itself. The Event Loop keeps a tiny object in memory representing that user's state, rather than a full 1MB OS stack.

We've seen that asyncio is great for waiting on 50,000 people to type. But what do you think would happen to those 50,000 connections if one single user triggered a function that spent 2 seconds doing heavy mathematical calculations without any await keywords? 🛑

### The Default (The Trap) 🪤

- If you just write a standard Python script with asyncio, it will not automatically spawn a new worker.
- asyncio runs on a single OS thread. If one of those 50,000 chatters triggers a function that does heavy math for 2 seconds (like sum(range(10**8))), the entire event loop stops.
    - The 49,999 other users can't send messages.
    - The heartbeat signals fail.
    - The server looks like it has crashed for 2 seconds.
- The event loop is not "smart" enough to realize it's stuck; it just follows the instructions it's given until it hits an await.

### The "Systems" Solution (The Worker) 👷‍♂️

- To make the system "spawn a new worker," you have to explicitly architect it to do so. This is what we call Offloading.
- In a high-scale system, you use a Thread Pool or Process Pool.


| Tool                      | Action                                                             | Mental Model                                                            |   |   |
|---------------------------|--------------------------------------------------------------------|-------------------------------------------------------------------------|---|---|
| `loop.run_in_executor`      | Ships the heavy task to a pool of pre-warmed threads or processes. | The waiter (Event Loop) hands the "cooking" task to a chef in the back. |   |   |
| Task Queue (Celery/Redis) | Sends the job to a completely different server.                    | The waiter calls a catering company to handle a massive order.          |   |   |
|                           |                                                                    |                                                                         |   |   |

Code : `safe_chat_room_via_offloading.py`

--

### The Universal Rule of Concurrency & Parallelism

- If you take away one thing for your Giga interview, let it be this:
    - Concurrency (asyncio) is for Orchestration: Managing 50,000 connections. It stays on the main thread and uses almost no CPU.
    - Parallelism (multiprocessing) is for Execution: Doing the actual math. It lives on other cores.
- How to use this across all runtimes?
    - In Node.js: You use the "Event Loop" for I/O and "Worker Threads" for CPU math.
    - In Go: You use "Goroutines" (Green threads). Go is unique because its scheduler automatically spreads Goroutines across multiple OS threads (Parallelism + Concurrency built-in).
    - In Rust: You use tokio (Async/Await) and rayon (Parallelism).

--

## Final "Systems" Test
- You have a 4-core server. You have 4 Worker Processes (Parallelism) and 1 Event Loop (Concurrency). The 4 workers are 100% busy processing audio for 4 users.
- What happens to the 5th user who tries to connect?
    - Does the connection fail immediately?
    - Does the connection succeed but the audio stays silent?
    - Does the Event Loop crash?

(Think about the "Waiter vs Chef" analogy).

The Waiter (Event Loop) is standing at the front door; he can seat the 5th user and take their order (Connection Succeeds). But when he goes to the kitchen, all the Chefs (Worker Processes) are already sweating over hot pans. The order just sits on the counter. In a voice agent, that translates to dead silence.

To a user, silent audio is a failure. To a systems engineer, this means we need to handle Backpressure.

--


