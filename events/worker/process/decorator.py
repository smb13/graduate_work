from functools import wraps


def coroutine(func: callable) -> callable:
    @wraps(func)
    def inner(*args, **kwargs) -> callable:
        fn = func(*args, **kwargs)
        next(fn)
        return fn

    return inner
