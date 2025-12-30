"""
Utility script to post a single reply to an X (Twitter) post.

Designed for expansion: it accepts a post URL (or ID) and reply text, loads
credentials from the environment, and delegates to the reusable X API client.

Usage:
    python reply_once.py --url https://x.com/HsinpeiT66729/status/1998986981787979991 --text "test"

Environment:
    - X_API_KEY
    - X_API_SECRET
    - X_ACCESS_TOKEN
    - X_ACCESS_TOKEN_SECRET

In the future, the post URL/ID can be sourced directly from the Apify scraper
output instead of CLI flags.
"""

from __future__ import annotations

import argparse
import os
import re
from typing import Any, Dict

from dotenv import load_dotenv

from x_auto.x_api.x_client import post_reply


def load_env() -> None:
    """
    Load environment variables from .env if present.
    """
    if os.path.isfile(".env"):
        load_dotenv(".env")
    elif os.path.isfile(".env.example"):
        load_dotenv(".env.example")


def extract_post_id(post_url_or_id: str) -> str:
    """
    Extract the tweet ID from a full URL or return the provided ID directly.

    Args:
        post_url_or_id: Full X post URL (e.g., https://x.com/.../status/123) or a raw ID.

    Returns:
        The tweet ID string.

    Raises:
        ValueError: If no ID can be parsed from the input.
    """
    # If it looks like a numeric ID already, return as-is.
    if post_url_or_id.isdigit():
        return post_url_or_id

    match = re.search(r"status/(\d+)", post_url_or_id)
    if match:
        return match.group(1)

    raise ValueError("Unable to parse tweet ID from input.")


def send_reply(post_url_or_id: str, text: str) -> Dict[str, Any]:
    """
    Post a reply to the specified X post.

    Args:
        post_url_or_id: Full X post URL or tweet ID.
        text: Reply body to publish.

    Returns:
        Parsed JSON response from the X API.
    """
    tweet_id = extract_post_id(post_url_or_id)
    return post_reply(text=text, in_reply_to_post_id=tweet_id)


def main() -> None:
    """
    CLI entrypoint for sending a single reply.
    """
    parser = argparse.ArgumentParser(description="Post a reply to an X post.")
    parser.add_argument(
        "--url",
        dest="post_url",
        default="https://x.com/HsinpeiT66729/status/1998986981787979991",
        help="Full X post URL or tweet ID.",
    )
    parser.add_argument(
        "--text",
        dest="text",
        default="test",
        help="Reply text to post.",
    )
    args = parser.parse_args()

    load_env()
    response = send_reply(args.post_url, args.text)
    print("Reply sent. Response:")
    print(response)


if __name__ == "__main__":
    main()
