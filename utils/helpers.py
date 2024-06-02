import random
import time

def random_delay(min_delay=2, max_delay=5):
    """
    Introduces a random delay to mimic human behavior.

    Args:
        min_delay (int, optional): Minimum delay time in seconds. Defaults to 2.
        max_delay (int, optional): Maximum delay time in seconds. Defaults to 5.
    """
    time.sleep(random.uniform(min_delay, max_delay))

def get_random_user_agent():
    """
    Returns a random user agent string from a predefined list.

    Returns:
        str: A randomly selected user agent string.
    """
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36',
    ]
    return random.choice(user_agents)
