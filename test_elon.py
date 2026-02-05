#!/usr/bin/env python3
"""
簡單測試：只抓取 @elonmusk 過去 1 天的貼文
"""
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from x_auto.scrapers.apify_client import fetch_posts

# 載入環境變數
load_dotenv()

# 計算日期範圍（過去 1 天）
end_date = datetime.now(tz=timezone.utc)
start_date = end_date - timedelta(days=1)
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

print("=" * 70)
print("測試：抓取 @BensonTWN 過去 1 天的貼文")
print("=" * 70)
print(f"日期範圍: {start_date_str} 到 {end_date_str}")
print()

# 只查詢 BensonTWN
handles = ["BensonTWN"]

print(f"正在查詢 @{handles[0]}...")
posts = fetch_posts(
    handles,
    max_items=20,
    start_date=start_date_str,
    end_date=end_date_str
)

print(f"\n✓ 抓取到 {len(posts)} 篇貼文")
print()

if posts:
    print("前 5 篇貼文預覽：")
    print("-" * 70)
    for i, post in enumerate(posts[:5], 1):
        text = (post.get("text") or post.get("postText") or "")[:100]
        created_at = post.get("createdAt", "")
        likes = post.get("likes", 0)
        print(f"\n{i}. {created_at}")
        print(f"   讚數: {likes}")
        print(f"   內容: {text}...")
else:
    print("⚠️  過去 1 天內沒有貼文")
