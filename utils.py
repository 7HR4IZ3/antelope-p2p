import time

def nanoseconds():
    load_ns = time.time_ns()
    load_ms = int(time.time() * 1000)
    diff_ns = time.time_ns() - load_ns
    return (load_ms * 10**6) + diff_ns
