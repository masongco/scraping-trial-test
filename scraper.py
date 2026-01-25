import requests
from bs4 import BeautifulSoup
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time


BASE_URL = "https://scraping-trial-test.vercel.app"


def fetch_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
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
            "business_name": get_text(card, ".businessName"),
            "registration_id": get_text(card, ".entityNumber"),
            "status": get_text(card, ".status"),
            "filing_date": get_text(card, ".filingDate"),
            "agent_name": get_text(card, ".agentName"),
            "agent_address": get_text(card, ".agentAddress"),
            "agent_email": get_text(card, ".agentEmail"),
        }

        records.append(record)

    return records

def fetch_dynamic_page(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        logging.info(f"Opening page with Selenium: {url}")
        driver.get(url)
        time.sleep(3)
        return driver.page_source
    finally:
        driver.quit()

def main():
    html = fetch_page(BASE_URL)

    if html is None:
        logging.error("Failed to retrieve page.")
        return

    records = parse_page(html)

    if records:
        logging.info("First record extracted:")
        logging.info(records[0])
        logging.info(f"\nTotal records extracted: {len(records)}")
    else:
        logging.error("No records found.")


if __name__ == "__main__":
    main()