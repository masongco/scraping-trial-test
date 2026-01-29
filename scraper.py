import json
import logging
import sys
from typing import Any, Dict, List, Optional

import requests

from bootstrap_session import get_search_session


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("scraper.log")],
)

BASE_URL = "https://scraping-trial-test.vercel.app"
API_URL = f"{BASE_URL}/api/search"


def build_headers(query: str, session_id: str) -> Dict[str, str]:
    """
    the api is picky about headers and expects a browser-like request.
    this mirrors what the ui sends (safari-ish in this case).
    """
    return {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/26.1 Safari/605.1.15"
        ),
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Referer": f"{BASE_URL}/search/results?q={query}",
        "Origin": BASE_URL,
        "x-search-session": session_id,
    }


def fetch_page(query: str, session_id: str, page: int = 1) -> Dict[str, Any]:
    """
    fetch a single api page for the given query.
    the session id is short-lived and comes from the ui bootstrap flow.
    """
    headers = build_headers(query, session_id)

    logging.info("fetching page %s for query='%s'", page, query)

    resp = requests.get(
        API_URL,
        headers=headers,
        params={"q": query, "page": page},
        timeout=15,
    )

    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        snippet = (resp.text or "")[:250].replace("\n", " ")
        logging.error("http error on page %s: %s", page, e)
        logging.error("response snippet: %s", snippet)
        raise

    try:
        data = resp.json()
    except ValueError as e:
        snippet = (resp.text or "")[:250].replace("\n", " ")
        logging.error("failed to parse json on page %s: %s", page, e)
        logging.error("response snippet: %s", snippet)
        raise

    results = data.get("results", [])
    logging.info("fetched %d rows from page %s", len(results), page)
    return data


def fetch_all_results(query: str) -> List[Dict[str, Any]]:
    """
    fetch all pages for a query until the api-reported total is reached.

    notes:
    - the site requires an x-search-session derived from the ui flow
    - if session capture fails, the scraper cannot continue
    """
    logging.info("bootstrapping session via browser flow...")
    session_id = get_search_session()

    if not session_id:
        logging.error("could not obtain x-search-session from ui flow")
        logging.error("complete the recaptcha (if shown), run a search, and wait for results")
        raise RuntimeError("failed to obtain search session")

    logging.info("session acquired: %s...", session_id[:20])

    all_results: List[Dict[str, Any]] = []
    page = 1

    while True:
        data = fetch_page(query, session_id, page=page)
        results = data.get("results", [])

        if not results:
            logging.info("no results returned on page %s; stopping", page)
            break

        all_results.extend(results)

        total = int(data.get("total", 0) or 0)
        logging.info("total collected so far: %d / %d", len(all_results), total)

        if total and len(all_results) >= total:
            logging.info("reached api total (%d); done", total)
            break

        page += 1

    return all_results


def transform_result(result: Dict[str, Any]) -> Dict[str, str]:
    """
    map the api payload to the exact output fields required by the test.
    empty strings are used to keep the schema consistent.
    """
    agent = result.get("agent", {}) or {}

    return {
        "business_name": result.get("businessName", "") or "",
        "registration_id": result.get("registrationId", "") or "",
        "status": result.get("status", "") or "",
        "filing_date": result.get("filingDate", "") or "",
        "agent_name": agent.get("name", "") or "",
        "agent_address": agent.get("address", "") or "",
        "agent_email": agent.get("email", "") or "",
    }


def save_to_file(records: List[Dict[str, str]], filename: str = "output.json") -> None:
    """
    save results as a proper json array (expected when output.json is requested).
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    logging.info("saved %d records to %s", len(records), filename)


def main(query: Optional[str] = None) -> None:
    try:
        if query is None:
            query = "Silver Tech"

        logging.info("starting scraper with query='%s'", query)

        raw_results = fetch_all_results(query)
        logging.info("fetched %d raw records total", len(raw_results))

        transformed = [transform_result(r) for r in raw_results]
        save_to_file(transformed, filename="output.json")

        if transformed:
            logging.info("sample output:")
            for i, record in enumerate(transformed[:3], start=1):
                logging.info(
                    "%d) %s | %s | %s | agent=%s",
                    i,
                    record["business_name"],
                    record["registration_id"],
                    record["status"],
                    record["agent_name"],
                )
        else:
            logging.warning("no records scraped")

    except Exception as e:
        logging.error("scraper failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    query_arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(query_arg)