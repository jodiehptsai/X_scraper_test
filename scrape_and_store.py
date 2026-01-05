#!/usr/bin/env python3
"""
End-to-end scraping workflow: Read profiles → Scrape posts → Filter duplicates → Store in Google Sheets

This script orchestrates the complete data collection pipeline:
1. Reads X profile URLs from the configured Google Sheet (profiles worksheet)
2. Scrapes recent posts from each profile using the Apify scraper
3. Filters out posts that have already been processed (deduplication)
4. Writes new posts to the output Google Sheet

Usage:
    python scrape_and_store.py

Environment variables (新版整合):
    - GOOGLE_SHEET_ID: 單一 Google Sheet ID (所有 worksheets 都在這裡)
    - GOOGLE_WS_PROFILES: profiles worksheet 名稱 (default: "profiles")
    - GOOGLE_WS_SCRAPED_OUTPUT: scraped_output worksheet 名稱 (default: "scraped_output")
    - APIFY_TOKEN: Apify API token
    - MAX_PROFILE_URLS: Maximum number of profiles to process (default: 3)
    - POST_RESULTS_LIMIT: Maximum posts per profile (default: 3)

Legacy env vars (向後相容):
    - GOOGLE_X_ACCOUNT_ID, GOOGLE_X_PROFILES_WORKSHEET
    - GOOGLE_X_SCRAPE_OUTPUT, GOOGLE_X_SCRAPE_OUTPUT_WORKSHEET
"""

from __future__ import annotations

import os
import sys
from typing import List, Dict, Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

from scrapers.apify_client import fetch_posts_by_urls
from x_auto.sheets.client import GoogleSheetsClient, write_scraped_posts
from x_auto.workflow.pipeline import filter_already_processed


def get_profile_urls(sheet_client: GoogleSheetsClient, worksheet_name: str) -> List[str]:
    """
    Extract X profile URLs from the specified worksheet.

    Args:
        sheet_client: Authenticated GoogleSheetsClient instance
        worksheet_name: Name of the worksheet containing profiles

    Returns:
        List of X profile URLs
    """
    try:
        records = sheet_client.read_records(worksheet_name)
        profile_urls = []

        for record in records:
            # Try common column names for profile URLs
            url = (
                record.get("profile_url") or
                record.get("x_profile_url") or
                record.get("Profile URL") or
                record.get("X Profile URL") or
                record.get("X (link)") or
                record.get("url") or
                record.get("URL") or
                ""
            )

            if url and isinstance(url, str) and url.strip():
                profile_urls.append(url.strip())

        return profile_urls
    except Exception as e:
        print(f"Error reading profile URLs: {e}")
        return []


def main():
    """Execute the scraping and storage workflow."""
    print("=" * 70)
    print("X-PIGGYBACKING: SCRAPE AND STORE WORKFLOW")
    print("=" * 70)

    # Get configuration from environment (新版整合 + 向後相容)
    # 使用單一 GOOGLE_SHEET_ID，fallback 到舊的環境變數
    sheet_id = os.getenv("GOOGLE_SHEET_ID") or os.getenv("GOOGLE_X_ACCOUNT_ID")
    profiles_worksheet = os.getenv("GOOGLE_WS_PROFILES") or os.getenv("GOOGLE_X_PROFILES_WORKSHEET", "profiles")
    output_worksheet = os.getenv("GOOGLE_WS_SCRAPED_OUTPUT") or os.getenv("GOOGLE_X_SCRAPE_OUTPUT_WORKSHEET", "scraped_output")
    max_profiles = int(os.getenv("MAX_PROFILE_URLS", "3"))
    posts_per_profile = int(os.getenv("POST_RESULTS_LIMIT", "3"))

    if not sheet_id:
        print("ERROR: GOOGLE_SHEET_ID (或 GOOGLE_X_ACCOUNT_ID) is not set in .env")
        sys.exit(1)

    print(f"\nConfiguration:")
    print(f"  Sheet ID: {sheet_id}")
    print(f"  Profiles worksheet: {profiles_worksheet}")
    print(f"  Output worksheet: {output_worksheet}")
    print(f"  Max profiles to process: {max_profiles}")
    print(f"  Posts per profile: {posts_per_profile}")
    print()

    # Step 1: Connect to Google Sheets and get profile URLs
    print("[1/4] Reading profile URLs from Google Sheets...")
    try:
        sheet_client = GoogleSheetsClient(
            spreadsheet_name="X-Piggybacking Sheet",
            spreadsheet_id=sheet_id
        )
        all_profile_urls = get_profile_urls(sheet_client, profiles_worksheet)

        if not all_profile_urls:
            print("No profile URLs found in the worksheet.")
            sys.exit(0)

        # Limit to max_profiles (0 means process all)
        if max_profiles > 0:
            profile_urls = all_profile_urls[:max_profiles]
        else:
            profile_urls = all_profile_urls
        print(f"Found {len(all_profile_urls)} total profiles, processing {len(profile_urls)}")
        for i, url in enumerate(profile_urls, 1):
            print(f"  {i}. {url}")
    except Exception as e:
        print(f"ERROR: Failed to read profile URLs: {e}")
        sys.exit(1)

    # Step 2: Scrape posts from Apify
    print(f"\n[2/4] Scraping posts from {len(profile_urls)} profiles...")
    try:
        all_posts = fetch_posts_by_urls(profile_urls, results_limit=posts_per_profile)
        print(f"Scraped {len(all_posts)} total posts")
    except Exception as e:
        print(f"ERROR: Failed to scrape posts: {e}")
        sys.exit(1)

    # Step 3: Filter out already processed posts
    print(f"\n[3/4] Filtering duplicate posts...")
    try:
        # 使用同一個 sheet_client，因為現在所有 worksheets 都在同一個 Sheet 內
        new_posts = filter_already_processed(
            all_posts,
            sheet_client=sheet_client,
            output_sheet_name=output_worksheet
        )
        print(f"Found {len(new_posts)} new posts (filtered {len(all_posts) - len(new_posts)} duplicates)")
    except Exception as e:
        print(f"ERROR: Failed to filter posts: {e}")
        sys.exit(1)

    # Step 4: Write new posts to output sheet
    if new_posts:
        print(f"\n[4/4] Writing {len(new_posts)} new posts to Google Sheets...")
        try:
            count = write_scraped_posts(
                sheet_client,
                output_worksheet,
                new_posts,
                ensure_headers=True
            )
            print(f"Successfully wrote {count} posts to '{output_worksheet}'")
        except Exception as e:
            print(f"ERROR: Failed to write posts: {e}")
            sys.exit(1)
    else:
        print(f"\n[4/4] No new posts to write.")

    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  Profiles processed: {len(profile_urls)}")
    print(f"  Total posts scraped: {len(all_posts)}")
    print(f"  New posts stored: {len(new_posts)}")
    print(f"  Duplicates filtered: {len(all_posts) - len(new_posts)}")
    print()


if __name__ == "__main__":
    main()
