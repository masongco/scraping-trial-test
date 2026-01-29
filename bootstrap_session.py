"""
bootstrap a valid x-search-session by opening the site in a real browser (playwright).
the api rejects direct requests unless this session header matches what the ui generates.

this script:
- opens the homepage
- waits for the first /api/search call (triggered after you type a query)
- grabs x-search-session from the outgoing request headers
- caches it locally so you don't have to do the recaptcha every run
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright, TimeoutError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

base_dir = Path(__file__).resolve().parent
session_cache_file = base_dir / "session_cache.json"


def load_cached_session() -> Optional[str]:
    """load a previously saved session id from disk (if present)."""
    if not session_cache_file.exists():
        return None

    try:
        with open(session_cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        session_id = data.get("session_id")
        timestamp = data.get("timestamp")

        if session_id:
            logging.info("using cached session from %s", timestamp)
            return session_id

    except Exception as e:
        logging.debug("could not load cached session: %s", e)

    return None


def save_session(session_id: str) -> None:
    """persist the session id to disk so we can reuse it on the next run."""
    try:
        payload = {
            "session_id": session_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        with open(session_cache_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        logging.info("cached session to %s", session_cache_file)
    except Exception as e:
        logging.warning("could not cache session: %s", e)


def get_search_session() -> Optional[str]:
    """
    returns a valid x-search-session for the api.

    the site uses recaptcha, so we launch a visible browser and wait for the ui
    to make the /api/search request. we then read the header from that request.
    """
    cached = load_cached_session()
    if cached:
        return cached

    with sync_playwright() as p:
        logging.info("launching browser to capture session (type a query in the page)")

        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        try:
            logging.info("opening site and waiting for manual search")
            page.goto("https://scraping-trial-test.vercel.app", wait_until="domcontentloaded", timeout=120000)

            print("\naction required:")
            print("1) type any search term in the browser")
            print("2) complete recaptcha if prompted")
            print("3) wait for results to load\n")

            # attach listeners for requests and responses, and poll browser
            # storage/cookies for any session-like values. Some sites store
            # the token in response headers, cookies, or local/sessionStorage.
            requests_seen = []
            responses_seen = []

            def _on_request(req):
                try:
                    if "/api/search" in req.url:
                        try:
                            hdrs = req.headers
                        except Exception:
                            hdrs = {}
                        requests_seen.append((req, hdrs))
                except Exception:
                    pass

            def _on_response(resp):
                try:
                    if "/api/search" in resp.url:
                        try:
                            hdrs = resp.headers
                        except Exception:
                            hdrs = {}
                        responses_seen.append((resp, hdrs))
                except Exception:
                    pass

            page.on("request", _on_request)
            page.on("response", _on_response)

            timeout_seconds = 240
            end_time = time.time() + timeout_seconds

            while time.time() < end_time:
                # examine buffered requests for the session header
                while requests_seen:
                    req, hdrs = requests_seen.pop(0)
                    session_value = hdrs.get("x-search-session")
                    logging.info("observed /api/search request: %s (has session=%s)", req.url, bool(session_value))
                    if session_value:
                        logging.info("captured x-search-session from request: %s", session_value)
                        try:
                            save_session(session_value)
                        except Exception:
                            logging.debug("failed to save session cache")
                        return session_value

                # examine responses for header that might contain session token
                while responses_seen:
                    resp, hdrs = responses_seen.pop(0)
                    session_value = hdrs.get("x-search-session") or hdrs.get("x-search-token")
                    logging.info("observed /api/search response: %s (has session=%s)", resp.url, bool(session_value))
                    if session_value:
                        logging.info("captured x-search-session from response: %s", session_value)
                        try:
                            save_session(session_value)
                        except Exception:
                            logging.debug("failed to save session cache")
                        return session_value

                # check cookies and storage for potential session values
                try:
                    cookies = context.cookies()
                    for c in cookies:
                        name = c.get("name", "")
                        value = c.get("value", "")
                        if "session" in name.lower() or "search" in name.lower() or "x-search" in name.lower():
                            logging.info("found cookie possibly containing session: %s", name)
                            save_session(value)
                            return value
                except Exception:
                    pass

                try:
                    # inspect localStorage/sessionStorage for keys containing 'session' or 'search'
                    ls = page.evaluate("() => JSON.stringify(localStorage)") or "{}"
                    ss = page.evaluate("() => JSON.stringify(sessionStorage)") or "{}"
                    for store_name, store_str in (("localStorage", ls), ("sessionStorage", ss)):
                        try:
                            mapping = json.loads(store_str)
                        except Exception:
                            mapping = {}
                        for k, v in mapping.items():
                            if "session" in k.lower() or "search" in k.lower() or "x-search" in k.lower():
                                logging.info("found %s key possibly containing session: %s", store_name, k)
                                save_session(v)
                                return v
                except Exception:
                    pass

                logging.info("waiting for /api/search activity... (%ds remaining)", int(end_time - time.time()))
                time.sleep(1)

            logging.warning("did not capture x-search-session within %s seconds", timeout_seconds)
            return None

        except Exception as e:
            logging.warning("session capture failed: %s", e)
            return None

        finally:
            try:
                browser.close()
            except Exception:
                pass


if __name__ == "__main__":
    session = get_search_session()
    if session:
        print(f"\nsession ok: {session}\n")
    else:
        print("\nfailed to capture session. make sure recaptcha was completed and results loaded.\n")
        sys.exit(1)