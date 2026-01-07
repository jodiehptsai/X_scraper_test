#!/usr/bin/env python3
"""
測試日期過濾功能
"""
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from x_auto.scrapers.apify_client import fetch_posts
from x_auto.workflow.scrape_filter import is_recent_post

load_dotenv()

# 計算日期範圍（過去 1 天）
lookback_days = 1
end_date = datetime.now(tz=timezone.utc)
start_date = end_date - timedelta(days=lookback_days)
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

print("=" * 70)
print("測試日期過濾")
print("=" * 70)
print(f"目標日期範圍: {start_date_str} 到 {end_date_str} ({lookback_days} 天)")
print()

handles = ["BensonTWN"]
print(f"查詢 @{handles[0]}...")

# 抓取貼文（Apify 可能不會過濾日期）
posts = fetch_posts(
    handles,
    max_items=20,
    start_date=start_date_str,
    end_date=end_date_str
)

print(f"✓ API 回傳 {len(posts)} 篇貼文\n")

# 使用模組的日期過濾函數（已修復支援 createdAt）
recent = [p for p in posts if is_recent_post(p, days=lookback_days)]

print(f"日期過濾結果:")
print(f"  - API 回傳: {len(posts)} 篇")
print(f"  - 符合日期範圍: {len(recent)} 篇")
print(f"  - 過濾掉: {len(posts) - len(recent)} 篇")
print()

if recent:
    print(f"✓ 過去 {lookback_days} 天內的貼文:")
    print("-" * 70)
    for i, post in enumerate(recent[:5], 1):
        text = (post.get("text") or post.get("postText") or "")[:80]
        created_at = post.get("createdAt", "")
        ts = post.get("timestamp")
        if ts:
            dt = datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc)
            age_hours = (datetime.now(tz=timezone.utc) - dt).total_seconds() / 3600
            print(f"{i}. {created_at} ({age_hours:.1f} 小時前)")
        else:
            print(f"{i}. {created_at}")
        print(f"   {text}...")
        print()
else:
    print(f"⚠️  過去 {lookback_days} 天內沒有貼文")
