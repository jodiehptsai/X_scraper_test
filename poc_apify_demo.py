"""
Proof-of-concept runner to fetch recent X posts via the Apify actor.

Usage:
    python poc_apify_demo.py

It loads `APIFY_TOKEN` from environment (optionally via .env/.env.example),
invokes the Apify actor for the provided profile handle(s), and prints a small
snapshot of the returned dataset for inspection.

Supports:
- Batch query multiple handles
- Date range filtering with start_date/end_date
"""

from __future__ import annotations

import os
from typing import List, Optional

from dotenv import load_dotenv

from x_auto.scrapers.apify_client import fetch_posts


def load_env() -> None:
    """
    Load environment variables from .env, falling back to .env.example if present.
    """
    if os.path.isfile(".env"):
        load_dotenv(".env")
    elif os.path.isfile(".env.example"):
        load_dotenv(".env.example")


def run_demo(
    handles: List[str] | None = None,
    max_items: int = 10,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> None:
    """
    Fetch posts for the provided handles and print a short summary.

    Args:
        handles: Optional list of X handles (without @). Defaults to demo handles.
        max_items: Maximum number of posts to fetch.
        start_date: Optional start date in YYYY-MM-DD format.
        end_date: Optional end date in YYYY-MM-DD format.
    """
    load_env()

    # Default demo handles
    demo_handles = handles or ["Arthur_0x"]
    
    print(f"Fetching posts for {len(demo_handles)} handle(s): {demo_handles}")
    if start_date:
        print(f"  Start date: {start_date}")
    if end_date:
        print(f"  End date: {end_date}")
    print(f"  Max items: {max_items}")
    print()

    posts = fetch_posts(
        handles=demo_handles,
        max_items=max_items,
        start_date=start_date,
        end_date=end_date,
    )

    print(f"Fetched {len(posts)} posts.")
    for idx, post in enumerate(posts[:5], start=1):
        post_id = post.get("id") or post.get("postId") or post.get("tweetId")
        text = (post.get("text") or post.get("postText") or post.get("fullText") or "")[:200].replace("\n", " ")
        created_at = post.get("createdAt") or post.get("timestamp") or ""
        author = post.get("author", {})
        username = author.get("userName") or author.get("username") or post.get("handle") or ""
        print(f"{idx}. @{username} | {created_at}")
        print(f"   id={post_id}")
        print(f"   text={text!r}")
        print()


if __name__ == "__main__":
    run_demo()
