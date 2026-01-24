import requests
from bs4 import BeautifulSoup
import logging

BASE_URL = "https://scraping-trial-test.vercel.app"

def fetch_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging(f"Error fetching {url}: {e}")
        return None

def get_text(parent, selector):
    element = parent.select_one(selector)
    return element.get_text(strip=True) if element else None

def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    records = []

    business_cards = soup.select(".card")

    for card in business_cards:
        record = {
            "business_name": get_text(card, ".business-name"),
            "registration_id": get_text(card, ".entity-number"),
            "status": get_text(card, ".status"),
            "filing_date": get_text(card, ".filing-date"),
            "agent_name": get_text(card, ".agent-name"),
            "agent_address": get_text(card, ".agent-address"),
            "agent_email": get_text(card, ".agent-email"),
        }

        records.append(record)

    return records

def main():
    html = fetch_page(BASE_URL)

    if html is None:
        logging("Failed to retrieve page.")
        return

    records = parse_page(html)

    if records:
        logging("First record extracted:")
        logging(records[0])
        logging(f"\nTotal records extracted: {len(records)}")
    else:
        logging("No records found.")


if __name__ == "__main__":
    main()