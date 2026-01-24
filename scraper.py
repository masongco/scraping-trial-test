import requests

def fetch_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.txt
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    url = "https://scraping-trial-test.vercel.app"
    html = fetch_page(url)
    print(len(html))


if __name__ == "__main__":
    main()