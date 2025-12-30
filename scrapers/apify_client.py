"""
Connector for the Apify actor `scraper_one/x-profile-posts-scraper`.

This module is responsible solely for invoking the actor and returning raw data.
It does not implement any downstream business logic.

Example:
    >>> from scrapers.apify_client import fetch_posts
    >>> posts = fetch_posts(["https://x.com/example_user"], results_limit=10)
    >>> print(len(posts))
"""

from __future__ import annotations

import os
from typing import Dict, List

import requests

APIFY_RUN_URL = (
    "https://api.apify.com/v2/acts/"
    "scraper_one~x-profile-posts-scraper/run-sync-get-dataset-items"
)


def fetch_posts(
    profile_urls: List[str], results_limit: int = 20, timeout_seconds: int = 600
) -> List[Dict]:
    """
    Call the Apify actor to retrieve recent posts for the given X profile URLs.

    Args:
        profile_urls: List of full X profile URLs (e.g., https://x.com/handle).
        results_limit: Maximum number of posts to retrieve per profile.

    Returns:
        A list of post dictionaries as returned by the Apify actor.

    Raises:
        ValueError: If the APIFY_TOKEN environment variable is missing.
        requests.HTTPError: If the Apify API response status is not 200.
    """
    token = os.getenv("APIFY_TOKEN")
    if not token:
        raise ValueError("APIFY_TOKEN environment variable is required but missing.")

    payload = {"profileUrls": profile_urls, "resultsLimit": results_limit}
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
