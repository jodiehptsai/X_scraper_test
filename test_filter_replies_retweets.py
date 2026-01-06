#!/usr/bin/env python3
"""
測試回覆和轉推過濾功能
驗證 API 層級的 -filter:replies -filter:retweets 是否有效
"""
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from scrapers.apify_client import fetch_posts
from x_auto.workflow.scrape_filter import is_reply, is_retweet

load_dotenv()

# 計算日期範圍（過去 7 天以獲得更多測試樣本）
lookback_days = 7
end_date = datetime.now(tz=timezone.utc)
start_date = end_date - timedelta(days=lookback_days)
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

print("=" * 70)
print("測試回覆和轉推過濾功能")
print("=" * 70)
print(f"目標日期範圍: {start_date_str} 到 {end_date_str} ({lookback_days} 天)")
print()

# 測試帳號（選擇一個比較活躍的帳號）
handles = ["BensonTWN"]
print(f"測試帳號: @{handles[0]}")
print(f"查詢語法: from:{handles[0]} since:{start_date_str} until:{end_date_str} -filter:replies -filter:retweets")
print()

print(f"正在抓取 @{handles[0]} 的貼文...")
posts = fetch_posts(
    handles,
    max_items=50,
    start_date=start_date_str,
    end_date=end_date_str
)

print(f"✓ API 回傳 {len(posts)} 篇貼文")
print()

if posts:
    print("驗證過濾效果：")
    print("-" * 70)

    reply_count = 0
    retweet_count = 0
    original_count = 0

    for i, post in enumerate(posts[:20], 1):
        text = (post.get("text") or post.get("postText") or "")[:80]
        created_at = post.get("createdAt", "")

        # 檢查是否為回覆
        is_reply_post = is_reply(post)
        # 檢查是否為轉推
        is_retweet_post = is_retweet(post)

        if is_reply_post:
            status = "❌ 回覆"
            reply_count += 1
        elif is_retweet_post:
            status = "❌ 轉推"
            retweet_count += 1
        else:
            status = "✓ 原創"
            original_count += 1

        print(f"{i}. {status}")
        print(f"   日期: {created_at}")
        print(f"   內容: {text}...")

        # 顯示診斷資訊
        if is_reply_post or is_retweet_post:
            conv_id = post.get("conversationId")
            post_id = post.get("postId") or post.get("id")
            in_reply_to = post.get("inReplyToStatusId") or post.get("inReplyToPostId")
            is_rt = post.get("isRetweet")
            print(f"   [診斷] conversationId={conv_id}, postId={post_id}, inReplyTo={in_reply_to}, isRetweet={is_rt}")

        print()

    print("=" * 70)
    print(f"結果統計：")
    print(f"  - API 回傳總數: {len(posts)} 篇")
    print(f"  - 原創貼文: {original_count} 篇")
    print(f"  - 回覆（應為 0）: {reply_count} 篇")
    print(f"  - 轉推（應為 0）: {retweet_count} 篇")

    if len(posts) > 0:
        filter_effectiveness = (original_count / min(len(posts), 20)) * 100
        print(f"  - 過濾效率: {filter_effectiveness:.1f}%")

        if reply_count == 0 and retweet_count == 0:
            print(f"\n✓ 成功！API 層級過濾完全有效，沒有回覆和轉推")
        elif reply_count + retweet_count <= 2:
            print(f"\n⚠️  大致成功，但有少量回覆或轉推漏網")
        else:
            print(f"\n✗ 注意：API 層級過濾似乎不完全有效")
            print(f"   建議：後處理過濾層會作為安全網過濾這些內容")
else:
    print(f"⚠️  過去 {lookback_days} 天內沒有貼文")
