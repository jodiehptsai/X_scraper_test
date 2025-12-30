"""
Logger factory for consistent application logging.
"""

import logging
from typing import Any


def get_logger(name: str) -> Any:
    """
    Configure and return a logger instance.

    Args:
        name: Logger name, typically __name__ from the caller.

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
