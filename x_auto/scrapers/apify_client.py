"""
Integration with the Apify actor `scraper_one/x-profile-posts-scraper`.
"""

from typing import Any, Dict, List, Optional


def fetch_recent_posts(
    apify_token: str,
    handle: str,
    since_id: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    Invoke the Apify actor to fetch recent posts for a profile handle.

    Args:
        apify_token: Apify API token used for authentication.
        handle: X profile handle to scrape.
        since_id: Optional post ID to fetch posts newer than this value.
        limit: Maximum number of posts to request.

    Returns:
        A list of normalized post dictionaries including id, text, timestamps, and URLs.
    """
    raise NotImplementedError("Apify scraping is not yet implemented.")
