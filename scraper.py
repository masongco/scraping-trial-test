import requests
import json
import logging

logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

API_URL = "https://scraping-trial-test.vercel.app/api/search"

def fetch_api(q="Tech", page=2):
    params = {
        "q": q,
        "page": page,
        }
    try:
        response = requests.get("https://scraping-trial-test.vercel.app/search/results", params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"API request failed for query='{q}' page={page}: {e}")
        return None

def parse_record(record):
    agent = record.get("agent", {})
    return {
        "business_name": record.get("businessName"),
        "registration_id": record.get("registrationId"),
        "status": record.get("status"),
        "filing_date": record.get("filingDate"),
        "agent_name": agent.get("name"),
        "agent_address": agent.get("address"),
        "agent_email": agent.get("email")
    }

def save_output(records, filename="output.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    logging.info(f"Saved {len(records)} records to {filename}")

def main():
    page = 1
    all_records = []

    while True:
        logging.info(f"Fetching page {page}")
        data = fetch_api(q="Tech", page=page)
        if not data or "results" not in data:
            logging.error(f"No data returned for page {page}")
            break

        records = [parse_record(r) for r in data["results"]]
        all_records.extend(records)

        if page >= data.get("totalPages", 0):
            break
        page += 1

    if all_records:
        save_output(all_records)
    else:
        logging.warning("No records scraped")

if __name__ == "__main__":
    main()