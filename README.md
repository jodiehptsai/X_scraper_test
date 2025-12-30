# X Automation Starter

This project scaffolds an automation system that reads X (Twitter) handles and reply templates from Google Sheets, scrapes recent posts with Apify, evaluates them against keyword rules, generates candidate replies, optionally routes them through human review, posts replies via the X API, and logs all activity.

## Features
- Pull profile lists and templates from Google Sheets.
- Scrape recent posts via the Apify `scraper_one/x-profile-posts-scraper` actor.
- Score posts with keyword matching to decide whether to reply.
- Generate reply text from templates or dynamic builders.
- Optional human review via chat or Sheets before posting.
- Post replies through the X API.
- Log every step back to Google Sheets.
- Run on schedules (cron, GitHub Actions, or Apify Actor runner).

## Setup
1) Create a Python 3.10+ virtual environment.  
2) Install dependencies: `pip install -r requirements.txt`.  
3) Copy `.env.example` to `.env` and fill in credentials.  
4) Ensure the Google service account has access to the target Sheets.  
5) Configure Apify token and X API credentials in the environment.  
6) Run the orchestrator: `python main.py`.

## Structure
- `x_auto/config`: Environment loading and credential helpers.
- `x_auto/sheets`: Google Sheets read/write utilities.
- `x_auto/scrapers`: Apify integration for fetching posts.
- `x_auto/matcher`: Keyword detection, scoring, and template selection.
- `x_auto/reply_engine`: Reply message construction.
- `x_auto/x_api`: X API client for posting replies.
- `x_auto/workflow`: End-to-end pipeline orchestration.
- `x_auto/utils`: Shared helpers (logging, rate limiting, ID tracking).
- `docs/architecture.md`: High-level flow description.

## Next Steps
- Implement each stub with real API calls and business logic.
- Add tests around scoring, template selection, and posting safety checks.
- Wire the scheduler (cron, GitHub Actions, or Apify Runner) to call `main.py`.
