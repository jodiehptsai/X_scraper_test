"""
Proof-of-concept runner to fetch recent X posts via the Apify actor.

Usage:
    python poc_apify_demo.py

It loads `APIFY_TOKEN` from environment (optionally via .env/.env.example),
invokes the Apify actor for the provided profile URL, and prints a small
snapshot of the returned dataset for inspection.
"""

from __future__ import annotations

import os
from typing import List

from dotenv import load_dotenv

from scrapers.apify_client import fetch_posts


def load_env() -> None:
    """
    Load environment variables from .env, falling back to .env.example if present.
    """
    if os.path.isfile(".env"):
        load_dotenv(".env")
    elif os.path.isfile(".env.example"):
        load_dotenv(".env.example")


def run_demo(profile_urls: List[str] | None = None) -> None:
    """
    Fetch posts for the provided profile URLs and print a short summary.

    Args:
        profile_urls: Optional list of X profile URLs. Defaults to a Simon profile demo.
    """
    load_env()

    urls = profile_urls or ["https://x.com/simononchain"]
    posts = fetch_posts(urls, results_limit=10)

    print(f"Fetched {len(posts)} posts.")
    for idx, post in enumerate(posts[:3], start=1):
        post_id = post.get("id") or post.get("postId")
        text = (post.get("text") or post.get("postText") or "")[:200].replace("\n", " ")
        print(f"{idx}. id={post_id} text={text!r}")


if __name__ == "__main__":
    run_demo()
