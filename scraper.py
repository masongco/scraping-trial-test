import requests
from bs4 import BeautifulSoup

BASE_URL = "https://scraping-trial-test.vercel.app"

def fetch_page(url):
    response = requests.get(url)
    return response.text

def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    names = []

    for card in soup.select(".business-card"):
        name_el = card.select_one(".business-name")
        if name_el:
            names.append(name_el.get_text(strip=True))

    return names

def main():
    html = fetch_page(BASE_URL)
    names = parse_page(html)
    print(names[:5])


if __name__ == "__main__":
    main()