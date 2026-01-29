# Web Scraping Trial Test

A Python-based web scraper that extracts business registration data from a search API using Playwright for session management and reCAPTCHA handling.

## Features

- **Dynamic Search**: Search for any query term
- **Multi-page Pagination**: Automatically fetches all results across pages
- **reCAPTCHA Handling**: Browser-based manual completion
- **Session Management**: Caches sessions for efficient reuse
- **Structured Output**: JSON format with one record per line

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
python -m playwright install
```

### 2. Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venvScriptsactivate  # On Windows
```

## Usage

### Basic Search

```bash
python scraper.py
```


## How It Works

1. **Session Capture**: Uses Playwright to navigate to the search page and complete reCAPTCHA
2. **API Requests**: Makes authenticated requests with the captured session token
3. **Pagination**: Automatically fetches all pages until all results are retrieved
4. **Data Transformation**: Converts API responses to a clean output format
5. **File Export**: Saves results to `output.json` (one record per line)

## Output

Results are saved to `output.json` in the following format:

```json
{
  "business_name": "Silver Tech CORP",
  "registration_id": "SD0000001",
  "status": "Active",
  "filing_date": "1999-12-04",
  "agent_name": "Sara Smith",
  "agent_address": "1545 Maple Ave",
  "agent_email": "sara.smith@example.com"
}
```

## Logging

All activity is logged to `scraper.log` with timestamps and log levels.

## Troubleshooting

If the scraper fails:

1. **Browser window doesn't open**:
   - Ensure Playwright browsers are installed: `python -m playwright install`

2. **reCAPTCHA errors**:
   - Complete the reCAPTCHA manually when the browser opens
   - Wait for results to load before the script continues

3. **Session errors**:
   - Delete `session_cache.json` to force a fresh session capture
   - Run the scraper again

## Files

- `scraper.py` - Main scraper script
- `bootstrap_session.py` - Session capture with Playwright
- `requirements.txt` - Python dependencies
- `output.json` - Results file (generated)
- `scraper.log` - Activity logs (generated)
- `session_cache.json` - Cached session (generated, can be deleted)