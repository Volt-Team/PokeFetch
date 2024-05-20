import time


class Benchmark:
    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.perf_counter()
        self.end_time = None

    def stop(self):
        self.end_time = time.perf_counter()

    def time(self):
        if self.start_time is None:
            raise ValueError("Benchmark has not been started.")
        if self.end_time is None:
            raise ValueError("Benchmark has not been stopped.")
        return self.end_time - self.start_time

    def print(self):
        elapsed_time = self.time()
        print(f"Elapsed time: {elapsed_time:.6f} seconds")