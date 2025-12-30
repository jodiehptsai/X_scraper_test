"""
Scrape X posts from profile URLs listed in Google Sheets and filter them via LLM.

Workflow:
1) Read profile URLs from header columns `X(handle)` / `X(link)` in the profiles worksheet.
2) Read a decision prompt from the "prompts" worksheet (first row/column or a
   "prompt" column if present).
3) Fetch recent posts for each profile via the Apify actor.
4) Send post text to the ChatGPT API with the decision prompt to get a yes/no.
5) Print or return posts that satisfy the requirement.

This module focuses on scraping and LLM-based filtering, leaving reply/posting
to other modules.
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

from scrapers.apify_client import fetch_posts
from x_auto.sheets.client import GoogleSheetsClient


def load_env() -> None:
    """Load environment variables from .env if present."""
    if os.path.isfile(".env"):
        load_dotenv(".env")
    elif os.path.isfile(".env.example"):
        load_dotenv(".env.example")


def get_profile_urls(sheet_client: GoogleSheetsClient, sheet_name: str = "profiles") -> List[str]:
    """
    Extract profile URLs using header columns `X(handle)` / `X(link)` or the 5th column.

    Args:
        sheet_client: Authenticated GoogleSheetsClient instance.
        sheet_name: Worksheet name containing profile rows.

    Returns:
        List of validated X profile URLs.
    """
    worksheet_name = os.getenv("GOOGLE_X_PROFILES_WORKSHEET", sheet_name)
    try:
        worksheet = sheet_client.get_sheet(worksheet_name)
    except RuntimeError:
        variants = {worksheet_name.strip(), f"{worksheet_name} ", worksheet_name}
        last_exc: Optional[Exception] = None
        for candidate in variants:
            if not candidate:
                continue
            try:
                worksheet = sheet_client.get_sheet(candidate)
                break
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
        else:
            raise RuntimeError(f"Worksheet '{worksheet_name}' not found.") from last_exc

    urls: List[str] = []
    def normalize_links(raw: str) -> List[str]:
        cleaned: List[str] = []
        # Split on common separators (whitespace, commas, pipes, newlines)
        parts = re.split("[\\s,|]+", raw)
        for part in parts:
            p = part.replace("\u00a0", " ").strip().strip('"').strip("'")
            if not p or p.lower() in {"n/a", "na", "(full link not provided)"}:
                continue
            # Normalize twitter.com → x.com
            p = p.replace("twitter.com", "x.com")
            # Add protocol if missing
            if p.startswith("x.com/") or p.startswith("www.x.com/"):
                p = "https://" + p
            if not p.startswith("http"):
                continue
            cleaned.append(p)
        return cleaned

    def is_valid(url: str) -> bool:
        cleaned = url.replace("\u00a0", " ").strip()
        if "x.com/" not in cleaned:
            return False
        if cleaned.startswith("http://"):
            cleaned = "https://" + cleaned[len("http://") :]
        # Accept any https URL containing x.com with no spaces.
        return cleaned.startswith("https://") and ("x.com/" in cleaned) and (" " not in cleaned)

    try:
        records = worksheet.get_all_records()
        for row in records:
            handle = row.get("X(handle)") or row.get("X handle") or row.get("handle")
            link = row.get("X(link)") or row.get("X link") or row.get("link")
            handle = (handle or "").strip().lstrip("@")
            link = (link or "").strip()

            if link:
                urls.extend(normalize_links(link))
            if handle:
                urls.append(f"https://x.com/{handle}")
    except Exception:
        records = None

    # Fallback if headers are not unique or URLs are empty: use 5th column (index 4).
    if not urls:
        values = worksheet.get_all_values()
        if values:
            for row in values[1:]:
                if len(row) > 4 and row[4].strip():
                    urls.extend(normalize_links(row[4].strip()))

    # Deduplicate and validate.
    seen = set()
    valid_urls: List[str] = []
    for u in urls:
        if not is_valid(u):
            continue
        if u in seen:
            continue
        seen.add(u)
        valid_urls.append(u)

    if len(valid_urls) != len(urls):
        print(f"Filtered out {len(urls) - len(valid_urls)} invalid profile URLs.")
    return valid_urls


def is_recent_post(post: Dict[str, Any], days: int = 30) -> bool:
    """
    Check whether a post's timestamp falls within the last N days.

    Args:
        post: Post dictionary (expects a 'timestamp' field in milliseconds).
        days: Window size in days to treat as recent.

    Returns:
        True if timestamp is within the window; False otherwise.
    """
    ts = post.get("timestamp")
    if ts is None:
        return False
    try:
        ts_dt = datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc)
    except Exception:
        return False
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=days)
    return ts_dt >= cutoff


def merge_threaded_posts(posts: List[Dict[str, Any]], window_ms: int = 120_000) -> List[Dict[str, Any]]:
    """
    Merge posts (including replies) from the same profile that belong to the same conversation
    and occur within a short window (default 2 minutes).

    Args:
        posts: List of post dicts for a single profile.
        window_ms: Time window in milliseconds to merge contiguous posts.

    Returns:
        A list of merged post dictionaries.
    """
    # Group by conversation id (fallback to post id if missing).
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for p in posts:
        cid = str(p.get("conversationId") or p.get("postId") or p.get("id") or "")
        groups.setdefault(cid, []).append(p)

    merged_all: List[Dict[str, Any]] = []
    for group in groups.values():
        posts_with_ts = [p for p in group if p.get("timestamp") is not None]
        posts_no_ts = [p for p in group if p.get("timestamp") is None]

        merged: List[Dict[str, Any]] = []
        for p in sorted(posts_with_ts, key=lambda x: x["timestamp"]):
            if not merged:
                merged.append(p)
                continue
            prev = merged[-1]
            if p["timestamp"] - prev["timestamp"] <= window_ms:
                # Merge content fields and track IDs/URLs.
                prev_text = prev.get("text") or prev.get("postText") or ""
                new_text = (p.get("text") or p.get("postText") or "")
                prev["text"] = (prev_text + " " + new_text).strip()
                # Concatenate IDs and post URLs to retain references.
                pid = prev.get("postId") or prev.get("id") or ""
                nid = p.get("postId") or p.get("id") or ""
                if nid and nid not in pid:
                    prev["postId"] = f"{pid},{nid}".strip(",")
                purl = prev.get("postUrl") or prev.get("url") or ""
                nurl = p.get("postUrl") or p.get("url") or ""
                if nurl and nurl not in purl:
                    prev["postUrl"] = f"{purl} {nurl}".strip()
            else:
                merged.append(p)

        merged.extend(posts_no_ts)
        merged_all.extend(merged)

    return merged_all


def is_reply(post: Dict[str, Any]) -> bool:
    """
    Determine if a post is a reply rather than a root/original post.

    Heuristics:
        - conversationId present and different from post id
        - presence of reply-specific fields like inReplyTo* keys
    """
    post_id = post.get("postId") or post.get("id")
    conv_id = post.get("conversationId")
    if conv_id and post_id and str(conv_id) != str(post_id):
        return True
    for key in ("inReplyToStatusId", "inReplyToPostId", "inReplyTo", "parentPostId"):
        if post.get(key):
            return True
    return False


def get_prompt(sheet_client: GoogleSheetsClient, sheet_name: str = "prompts") -> str:
    """
    Retrieve the decision prompt from the prompts worksheet.

    Strategy:
        - If the sheet has headers and a "prompt" column, use the first row's value.
        - Otherwise, use the first cell.

    Args:
        sheet_client: Authenticated GoogleSheetsClient instance.
        sheet_name: Worksheet name containing the prompt.

    Returns:
        Prompt string to send to the ChatGPT API.

    Raises:
        RuntimeError: If no prompt can be found.
    """
    worksheet = sheet_client.get_sheet(sheet_name)
    records = worksheet.get_all_records()
    if records and "prompt" in records[0] and records[0]["prompt"]:
        return str(records[0]["prompt"])

    values = worksheet.get_all_values()
    if values and values[0] and values[0][0]:
        return str(values[0][0])

    raise RuntimeError("No prompt found in the prompts sheet.")


def call_chatgpt(
    prompt: str,
    content: str,
    model: str = "gpt-4o-mini",
    max_tokens: int = 50,
) -> str:
    """
    Call the OpenAI Chat Completions API and return the model's content response.

    Args:
        prompt: Instruction describing acceptance criteria.
        content: Post text to evaluate.
        model: Model name to call.
        max_tokens: Maximum tokens to generate in the response.

    Returns:
        Response content string.

    Raises:
        RuntimeError: If OPENAI_API_KEY is missing or the request fails.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for ChatGPT calls.")

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": content},
        ],
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    resp = requests.post("https://api.openai.com/v1/chat/completions", json=body, headers=headers, timeout=30)
    if not resp.ok:
        raise RuntimeError(f"ChatGPT API error {resp.status_code}: {resp.text}")
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


def is_match_via_llm(prompt: str, post_text: str) -> bool:
    """
    Send post text to the LLM and interpret a yes/no style response.

    Args:
        prompt: Decision prompt.
        post_text: Text of the post.

    Returns:
        True if the response contains 'yes' (case-insensitive), otherwise False.
    """
    reply = call_chatgpt(prompt, post_text, max_tokens=10)
    return "yes" in reply.lower()


def generate_reply_recommendation(post_text: str, prompt: str) -> str:
    """
    Produce a concise, humanized reply recommendation for a given post.

    Args:
        post_text: The original X post text.
        prompt: Prompt text to guide the reply generation.

    Returns:
        A short recommendation string suitable as a draft reply.
    """
    try:
        recommendation = call_chatgpt(prompt, post_text, model="gpt-4o-mini", max_tokens=120)
        return recommendation.strip()
    except Exception:
        return "No recommendation generated."


def get_content_provided() -> str:
    """
    Load reference content from a separate Google Sheet (first column).

    Uses env:
        - GOOGLE_X_CONTENT_SHEET_ID: Spreadsheet ID holding reference content.
        - GOOGLE_X_CONTENT_WORKSHEET: Worksheet name (default: 'content').

    Returns:
        Concatenated string of non-empty first-column values.

    Raises:
        RuntimeError: If required envs are missing or sheet cannot be read.
    """
    content_sheet_id = os.getenv("GOOGLE_X_CONTENT_SHEET_ID")
    if not content_sheet_id:
        raise RuntimeError("GOOGLE_X_CONTENT_SHEET_ID is required for content lookup.")

    worksheet_name = os.getenv("GOOGLE_X_CONTENT_WORKSHEET", "content")
    client = GoogleSheetsClient(spreadsheet_name="content_sheet", spreadsheet_id=content_sheet_id)
    ws = client.get_sheet(worksheet_name)
    values = ws.col_values(1)
    # Skip header and join meaningful rows.
    content_lines = [v for v in values[1:] if v]
    if not content_lines and values:
        content_lines = [values[0]]
    if not content_lines:
        raise RuntimeError("No content found in the first column of the content sheet.")
    return "\n".join(content_lines)


def get_prompts_from_sheet() -> Dict[str, str]:
    """
    Load prompts from a dedicated prompts sheet.

    Expects columns: name, prompt (first row as header). Returns a mapping.
    Falls back to defaults if env not set or sheet unreadable.
    """
    prompts_sheet_id = os.getenv("GOOGLE_X_PROMPTS_SHEET_ID")
    if not prompts_sheet_id:
        return {}
    worksheet_name = os.getenv("GOOGLE_X_PROMPTS_WORKSHEET", "prompts")
    try:
        client = GoogleSheetsClient(spreadsheet_name="prompts_sheet", spreadsheet_id=prompts_sheet_id)
        ws = client.get_sheet(worksheet_name)
        records = ws.get_all_records()
        prompt_map: Dict[str, str] = {}
        for row in records:
            name = str(row.get("name") or "").strip()
            prompt_val = str(row.get("prompt") or "").strip()
            if name and prompt_val:
                prompt_map[name] = prompt_val
        return prompt_map
    except Exception:
        return {}


def format_timestamp(ts: Any) -> str:
    """
    Convert a millisecond timestamp to an ISO8601 string (UTC).
    """
    try:
        return datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc).isoformat()
    except Exception:
        return ""


def run_scrape_and_filter() -> List[Dict[str, Any]]:
    """
    End-to-end scraper + filter:
        - Loads env and Sheets client
        - Reads profile URLs (column 6)
        - Reads decision prompt
        - Scrapes posts via Apify
        - Filters via ChatGPT

    Returns:
        List of matched post dictionaries.
    """
    load_env()
    sheet_client = GoogleSheetsClient(spreadsheet_name=os.getenv("GOOGLE_SPREADSHEET_NAME", "Automation Config"))
    profile_urls = get_profile_urls(sheet_client)
    max_profiles = int(os.getenv("MAX_PROFILE_URLS", "0") or 0)
    batch_start = int(os.getenv("PROFILE_BATCH_START", "0") or 0)
    batch_size = int(os.getenv("PROFILE_BATCH_SIZE", "0") or 0)
    total_profiles = len(profile_urls)

    # Apply batch slicing first if batch_size is set.
    if batch_size > 0:
        profile_urls = profile_urls[batch_start : batch_start + batch_size]
    # Then apply max_profiles cap if set.
    if max_profiles > 0:
        profile_urls = profile_urls[:max_profiles]

    print(
        f"Collected {total_profiles} unique profile URLs; "
        f"processing {len(profile_urls)} (batch_start={batch_start}, batch_size={batch_size or 'all'}, "
        f"limit={max_profiles or 'all'})."
    )

    # Build LLM prompts from the prompts sheet (or defaults).
    prompt_map = get_prompts_from_sheet()
    base_prompt = prompt_map.get(
        "match_prompt",
        'You are a professional liquid fund investor, please see if this content has the similar information as the '
        '"content provided" or is related to an industry, token analysis that would help investment. '
        'Respond with "yes" or "no".',
    )
    reply_prompt = prompt_map.get(
        "reply_prompt",
        "You craft concise, human replies for a professional liquid fund account. "
        "Read the user's post and propose a short, friendly reply that adds value, "
        "acknowledges the topic, and avoids hype. Use relevant domain knowledge if helpful. "
        "Keep it under 100 words (aim for brevity). "
        "Do not include placeholders or ask for more info. Return only the reply text.",
    )

    matched: List[Dict[str, Any]] = []
    matched_with_profile: List[Dict[str, Any]] = []
    total_posts = 0
    recent_posts = 0
    reply_posts = 0
    post_limit = int(os.getenv("POST_RESULTS_LIMIT", "5") or 5)
    for idx, url in enumerate(profile_urls, start=1):
        print(f"[{idx}/{len(profile_urls)}] Fetching posts for {url}")
        posts = fetch_posts([url], results_limit=post_limit)
        total_posts += len(posts)
        lookback_days = int(os.getenv("LOOKBACK_DAYS", "30") or 30)
        recent = [p for p in posts if is_recent_post(p, days=lookback_days)]
        recent_posts += len(recent)
        replies = [p for p in recent if is_reply(p)]
        reply_posts += len(replies)
        # Merge by conversation id and 2-minute window; include originals if no replies found.
        to_merge = replies if replies else recent
        merged_recent = merge_threaded_posts(to_merge)
        for post in merged_recent:
            text = post.get("text") or post.get("postText") or ""
            if not text:
                continue
            if is_match_via_llm(base_prompt, text):
                matched.append(post)
                recommendation = generate_reply_recommendation(text, prompt=reply_prompt)
                matched_with_profile.append(
                    {
                        "profile_url": url,
                        "post": post,
                        "reply_reco": recommendation,
                        "post_id": post.get("id") or post.get("postId") or "",
                        "timestamp": post.get("timestamp"),
                    }
                )

    # For now, print a simple summary and return the matches for caller use.
    print(f"Total posts fetched: {total_posts}")
    print(f"Posts within last 30 days: {recent_posts}")
    print(f"Replies considered (<=2 min merge per author): {reply_posts}")
    print(f"Matched (LLM yes) posts: {len(matched)}")
    for idx, post in enumerate(matched, 1):
        pid = post.get("id") or post.get("postId")
        preview = (post.get("text") or post.get("postText") or "")[:140].replace("\n", " ")
        print(f"{idx}. {pid}: {preview!r}")

    # Persist matches to output sheet if configured.
    output_sheet_id = os.getenv("GOOGLE_X_SCRAPE_OUTPUT")
    output_ws_name = os.getenv("GOOGLE_X_SCRAPE_OUTPUT_WORKSHEET", "scrape_output")
    if output_sheet_id and matched_with_profile:
        try:
            out_client = GoogleSheetsClient(
                spreadsheet_name="scrape_output",
                spreadsheet_id=output_sheet_id,
            )
            ws = out_client.get_sheet(output_ws_name)
            existing = ws.get_all_values()

            def normalize_row(row: List[str]) -> List[str]:
                # Shift left if leading blanks exist.
                normalized = list(row)
                while normalized and normalized[0] == "":
                    normalized = normalized[1:]
                return normalized

            if not any(cell for r in existing for cell in r):
                ws.append_row(
                    ["profile_url", "post_content", "timestamp_ms", "reply_recommendation", "post_link"],
                    value_input_option="USER_ENTERED",
                )
                existing = ws.get_all_values()

            existing_pairs = set()
            for row in existing[1:]:
                norm = normalize_row(row)
                if len(norm) >= 3:
                    existing_pairs.add((norm[0].strip(), norm[1].strip(), norm[2].strip()))
            rows = []
            for item in matched_with_profile:
                post = item["post"]
                profile_url = (item["profile_url"] or "").strip()
                text = (post.get("text") or post.get("postText") or "").replace("\n", " ").strip()
                reply_reco = item.get("reply_reco", "")
                ts_raw = item.get("timestamp") or ""
                ts_str = str(ts_raw) if ts_raw is not None else ""
                ts_human = format_timestamp(ts_raw)
                post_id = item.get("post_id", "")
                post_link = (
                    post.get("postUrl")
                    or post.get("url")
                    or (f"https://x.com/i/web/status/{post_id}" if post_id else "")
                )
                key = (profile_url, text, ts_str)
                if key in existing_pairs:
                    continue
                rows.append([profile_url, text, ts_human, reply_reco, post_link])
            if rows:
                ws.append_rows(rows, value_input_option="USER_ENTERED", table_range="A1")
            print(f"Wrote {len(rows)} rows to output sheet '{output_ws_name}'.")
        except Exception as exc:  # noqa: BLE001
            print(f"Failed to write scrape output: {exc}")
    return matched


if __name__ == "__main__":
    run_scrape_and_filter()
