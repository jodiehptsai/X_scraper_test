"""
Keyword matcher for X posts using definitions pulled from Google Sheets.

This module focuses strictly on matching and scoring; it does not generate
templates or post replies.

Example:
    >>> rows = [
    ...     {"keyword": "python", "weight": 2},
    ...     {"keyword": "open source", "weight": 1},
    ... ]
    >>> matches = match_keywords("I love Python and open source", rows)
    >>> score = score_matches(matches, {"favoriteCount": 3, "replyCount": 1})
    >>> print(matches, score)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def match_keywords(text: str, keyword_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Perform case-insensitive substring matching between tweet text and keyword rows.

    Args:
        text: Tweet or post body to scan for keywords.
        keyword_rows: List of dictionaries sourced from Sheets, each expected to
            contain a "keyword" field and optionally other metadata (e.g., weight,
            template references).

    Returns:
        A list of row dictionaries that matched the provided text.
    """
    lowered = text.lower()
    matches: List[Dict[str, Any]] = []

    for row in keyword_rows:
        keyword_raw = row.get("keyword", "")
        if not isinstance(keyword_raw, str):
            continue

        keyword = keyword_raw.strip()
        if not keyword:
            continue

        if keyword.lower() in lowered:
            matches.append(row)

    return matches


def score_matches(
    matches: List[Dict[str, Any]],
    post_metadata: Optional[Dict[str, Any]] = None,
) -> int:
    """
    Calculate a relevance score by summing weights of matched rows.

    Args:
        matches: Matched keyword rows (typically output from `match_keywords`),
            each optionally containing a numeric "weight" value.
        post_metadata: Optional engagement metadata such as favoriteCount or
            replyCount; included here for callers that want to incorporate basic
            engagement into the score.

    Returns:
        Integer score derived from matched keyword weights and optional engagement.
    """
    score = 0
    for row in matches:
        weight = row.get("weight", 0)
        try:
            score += int(weight)
        except (TypeError, ValueError):
            continue

    if post_metadata:
        favorites = int(post_metadata.get("favoriteCount", 0) or 0)
        replies = int(post_metadata.get("replyCount", 0) or 0)
        score += favorites + replies

    return score
