import requests
import logging
import json
import uuid

BASE_API_URL = "https://scraping-trial-test.vercel.app/api/search"
SEARCH_QUERY = "Tech"
OUTPUT_FILE = "output.json"

logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def fetch_page(query, page):
    search_session = str(uuid.uuid4())

    # copied the headers for testing.
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"https://scraping-trial-test.vercel.app/search/results?q={query}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.1 Safari/605.1.15",
        "x-search-session": search_session
    }

    params = {
        "q": query,
        "page": page
    }

    try:
        logging.info(f"Fetching page {page} for query='{query}'")
        response = requests.get(
            BASE_API_URL,
            headers=headers,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"API request failed: {e}")
        return None

def parse_results(data):
    records = []

    if not data or "results" not in data:
        logging.error("Invalid or empty API response")
        return records

    for item in data["results"]:
        record = {
            "business_name": item.get("businessName"),
            "registration_id": item.get("registrationId"),
            "status": item.get("status"),
            "filing_date": item.get("filingDate"),
            "agent_name": item.get("agent", {}).get("name"),
            "agent_address": item.get("agent", {}).get("address"),
            "agent_email": item.get("agent", {}).get("email")
        }
        records.append(record)

    return records

def save_output(records):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    logging.info(f"Saved {len(records)} records to {OUTPUT_FILE}")

def main():
    data = fetch_page(SEARCH_QUERY, page=1)

    if not data:
        logging.warning("No data fetched")
        return

    records = parse_results(data)

    if not records:
        logging.warning("No records parsed")
        return

    save_output(records)

if __name__ == "__main__":
    main()