import time
import threading


class RateLimiter:

    def __init__(self, rate_per_sec):
        self.rate = rate_per_sec
        self.interval = 1.0 / rate_per_sec
        self.lock = threading.Lock()
        self.last_time = 0

    def acquire(self):
        with self.lock:
            now = time.time()
            wait = self.interval - (now - self.last_time)

            if wait > 0:
                time.sleep(wait)

            self.last_time = time.time()
