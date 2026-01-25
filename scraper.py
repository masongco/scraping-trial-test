import requests
import logging
import uuid

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

BASE_URL = "https://scraping-trial-test.vercel.app"
API_URL = f"{BASE_URL}/api/search"

def build_headers(query: str) -> dict:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/26.1 Safari/605.1.15"
        ),
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",

        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",

        "Referer": f"{BASE_URL}/search/results?q={query}",
        "Origin": BASE_URL,

        "x-search-session": str(uuid.uuid4()),
    }

def fetch_page(query: str):
    headers = build_headers(query)

    logging.info("Fetching page 1 for query='%s'", query)
    logging.info("Using x-search-session=%s", headers["x-search-session"])

    resp = requests.get(
        API_URL,
        headers=headers,
        params={"q": query, "page": 1},
        timeout=15,
    )

    resp.raise_for_status()
    return resp.json()

def main():
    try:
        data = fetch_page("Tech")
        results = data.get("results", [])
        logging.info("Fetched %d records", len(results))
        return results

    except requests.HTTPError as e:
        logging.error("API request failed: %s", e)
    except Exception:
        logging.exception("Unexpected error")

if __name__ == "__main__":
    main()