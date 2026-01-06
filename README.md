# X Automation Starter

This project automates X (Twitter) monitoring: scrapes posts from target profiles, evaluates them with AI, categorizes content, generates reply recommendations, and sends daily summaries via Telegram.

## Features
- **Profile monitoring** - Track X handles from Google Sheets
- **Apify scraping** - Fetch recent posts via `scraper_one/x-profile-posts-scraper`
- **AI-powered filtering** - LLM evaluates each post for relevance (decision recorded as 0/1)
- **Post categorization** - Auto-categorize posts (token_analysis, industry_analysis, market_comment, etc.)
- **Smart summaries** - Generate concise headlines for quick review
- **Reply generation** - AI-powered reply recommendations
- **Telegram notifications** - Daily summaries organized by category with emoji indicators
- **Google Sheets logging** - Track all posts and decisions
- **Scheduled execution** - Run on Railway, cron, or GitHub Actions

## Setup
1) Create a Python 3.11+ virtual environment
2) Install dependencies: `pip install -r requirements.txt`
3) Copy `.env.example` to `.env` and fill in credentials
4) Share your Google Sheet with the service account email (from JSON credentials)
5) Configure required env vars: `APIFY_TOKEN`, `OPENAI_API_KEY`, `GOOGLE_SHEET_ID`
6) **(Optional) Telegram notifications**:
   - Create bot via [@BotFather](https://t.me/botfather), get token
   - Get chat ID from [@userinfobot](https://t.me/userinfobot)
   - Add to `.env`: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `ENABLE_TELEGRAM_NOTIFICATIONS=true`
7) Run: `python main.py`

## Google Sheets Structure

**Single unified sheet** with these worksheets:
- `profiles` (or `Researcher`) - Input: X handles to monitor
- `prompts` (or `prompt_inuse`) - Input: LLM prompts for filtering/replies/categorization
- `all_post` - Output: All scraped posts with llm_decision (0/1), reasons, engagement metrics
- `scraped_output` - Output: Matched posts (llm_decision=1) with reply recommendations, summaries, categories

## Telegram Notifications

The system can send daily summaries of scraped posts to Telegram, organized by category with emoji indicators.

**Quick Start:**
```bash
# Test the notification system
python test_telegram_notification.py

# Run scraping with automatic notifications
ENABLE_TELEGRAM_NOTIFICATIONS=true python scrape_and_store.py
```

**Features:**
- Posts grouped by category (Token Analysis 📊, Industry Analysis 🏭, Market Comment 💬, etc.)
- Direct links to X posts
- Handles long messages by splitting into multiple parts
- Graceful handling of errors and edge cases

**Requirements:**
- Posts must have `summary` and `category` fields to appear in notifications
- Set `ENABLE_TELEGRAM_NOTIFICATIONS=true` in `.env` to enable

## Structure
- `x_auto/config` - Environment loading and credential helpers
- `x_auto/sheets` - Google Sheets read/write utilities
- `x_auto/scrapers` - Apify integration for fetching posts
- `x_auto/matcher` - Keyword detection, scoring, template selection
- `x_auto/reply_engine` - Reply message construction
- `x_auto/x_api` - X API client for posting replies
- `x_auto/notifications` - Telegram bot integration for daily summaries
- `x_auto/workflow` - End-to-end pipeline orchestration (scraping, filtering, LLM evaluation)
- `x_auto/utils` - Shared helpers (logging, rate limiting, ID tracking)
- `docs/architecture.md` - High-level flow description

## Next Steps
- Review and adjust LLM prompts in the `prompts` worksheet for optimal filtering
- Monitor API costs and performance (Apify, OpenAI usage)
- Set `ENABLE_X_POSTING=true` when ready to post live replies to X
