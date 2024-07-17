import requests
import redis
from functools import wraps
from typing import Callable

# Initialize Redis client
redis_client = redis.Redis()

def cache_result(expiration: int):
    """Decorator to cache the result of a function with a given expiration time"""
    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(*args, **kwargs):
            url = args[0]
            cache_key = f"cache:{url}"
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return cached_result.decode('utf-8')
            result = method(*args, **kwargs)
            redis_client.setex(cache_key, expiration, result)
            return result
        return wrapper
    return decorator

def count_access(method: Callable) -> Callable:
    """Decorator to count how many times a URL is accessed"""
    @wraps(method)
    def wrapper(*args, **kwargs):
        url = args[0]
        count_key = f"count:{url}"
        redis_client.incr(count_key)
        return method(*args, **kwargs)
    return wrapper

@cache_result(expiration=10)
@count_access
def get_page(url: str) -> str:
    """Get the HTML content of a URL"""
    response = requests.get(url)
    return response.text

if __name__ == "__main__":
    # Example usage
    test_url = "http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.example.com"
    print(get_page(test_url))
    print(redis_client.get(f"count:{test_url}"))
