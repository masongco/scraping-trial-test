import json
import logging
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://scraping-trial-test.vercel.app"
SEARCH_TERM = "Silver Tech"
OUTPUT_FILE = "output.json"

logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def init_driver():
    driver = webdriver.Safari()
    return driver

def parse_business_table(html):
    soup = BeautifulSoup(html, "html.parser")
    records = []
    rows = soup.select("table.table tbody tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue
        link_tag = cols[0].find("a")
        detail_url = BASE_URL + link_tag["href"] if link_tag else None
        record = {
            "business_name": cols[0].get_text(strip=True),
            "registration_id": cols[1].get_text(strip=True),
            "status": cols[2].get_text(strip=True),
            "filing_date": cols[3].get_text(strip=True),
            "detail_url": detail_url
        }
        records.append(record)
    return records

def fetch_business_detail(driver, url):
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".agent-name"))
    )
    soup = BeautifulSoup(driver.page_source, "html.parser")
    agent_name = soup.select_one(".agent-name")
    agent_address = soup.select_one(".agent-address")
    agent_email = soup.select_one(".agent-email")
    return {
        "agent_name": agent_name.get_text(strip=True) if agent_name else None,
        "agent_address": agent_address.get_text(strip=True) if agent_address else None,
        "agent_email": agent_email.get_text(strip=True) if agent_email else None
    }

def save_output(records, filename=OUTPUT_FILE):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    logging.info(f"Saved {len(records)} records to {filename}")

def main():
    driver = init_driver()
    try:
        driver.get(BASE_URL)
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "input"))
        )
        search_input.clear()
        search_input.send_keys(SEARCH_TERM)
        search_input.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table tbody tr"))
        )

        records = parse_business_table(driver.page_source)

        for record in records:
            if record.get("detail_url"):
                agent_info = fetch_business_detail(driver, record["detail_url"])
                record.update(agent_info)
                del record["detail_url"]

        save_output(records)
        logging.info("Scraping completed successfully")

    except Exception as e:
        logging.error(f"Scraper error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()