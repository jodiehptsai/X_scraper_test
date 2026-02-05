#!/usr/bin/env python3
"""
檢查時間戳詳情
"""
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from x_auto.scrapers.apify_client import fetch_posts

load_dotenv()

handles = ["BensonTWN"]
posts = fetch_posts(handles, max_items=20)

print("=" * 70)
print(f"檢查 @{handles[0]} 的貼文時間戳")
print("=" * 70)
print(f"現在時間 (UTC): {datetime.now(tz=timezone.utc)}")
print()

for i, post in enumerate(posts[:10], 1):
    text = (post.get("text") or post.get("postText") or "")[:60]
    created_at = post.get("createdAt", "")
    ts = post.get("timestamp")

    print(f"{i}. createdAt: {created_at}")
    print(f"   timestamp: {ts}")

    if ts:
        try:
            dt = datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc)
            age = datetime.now(tz=timezone.utc) - dt
            print(f"   時間: {dt}")
            print(f"   距今: {age.total_seconds() / 3600:.1f} 小時")
        except Exception as e:
            print(f"   錯誤: {e}")
    else:
        print(f"   ⚠️  沒有 timestamp")

    print(f"   內容: {text}...")
    print()
