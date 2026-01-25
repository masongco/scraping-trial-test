import requests
from bs4 import BeautifulSoup
import logging
import json

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

def save_output(records, filename="output.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    logging.info(f"Saved {len(records)} records to {filename}")

def main():
    html = fetch_page(BASE_URL)
    records = parse_page(html) if html else []

    if not records:
        logging.warning("No records found with requests + BS4, trying Selenium...")
        html = fetch_dynamic_page(BASE_URL)
        records = parse_page(html) if html else []

    if not records:
        logging.error("No records could be extracted even with Selenium.")
        return
    
    save_output(records)

if __name__ == "__main__":
    main()