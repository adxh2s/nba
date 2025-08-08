from __future__ import annotations

import logging
import time
from functools import wraps


def log_function_call(logger: logging.Logger):
    """
    Decorator to log function start, completion, and elapsed time.

    Args:
        logger: Logger instance to use.

    Usage:
        @log_function_call(logger)
        def my_function():
            ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Start function '{func.__name__}'")
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info(
                f"End function '{func.__name__}' (duration {elapsed:.2f}s)"
            )
            return result

        return wrapper

    return decorator
