# Architecture Overview

This automation processes X (Twitter) profiles on a schedule to generate and optionally post replies.

## Data Flow
1) **Input**: Google Sheet rows supply profile handles, keywords, and reply templates.
2) **Scrape**: Apify actor `scraper_one/x-profile-posts-scraper` fetches recent posts per handle.
3) **Filter**: New posts are detected via stored IDs/timestamps. Keyword matching computes a score.
4) **Decide**: Scoring rules determine whether to build a candidate reply.
5) **Reply Build**: A reply template is selected or dynamically constructed.
6) **Review (optional)**: Candidate replies are sent to human review (Telegram/Slack/Sheet).
7) **Post**: Approved replies are posted via the X API.
8) **Log**: All decisions and actions are written to Google Sheets for auditing.

## Components
- `config`: Loads environment variables and credentials.
- `sheets`: Provides clients and helpers for reading profile lists, templates, and writing logs.
- `scrapers`: Wraps Apify actor calls and normalizes post payloads.
- `matcher`: Scores posts against keywords and templates.
- `reply_engine`: Builds final reply text and applies safety checks.
- `x_api`: Sends replies to X and handles errors/rate limits.
- `workflow`: Orchestrates the end-to-end pipeline and scheduling.
- `utils`: Logging, rate limiting, ID tracking, and common helpers.

## Deployment Options
- **Cron**: Run `python main.py` on a host with valid credentials.
- **GitHub Actions**: Schedule a workflow that installs dependencies and runs the pipeline.
- **Apify Actor**: Wrap `main.py` entrypoint in an Apify actor for hosted execution.
