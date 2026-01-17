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


