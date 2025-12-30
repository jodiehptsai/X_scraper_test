"""
Reply generation utilities: select best template and build reply text.

This module intentionally leaves implementation details to be filled in later.
"""

from __future__ import annotations

from typing import Any, Dict, List


def select_best_template(matches: List[Dict[str, Any]], templates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Choose the most appropriate template based on keyword matches.

    Args:
        matches: Keyword match results produced by matcher.keyword_matcher.
        templates: Template rows sourced from Google Sheets.

    Returns:
        A template dictionary to be used for reply construction.
    """
    raise NotImplementedError("Template selection logic is not yet implemented.")


def build_reply_text(template: Dict[str, Any], post: Dict[str, Any], matches: List[Dict[str, Any]]) -> str:
    """
    Render a reply string using the chosen template and post context.

    Args:
        template: Template data with placeholders and metadata.
        post: The post dictionary retrieved from Apify.
        matches: Keyword matches associated with the post.

    Returns:
        Reply text ready to be sent to the X API.
    """
    raise NotImplementedError("Reply rendering is not yet implemented.")
