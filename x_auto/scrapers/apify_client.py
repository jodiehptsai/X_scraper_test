"""
Connector for the Apify actor `apidojo/twitter-scraper-lite` (Twitter Scraper Unlimited).

This module provides functions to fetch posts from X (Twitter) profiles using Apify.
It is responsible solely for invoking the actor and returning raw data.
It does not implement any downstream business logic.

Features:
- Batch query multiple X accounts (no explicit limit)
- Date range filtering using Twitter query syntax (since/until)
- Supports sorting by "Latest" or "Top"

Implementation:
- Uses `searchTerms` parameter with Twitter query syntax: "from:handle since:date until:date"
- Date filtering happens at API level, reducing unnecessary data transfer

Example:
    >>> from x_auto.scrapers.apify_client import fetch_posts
    >>> posts = fetch_posts(["elonmusk", "NASA"], max_items=100)
    >>> print(len(posts))

    # With date filtering (API-level filtering using Twitter query syntax):
    >>> posts = fetch_posts(
    ...     handles=["elonmusk"],
    ...     max_items=50,
    ...     start_date="2025-01-01",
    ...     end_date="2025-12-31"
    ... )
    # This will use searchTerms: ["from:elonmusk since:2025-01-01 until:2025-12-31"]
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests

APIFY_RUN_URL = (
    "https://api.apify.com/v2/acts/"
    "apidojo~twitter-scraper-lite/run-sync-get-dataset-items"
)


def fetch_recent_posts(
    apify_token: str,
    handle: str,
    since_id: Optional[str] = None,
    limit: int = 20,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Invoke the Apify actor to fetch recent posts for a profile handle.

    Args:
        apify_token: Apify API token used for authentication.
        handle: X profile handle to scrape (without @).
        since_id: Optional post ID to fetch posts newer than this value (not used with this actor).
        limit: Maximum number of posts to request.
        start_date: Optional start date in YYYY-MM-DD format. Returns tweets after this date.
        end_date: Optional end date in YYYY-MM-DD format. Returns tweets before this date.

    Returns:
        A list of normalized post dictionaries including id, text, timestamps, and URLs.
    """
    return fetch_posts_batch(
        apify_token=apify_token,
        handles=[handle],
        max_items=limit,
        start_date=start_date,
        end_date=end_date,
    )


def fetch_posts_batch(
    apify_token: str,
    handles: List[str],
    max_items: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort: str = "Latest",
    timeout_seconds: int = 600,
) -> List[Dict[str, Any]]:
    """
    Fetch posts from multiple X profiles in a single API call.

    Args:
        apify_token: Apify API token used for authentication.
        handles: List of X handles (without @, e.g., ["elonmusk", "NASA"]).
        max_items: Maximum number of posts to retrieve in total.
        start_date: Optional start date in YYYY-MM-DD format. Returns tweets after this date.
        end_date: Optional end date in YYYY-MM-DD format. Returns tweets before this date.
        sort: Sort order - "Latest" or "Top". Default is "Latest" for more results.
        timeout_seconds: Request timeout in seconds.

    Returns:
        A list of post dictionaries as returned by the Apify actor.

    Raises:
        ValueError: If apify_token is empty.
        requests.HTTPError: If the Apify API response status is not 200.
    """
    if not apify_token:
        raise ValueError("apify_token is required but missing.")

    # Clean handles (remove @ if present)
    cleaned_handles = [h.lstrip("@") for h in handles]

    # Build payload
    payload: Dict[str, Any] = {
        "twitterHandles": cleaned_handles,
        "maxItems": max_items,
        "sort": sort,
    }

    # Add optional date filters
    if start_date:
        payload["start"] = start_date
    if end_date:
        payload["end"] = end_date

    params = {"token": apify_token}

    response = requests.post(
        APIFY_RUN_URL, params=params, json=payload, timeout=timeout_seconds
    )
    if not 200 <= response.status_code < 300:
        message = (
            f"Apify request failed with status {response.status_code}: "
            f"{response.text}"
        )
        raise requests.HTTPError(message, response=response)

    return response.json()


def fetch_posts_from_env(
    handles: List[str],
    max_items: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort: str = "Latest",
    timeout_seconds: int = 600,
) -> List[Dict[str, Any]]:
    """
    Fetch posts using APIFY_TOKEN from environment variables.

    This is a convenience function that reads the token from the environment.

    Args:
        handles: List of X handles (without @, e.g., ["elonmusk", "NASA"]).
        max_items: Maximum number of posts to retrieve in total.
        start_date: Optional start date in YYYY-MM-DD format. Returns tweets after this date.
        end_date: Optional end date in YYYY-MM-DD format. Returns tweets before this date.
        sort: Sort order - "Latest" or "Top". Default is "Latest" for more results.
        timeout_seconds: Request timeout in seconds.

    Returns:
        A list of post dictionaries as returned by the Apify actor.

    Raises:
        ValueError: If APIFY_TOKEN environment variable is missing.
        requests.HTTPError: If the Apify API response status is not 200.
    """
    token = os.getenv("APIFY_TOKEN")
    if not token:
        raise ValueError("APIFY_TOKEN environment variable is required but missing.")

    return fetch_posts_batch(
        apify_token=token,
        handles=handles,
        max_items=max_items,
        start_date=start_date,
        end_date=end_date,
        sort=sort,
        timeout_seconds=timeout_seconds,
    )


# ---------------------------------------------------------------------------
# Primary API functions (used by workflow modules)
# These use Twitter query syntax with searchTerms for advanced filtering
# ---------------------------------------------------------------------------


def fetch_posts(
    handles: List[str],
    max_items: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort: str = "Latest",
    timeout_seconds: int = 600,
) -> List[Dict[str, Any]]:
    """
    Call the Apify actor to retrieve posts for the given X handles.

    Uses Twitter query syntax with searchTerms for efficient date filtering at API level.
    If dates are provided, constructs queries like: "from:handle since:YYYY-MM-DD until:YYYY-MM-DD"

    Args:
        handles: List of X handles (without @, e.g., ["elonmusk", "NASA"]).
        max_items: Maximum number of posts to retrieve in total.
        start_date: Optional start date in YYYY-MM-DD format. Returns tweets on/after this date.
        end_date: Optional end date in YYYY-MM-DD format. Returns tweets on/before this date.
        sort: Sort order - "Latest" or "Top". Default is "Latest" for more results.
        timeout_seconds: Request timeout in seconds.

    Returns:
        A list of post dictionaries as returned by the Apify actor.
        When date filtering is applied, only posts within the date range are returned.

    Raises:
        ValueError: If the APIFY_TOKEN environment variable is missing.
        requests.HTTPError: If the Apify API response status is not 200.
    """
    token = os.getenv("APIFY_TOKEN")
    if not token:
        raise ValueError("APIFY_TOKEN environment variable is required but missing.")

    # Build search terms with Twitter query syntax for date filtering
    # Twitter syntax: "from:handle since:YYYY-MM-DD until:YYYY-MM-DD"
    # Add filters to exclude replies and retweets at API level
    search_terms = []
    for handle in handles:
        if start_date and end_date:
            # Use Twitter query syntax with date range
            query = f"from:{handle} since:{start_date} until:{end_date}"
        else:
            # Simple query without date filtering
            query = f"from:{handle}"

        # Add filters to exclude replies and retweets
        # -filter:replies = exclude replies
        # -filter:retweets = exclude native retweets (simple retweets without comments)
        # Note: This keeps quote tweets (retweets with comments) which are considered original content
        query += " -filter:replies -filter:retweets"

        search_terms.append(query)

    # Build payload with searchTerms (instead of twitterHandles)
    payload: Dict[str, Any] = {
        "searchTerms": search_terms,
        "maxItems": max_items,
        "sort": sort,
    }
    # Note: Date filtering is now embedded in searchTerms, no separate start/end parameters

    params = {"token": token}

    response = requests.post(
        APIFY_RUN_URL, params=params, json=payload, timeout=timeout_seconds
    )
    if not 200 <= response.status_code < 300:
        message = (
            f"Apify request failed with status {response.status_code}: "
            f"{response.text}"
        )
        raise requests.HTTPError(message, response=response)

    return response.json()


def fetch_posts_by_urls(
    profile_urls: List[str],
    results_limit: int = 20,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    timeout_seconds: int = 600,
) -> List[Dict[str, Any]]:
    """
    Backward compatible function that accepts profile URLs instead of handles.

    Args:
        profile_urls: List of full X profile URLs (e.g., https://x.com/handle).
        results_limit: Maximum number of posts to retrieve.
        start_date: Optional start date in YYYY-MM-DD format.
        end_date: Optional end date in YYYY-MM-DD format.
        timeout_seconds: Request timeout in seconds.

    Returns:
        A list of post dictionaries as returned by the Apify actor.
    """
    # Extract handles from URLs
    handles = []
    for url in profile_urls:
        # Handle both x.com and twitter.com URLs
        url = url.rstrip("/")
        handle = url.split("/")[-1]
        # Remove @ if present
        handle = handle.lstrip("@")
        handles.append(handle)

    return fetch_posts(
        handles=handles,
        max_items=results_limit,
        start_date=start_date,
        end_date=end_date,
        timeout_seconds=timeout_seconds,
    )
