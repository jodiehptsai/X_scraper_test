#!/usr/bin/env python3
"""
測試新的 searchTerms + 日期篩選實作
驗證 API 層級的日期過濾是否有效
"""
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from scrapers.apify_client import fetch_posts

load_dotenv()

# 計算日期範圍（過去 1 天）
lookback_days = 1
end_date = datetime.now(tz=timezone.utc)
start_date = end_date - timedelta(days=lookback_days)
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

print("=" * 70)
print("測試 searchTerms + Twitter 查詢語法日期篩選")
print("=" * 70)
print(f"目標日期範圍: {start_date_str} 到 {end_date_str} ({lookback_days} 天)")
print()

# 測試單一帳號
handles = ["BensonTWN"]
print(f"查詢語法: from:{handles[0]} since:{start_date_str} until:{end_date_str}")
print()

print(f"正在抓取 @{handles[0]} 的貼文...")
posts = fetch_posts(
    handles,
    max_items=20,
    start_date=start_date_str,
    end_date=end_date_str
)

print(f"✓ API 回傳 {len(posts)} 篇貼文")
print()

if posts:
    print("驗證日期篩選效果：")
    print("-" * 70)

    # 檢查每篇貼文的日期
    in_range_count = 0
    out_range_count = 0

    for i, post in enumerate(posts[:10], 1):
        text = (post.get("text") or post.get("postText") or "")[:60]
        created_at = post.get("createdAt", "")
        ts = post.get("timestamp")

        # 解析時間戳
        if ts:
            try:
                dt = datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc)
                age_hours = (datetime.now(tz=timezone.utc) - dt).total_seconds() / 3600

                # 檢查是否在範圍內
                if start_date <= dt <= end_date:
                    status = "✓"
                    in_range_count += 1
                else:
                    status = "✗"
                    out_range_count += 1

                print(f"{i}. {status} {created_at} ({age_hours:.1f} 小時前)")
                print(f"   {text}...")
                print()
            except Exception as e:
                print(f"{i}. ⚠️  時間戳解析錯誤: {e}")
                print(f"   {created_at}")
                print(f"   {text}...")
                print()
        else:
            # 嘗試解析 createdAt 字串
            try:
                dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
                dt = dt.astimezone(timezone.utc)
                age_hours = (datetime.now(tz=timezone.utc) - dt).total_seconds() / 3600

                if start_date <= dt <= end_date:
                    status = "✓"
                    in_range_count += 1
                else:
                    status = "✗"
                    out_range_count += 1

                print(f"{i}. {status} {created_at} ({age_hours:.1f} 小時前)")
                print(f"   {text}...")
                print()
            except Exception as e:
                print(f"{i}. ⚠️  日期解析錯誤: {e}")
                print(f"   {created_at}")
                print(f"   {text}...")
                print()

    print("=" * 70)
    print(f"結果統計：")
    print(f"  - API 回傳總數: {len(posts)} 篇")
    print(f"  - 符合日期範圍: {in_range_count} 篇")
    print(f"  - 不符合範圍: {out_range_count} 篇")

    if len(posts) > 0:
        efficiency = (in_range_count / len(posts)) * 100
        print(f"  - 篩選效率: {efficiency:.1f}%")

        if efficiency >= 90:
            print(f"\n✓ 成功！API 層級日期篩選有效")
        elif efficiency >= 50:
            print(f"\n⚠️  部分成功，但仍有一些範圍外的貼文")
        else:
            print(f"\n✗ 失敗，API 層級日期篩選似乎無效")
else:
    print("⚠️  過去 1 天內沒有貼文，或 API 篩選過於嚴格")
