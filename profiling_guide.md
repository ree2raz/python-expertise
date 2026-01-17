# Profiling Guide

> Profiling is the science of Observability. It is broken down into three levels of depth.

## Level 1: Deterministic Profiling (cProfile)

- This is the "Old Faithful" of Python. It tracks every single function call, how many times it was called, and how long it took.
- The Real-World Scenario: You notice your Voice Agent is taking 100ms longer than usual to process a sentence. You run cProfile to find the "Heavy" function.

```py
import cProfile
import pstats

def process_audio_chunk():
    # Imagine some logic here
    result = [i**2 for i in range(10000)]
    return result

# We wrap the execution in a profile object
with cProfile.Profile() as pr:
    process_audio_chunk()

# We print the stats sorted by 'cumulative' time
stats = pstats.Stats(pr)
stats.sort_stats(pstats.SortKey.CUMULATIVE)
stats.print_stats(10) # Print top 10 bottlenecks
```

> The Problem: cProfile has high overhead. It slows down your code by 2x–10x because it's intercepting every call. You never run this on every request in production.

--

## Level 2: Statistical Profiling (Sampling)

- This is how "Production" profiling works. Instead of tracking every call, the profiler "wakes up" every 1ms or 10ms, looks at what the CPU is doing (the stack trace), and goes back to sleep.
- Tools: `Py-Spy` or `Austin`
- Why this is "Systems Thinking": * Low Overhead: It doesn't slow down the app (usually <1-2% CPU hit).
    - Zero Code Change: You can "attach" it to a running production process without restarting it.
    - The Mental Model: If you sample 1,000 times and 800 times the CPU was inside json.loads(), you know that JSON parsing is your 80% bottleneck.

--

## Level 3: Visual Trace Profiling (VizTracer)

- In a millisecond-latency system, "total time" isn't enough. You need to see the Gaps. These are the periods where your CPU is doing nothing because it's waiting for a lock, a worker, or the OS.
- The Real-World Scenario: You have an Asyncio loop and a Process Pool. You see "Stuttering." VizTracer shows you a timeline of exactly when the main process hands data to the worker.

```bash
# You run your app through viztracer
viztracer my_voice_app.py
```

- This generates a Flame Graph.
    - How to read it: Long bars are functions. Gaps between bars are "Idle time." In a voice agent, a gap usually means a Serialization delay or an Asyncio loop block.

--

### The "Universal" Concepts of Profiling

Regardless of the language (Go, Rust, Python), you are looking for these three metrics:

| Metric          | What it means                              | The "Fix"                                               |   |   |
|-----------------|--------------------------------------------|---------------------------------------------------------|---|---|
| Wall Clock Time | The actual time the user waits.            | Optimize I/O or Parallelize.                            |   |   |
| CPU Time        | The time the CPU was actually "crunching." | Optimize algorithms (e.g., use NumPy instead of loops). |   |   |
| Memory Pressure | How often the Garbage Collector runs.      | Use __slots__, object pools, or shared memory.          |   |   |


--

### The High-Scale Production Strategy: "Continuous Profiling"

- In a startup, you don't wait for a bug to profile. You use Continuous Profilers (like Pyroscope or Datadog Profiler).
    - The profiler runs in the background of your production servers 24/7.
    - It sends small samples of stack traces to a central dashboard.
    - When a user says "The agent felt slow at 3 PM," you look at the 3 PM graph and see exactly which function was eating CPU at that moment.

### A Practical Exercise in "Systems" Profiling

- Imagine you profile your voice agent and see that socket.send() is taking 40ms.
    - The Coder's thought: "Maybe I should use a faster library for sockets."
    - The Systems Architect's thought: "Is the network buffer full? Is the OS kernel copying this data too many times? Should I use a Zero-Copy approach?"


