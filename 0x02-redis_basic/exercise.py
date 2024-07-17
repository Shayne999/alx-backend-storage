#!/usr/bin/env python3
"""Creates a Cache class."""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Decorator to count calls to a method"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Increment the count for the method and call the original method"""
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


class Cache:
    def __init__(self):
        """Initialize the Cache instance"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store the input data in Redis with a
        random key and return the key
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
            """Retrieve data from Redis and optionally apply a conversion function"""
            data = self._redis.get(key)
            if data is not None and fn is not None:
                return fn(data)
            return data

    def get_str(self, key: str) -> Optional[str]:
        """Retrieve data from Redis and convert it to a string"""
        data = self.get(key, fn=lambda d: d.decode("utf-8"))
        return data

    def get_int(self, key: str) -> Optional[int]:
        """Retrieve data from Redis and convert it to an integer"""
        data = self.get(key, fn=int)
        return data


# if __name__ == "__main__":
#     cache = Cache()

#     data = b"hello"
#     key = cache.store(data)
#     print(key)

#     local_redis = redis.Redis()
#     print(local_redis.get(key))
