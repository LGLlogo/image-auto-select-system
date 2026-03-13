import time
import random


def retry(func, retries=5, base_delay=1):
    for attempt in range(retries):

        try:
            return func()
        except Exception as e:
            if attempt == retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            delay += random.uniform(0, 0.5)
            print(f"Retry in {delay:.2f}s")
            time.sleep(delay)
