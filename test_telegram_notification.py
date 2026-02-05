#!/usr/bin/env python3
"""
Test script for Telegram Bot notification functionality.

This script creates mock post data and tests the Telegram notification
system without running the full scraping pipeline.

Usage:
    python test_telegram_notification.py
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import List, Dict, Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from x_auto.notifications.telegram_bot import send_daily_summary


def create_mock_posts() -> List[Dict[str, Any]]:
    """Create mock post data for testing."""
    mock_posts = [
        {
            "profile_url": "https://x.com/elonmusk",
            "post": {
                "text": "Bitcoin breaks through $45,000 resistance with strong volume confirmation and bullish momentum indicators.",
                "id": "1234567890",
                "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
                "author": {"userName": "elonmusk"}
            },
            "summary": "BTC breaks $45K resistance with strong volume",
            "category": "token_analysis",
            "post_id": "1234567890",
            "post_link": "https://x.com/elonmusk/status/1234567890",
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000)
        },
        {
            "profile_url": "https://x.com/VitalikButerin",
            "post": {
                "text": "Ethereum staking yields drop to 3.2% as validator count surges past 800,000 active validators.",
                "id": "1234567891",
                "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
                "author": {"userName": "VitalikButerin"}
            },
            "summary": "ETH staking yields drop to 3.2% amid validator surge",
            "category": "tokenomic_comment",
            "post_id": "1234567891",
            "post_link": "https://x.com/VitalikButerin/status/1234567891",
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000)
        },
        {
            "profile_url": "https://x.com/CryptoNews",
            "post": {
                "text": "US SEC approves new spot Bitcoin ETF framework, signaling major institutional adoption milestone.",
                "id": "1234567892",
                "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
                "author": {"userName": "CryptoNews"}
            },
            "summary": "SEC approves new Bitcoin ETF framework",
            "category": "industry_analysis",
            "post_id": "1234567892",
            "post_link": "https://x.com/CryptoNews/status/1234567892",
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000)
        },
        {
            "profile_url": "https://x.com/MarketAnalyst",
            "post": {
                "text": "Market sentiment shifts to greed as Fear & Greed Index hits 75, highest level since November 2021.",
                "id": "1234567893",
                "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
                "author": {"userName": "MarketAnalyst"}
            },
            "summary": "Market sentiment shifts to greed (index 75)",
            "category": "market_comment",
            "post_id": "1234567893",
            "post_link": "https://x.com/MarketAnalyst/status/1234567893",
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000)
        },
        {
            "profile_url": "https://x.com/BinanceNews",
            "post": {
                "text": "Binance announces new crypto savings product with competitive APY rates for multiple tokens.",
                "id": "1234567894",
                "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
                "author": {"userName": "BinanceNews"}
            },
            "summary": "Binance launches new crypto savings product",
            "category": "others",
            "post_id": "1234567894",
            "post_link": "https://x.com/BinanceNews/status/1234567894",
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000)
        }
    ]
    return mock_posts


def test_with_posts():
    """Test Telegram notification with mock posts."""
    print("=" * 70)
    print("TEST 1: Telegram notification with 5 mock posts")
    print("=" * 70)

    mock_posts = create_mock_posts()
    print(f"\nCreated {len(mock_posts)} mock posts:")
    for i, post in enumerate(mock_posts, 1):
        print(f"  {i}. [{post['category']}] {post['summary']}")

    print("\nSending to Telegram...")
    success = send_daily_summary(mock_posts)

    if success:
        print("\n✅ Test 1 PASSED: Telegram notification sent successfully")
    else:
        print("\n❌ Test 1 FAILED: Telegram notification failed")

    return success


def test_without_posts():
    """Test Telegram notification with no posts (should send 'no matches' message)."""
    print("\n" + "=" * 70)
    print("TEST 2: Telegram notification with 0 posts")
    print("=" * 70)

    print("\nSending empty list to Telegram...")
    success = send_daily_summary([])

    if success:
        print("\n✅ Test 2 PASSED: 'No matches' notification sent successfully")
    else:
        print("\n❌ Test 2 FAILED: 'No matches' notification failed")

    return success


def main():
    """Run all tests."""
    print("🤖 Telegram Bot Notification Test Suite")
    print("=" * 70)

    # Check environment variables
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    enabled = os.getenv("ENABLE_TELEGRAM_NOTIFICATIONS", "true").lower() == "true"

    print(f"\nConfiguration:")
    print(f"  TELEGRAM_BOT_TOKEN: {'✅ Set' if bot_token else '❌ Not set'}")
    print(f"  TELEGRAM_CHAT_ID: {'✅ Set' if chat_id else '❌ Not set'}")
    print(f"  ENABLE_TELEGRAM_NOTIFICATIONS: {enabled}")

    if not bot_token or not chat_id:
        print("\n❌ ERROR: Telegram credentials not configured")
        print("\nPlease set the following in your .env file:")
        print("  TELEGRAM_BOT_TOKEN=<your_bot_token>")
        print("  TELEGRAM_CHAT_ID=<your_chat_id>")
        print("\nSee .env.example for instructions on how to obtain these credentials.")
        return

    if not enabled:
        print("\n⚠️  WARNING: ENABLE_TELEGRAM_NOTIFICATIONS is set to false")
        print("   Notifications may be skipped")

    print("\n" + "=" * 70)
    print("Starting tests...")
    print("=" * 70)

    # Run tests
    results = []
    results.append(("Test 1 (with posts)", test_with_posts()))
    results.append(("Test 2 (no posts)", test_without_posts()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")

    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the logs above for details.")


if __name__ == "__main__":
    main()
