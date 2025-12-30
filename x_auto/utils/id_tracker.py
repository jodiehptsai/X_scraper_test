"""
Helpers for tracking last-seen post IDs per profile to avoid duplicate replies.
"""

from typing import Dict

_LAST_SEEN_CACHE: Dict[str, str] = {}


def get_last_seen_id(handle: str) -> str:
    """
    Retrieve the last processed post ID for a given handle.

    Args:
        handle: X profile handle identifier.

    Returns:
        The last seen post ID string, or an empty string if none is stored.
    """
    return _LAST_SEEN_CACHE.get(handle, "")


def update_last_seen_id(handle: str, post_id: str) -> None:
    """
    Update the stored last seen post ID for a given handle.

    Args:
        handle: X profile handle identifier.
        post_id: The newest processed post ID.

    Returns:
        None. Updates the in-memory cache; callers may persist separately.
    """
    _LAST_SEEN_CACHE[handle] = post_id
