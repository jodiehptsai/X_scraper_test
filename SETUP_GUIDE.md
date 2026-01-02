# Setup Guide - X-piggybacking

This guide will help you obtain all the necessary credentials and configure the `.env` file.

## Prerequisites
- Python 3.10+ (currently using 3.9.6, should work)
- Google account
- Apify account
- X (Twitter) Developer account (for posting)
- OpenAI account (for AI-powered replies)

---

## Step 1: Apify Configuration

### What is Apify?
Apify is a web scraping platform that we use to fetch X (Twitter) posts.

### How to get your Apify token:
1. Go to https://console.apify.com/
2. Sign up or log in
3. Navigate to **Settings** → **Integrations**
4. Copy your **API token**
5. Paste it in `.env` as `APIFY_TOKEN`

**Cost:** Apify has a free tier with limited usage. Check their pricing for production use.

---

## Step 2: Google Service Account Setup

### Why do we need this?
The Google Service Account allows the script to read/write Google Sheets without manual authentication.

### Steps to create a Service Account:

1. **Go to Google Cloud Console**
   - https://console.cloud.google.com/

2. **Create or select a project**
   - Click the project dropdown at the top
   - Click "New Project" or select existing one

3. **Enable Google Sheets API**
   - Go to **APIs & Services** → **Library**
   - Search for "Google Sheets API"
   - Click **Enable**

4. **Enable Google Drive API** (also required)
   - Search for "Google Drive API"
   - Click **Enable**

5. **Create Service Account**
   - Go to **IAM & Admin** → **Service Accounts**
   - Click **Create Service Account**
   - Name: `x-piggybacking-bot` (or any name)
   - Click **Create and Continue**
   - Skip role assignment (click Continue)
   - Click **Done**

6. **Create JSON Key**
   - Click on the service account you just created
   - Go to **Keys** tab
   - Click **Add Key** → **Create new key**
   - Choose **JSON** format
   - Click **Create**
   - A JSON file will download automatically

7. **Configure the path**
   - Move the downloaded JSON file to a secure location
   - Example: `/Users/weilinchen/credentials/x-piggybacking-service-account.json`
   - Update `GOOGLE_SERVICE_ACCOUNT_PATH` in `.env` with this path

8. **Share your Google Sheets with the Service Account**
   - Open the JSON file and find the `client_email` field
   - It looks like: `x-piggybacking-bot@your-project.iam.gserviceaccount.com`
   - Open each Google Sheet you want the bot to access
   - Click **Share** button
   - Paste the service account email
   - Give **Editor** permissions
   - Click **Send** (uncheck "Notify people")

---

## Step 3: Google Sheets Setup

### Required Sheets:

You need to create or identify the following Google Sheets:

#### 1. **Main Account Sheet** (`GOOGLE_X_ACCOUNT_ID`)
- Contains profile lists and main configuration
- Create a worksheet named **"Researcher"** (or update `GOOGLE_X_PROFILES_WORKSHEET`)
- Recommended columns in "Researcher" worksheet:
  - Column A: Profile Name
  - Column B: X Profile URL (e.g., `https://x.com/username`)
  - Column C: Status
  - Column D: Notes
  - Column E: X Profile URL (alternative location - code checks both)

#### 2. **Content Sheet** (`GOOGLE_X_CONTENT_SHEET_ID`)
- Stores content templates and keywords
- Create worksheet: **Sheet1** (or update `GOOGLE_X_CONTENT_WORKSHEET`)
- Recommended structure:
  - Keywords sheet with columns: `keyword`, `weight`, `template_id`
  - Templates sheet with columns: `template_id`, `template_text`, `category`

#### 3. **Scrape Output Sheet** (`GOOGLE_X_SCRAPE_OUTPUT`)
- Where scraped posts will be logged
- Create worksheet: **scraped_output** (or update `GOOGLE_X_SCRAPE_OUTPUT_WORKSHEET`)
- The script will write scraped post data here

#### 4. **Prompts Sheet** (`GOOGLE_X_PROMPTS_SHEET_ID`)
- Contains prompts for AI reply generation
- Create worksheet: **prompt_inuse**
- Recommended columns: `prompt_id`, `prompt_text`, `use_case`

### How to get Sheet IDs:
1. Open a Google Sheet in your browser
2. Look at the URL: `https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit`
3. Copy the long string between `/d/` and `/edit`
4. Paste it in the corresponding variable in `.env`

### Share each sheet with your service account email!

---

## Step 4: OpenAI API Key

### How to get your OpenAI API key:
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Click on your profile → **API keys**
4. Click **Create new secret key**
5. Name it (e.g., "X-piggybacking")
6. Copy the key immediately (you won't see it again!)
7. Paste it in `.env` as `OPENAI_API_KEY`

**Cost:** OpenAI charges per token usage. Start with a small budget and monitor usage.

---

## Step 5: X (Twitter) API Credentials

### When do you need this?
- Only required if you want to **actually post replies** to X
- Not needed for scraping (Apify handles that)
- Keep `ENABLE_X_POSTING=false` for testing without posting

### How to get X API credentials:

1. **Apply for X Developer Account**
   - Go to https://developer.twitter.com/
   - Click **Sign up** or **Apply**
   - Fill out the application form
   - Explain your use case (automation for engagement)
   - Wait for approval (can take a few days)

2. **Create a Project and App**
   - Go to https://developer.twitter.com/en/portal/dashboard
   - Click **Create Project**
   - Name your project
   - Create an App within the project

3. **Get OAuth 1.0a Credentials** (Recommended)
   - In your App settings, go to **Keys and tokens**
   - You'll see:
     - **API Key** → `X_API_KEY`
     - **API Secret** → `X_API_SECRET`
   - Under **Authentication Tokens**:
     - Click **Generate** for Access Token and Secret
     - **Access Token** → `X_ACCESS_TOKEN`
     - **Access Token Secret** → `X_ACCESS_TOKEN_SECRET`

4. **Set Permissions**
   - In App settings, go to **User authentication settings**
   - Click **Set up**
   - Enable **OAuth 1.0a**
   - Set permissions to **Read and Write** (needed for posting)
   - Save changes

5. **Alternative: OAuth 2.0 Bearer Token**
   - If you prefer OAuth 2.0, get a Bearer token with `tweet.write` scope
   - Set `X_BEARER_TOKEN` in `.env`

**Cost:** X API has different tiers. Basic tier may be free but with limitations. Check current pricing.

---

## Step 6: Verify Your Setup

### Check your `.env` file:
```bash
# Make sure all these are filled in (except X credentials if not posting):
✓ APIFY_TOKEN
✓ GOOGLE_SERVICE_ACCOUNT_PATH
✓ GOOGLE_X_ACCOUNT_ID
✓ OPENAI_API_KEY
✓ ENABLE_X_POSTING=false (for testing)
```

### Test the setup (dry run):
```bash
cd /Users/weilinchen/Documents/X_pickybacking/X-piggybacking
python3 main.py
```

**Note:** The script may fail due to unimplemented stub functions, but you should see it attempt to load credentials.

---

## Security Best Practices

1. **Never commit `.env` to git**
   - Already in `.gitignore`, but double-check

2. **Restrict JSON key permissions**
   - Keep the service account JSON file secure
   - Don't share it publicly
   - Use read-only access where possible

3. **Monitor API usage**
   - Set up billing alerts for Apify, OpenAI
   - Monitor X API rate limits

4. **Test with `ENABLE_X_POSTING=false`**
   - Always test in dry-run mode first
   - Only enable posting when you're confident

---

## Troubleshooting

### "Service account file not found"
- Check that `GOOGLE_SERVICE_ACCOUNT_PATH` points to the correct file
- Use absolute path, not relative

### "Spreadsheet not found"
- Verify the Sheet ID is correct
- Make sure you shared the sheet with the service account email

### "Apify request failed"
- Check that your Apify token is valid
- Verify you have credits/quota remaining

### "X API request failed"
- Check that all 4 OAuth 1.0a credentials are set
- Verify your app has Read and Write permissions
- Check X API rate limits

---

## Next Steps

Once your `.env` is configured:
1. Test each component individually
2. Implement the missing stub functions
3. Run the full pipeline in dry-run mode
4. Enable posting when ready

For questions or issues, refer to:
- `README.md` for project overview
- `docs/architecture.md` for system architecture
- `todo.md` for implementation status
