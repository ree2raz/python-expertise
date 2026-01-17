import multiprocessing
import time

def cpu_heavy_task(name, number):
    print(f"⚙️ Worker {name}: Calculating square of {number}...")
    # Physical math that eats CPU cycles
    result = sum(i * i for i in range(number))
    print(f"✨ Worker {name}: Done!")
    return result

if __name__ == "__main__":
    numbers = [10**7, 10**8, 10**6, 10**8]
    start_time = time.perf_counter()
    
    # Create a Pool of processes (one for each CPU core)
    print(f"🚀 Launching {len(numbers)} Parallel Processes...")
    with multiprocessing.Pool() as pool:
        results = pool.starmap(cpu_heavy_task, enumerate(numbers))
        
    end_time = time.perf_counter()
    print(f"🏁 Total time elapsed: {end_time - start_time:.2f} seconds")
