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


def call_history(method: Callable) -> Callable:
    """Decorator to store the history of inputs and outputs for a function"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Store input arguments and output in Redis lists"""
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        # Store the input arguments in the Redis list
        self._redis.rpush(input_key, str(args))

        # Call the original method and get the output
        output = method(self, *args, **kwargs)

        # Store the output in the Redis list
        self._redis.rpush(output_key, str(output))

        return output
    return wrapper

def replay(fn: Callable) -> None:
    """Display the history of calls of a particular function"""
    if fn is None or not hasattr(fn, '__self__'):
        return
    redis_store = getattr(fn.__self__, '_redis', None)
    if not isinstance(redis_store, redis.Redis):
        return
    fxn_name = fn.__qualname__
    in_key = '{}:inputs'.format(fxn_name)
    out_key = '{}:outputs'.format(fxn_name)
    fxn_call_count = 0
    if redis_store.exists(fxn_name) != 0:
        fxn_call_count = int(redis_store.get(fxn_name))
    print('{} was called {} times:'.format(fxn_name, fxn_call_count))
    fxn_inputs = redis_store.lrange(in_key, 0, -1)
    fxn_outputs = redis_store.lrange(out_key, 0, -1)
    for fxn_input, fxn_output in zip(fxn_inputs, fxn_outputs):
        print('{}(*{}) -> {}'.format(
            fxn_name,
            fxn_input.decode("utf-8"),
            fxn_output,
        ))


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
            """Retrieve data from Redis and optionally
            apply a conversion function
            """
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
