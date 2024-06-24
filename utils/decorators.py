import time
import logging

def log_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"Executed {func.__name__} in {end_time - start_time:.2f} seconds")
        return result
    return wrapper
