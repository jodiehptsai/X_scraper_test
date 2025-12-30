"""
Simple rate-limiting helpers to prevent API overuse.
"""

import time
from typing import Callable


def throttle(delay_seconds: float) -> Callable:
    """
    Decorator-style throttle to pause between function executions.

    Args:
        delay_seconds: Seconds to sleep before calling the wrapped function.

    Returns:
        A wrapper function that enforces the delay.
    """

    def decorator(func: Callable) -> Callable:
        def wrapped(*args, **kwargs):
            time.sleep(delay_seconds)
            return func(*args, **kwargs)

        return wrapped

    return decorator
