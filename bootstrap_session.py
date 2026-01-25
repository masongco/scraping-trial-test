from playwright.sync_api import sync_playwright

def get_search_session(query="Tech"):
    with sync_playwright() as p:
        browser = p.webkit.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        session_value = None

        def handle_request(request):
            nonlocal session_value
            if "/api/search" in request.url:
                session_value = request.headers.get("x-search-session")

        page.on("request", handle_request)

        page.goto(f"https://scraping-trial-test.vercel.app/search/results?q={query}")
        page.wait_for_timeout(3000)

        browser.close()
        return session_value

if __name__ == "__main__":
    print(get_search_session())