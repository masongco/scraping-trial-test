import requests
import logging
from bootstrap_session import get_search_session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

BASE_URL = "https://scraping-trial-test.vercel.app"
API_URL = f"{BASE_URL}/api/search"

def fetch_page(query: str):
    session_id = get_search_session(query)
    if not session_id:
        raise RuntimeError("Failed to obtain search session")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/26.1 Safari/605.1.15"
        ),
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Referer": f"{BASE_URL}/search/results?q={query}",
        "Origin": BASE_URL,
        "x-search-session": session_id,
    }

    logging.info("Using validated x-search-session=%s", session_id)

    resp = requests.get(
        API_URL,
        headers=headers,
        params={"q": query, "page": 1},
        timeout=15,
    )

    resp.raise_for_status()
    return resp.json()

def main():
    data = fetch_page("Tech")
    results = data.get("results", [])
    logging.info("Fetched %d records", len(results))

if __name__ == "__main__":
    main()